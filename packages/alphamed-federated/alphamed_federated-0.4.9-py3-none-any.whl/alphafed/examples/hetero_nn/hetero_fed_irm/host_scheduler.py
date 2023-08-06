"""Hetero FedIRM scheduler demo."""

import os
from hashlib import md5
from time import time
from typing import Dict, List, Set, Tuple

import pandas as pd
import torch
import torch.nn.functional as F
from PIL import Image
from res_net import ResNet18
from torch import Tensor, nn
from torch.optim import SGD, Adam, Optimizer
from torch.utils.data import DataLoader, Dataset, Subset
from torchvision import transforms

from alphafed import logger
from alphafed.hetero_nn import HeteroNNHostScheduler


class _CheXpertDataset(Dataset):

    def __init__(self, data_dir, csv_file, transform=None):
        """.

        Args:
            data_dir: path to image directory.
            csv_file: path to the file containing images
                with corresponding labels.
            transform: optional transform to be applied on a sample.
        """
        super(_CheXpertDataset, self).__init__()
        file = os.path.join(data_dir, csv_file)
        data = pd.read_csv(file)

        self.data_dir = data_dir
        self.images = data['ImageID'].values
        self.labels = data.iloc[:, 1:].values.astype(int)
        self.index = {self.images[idx]: idx for idx in range(len(self.images))}
        self.transform = transform

    def __getitem__(self, image_name):
        """.

        Args:
            index: name of the image, for example
        Returns:
            image and its labels
        """
        image_file = os.path.join(self.data_dir, image_name) + '.jpg'
        image = Image.open(image_file).convert('RGB')
        index = self.index[image_name]
        label = self.labels[index]
        if self.transform is not None:
            image = self.transform(image)
        return image, torch.FloatTensor(label)

    def __len__(self):
        return len(self.images)


class _LabelSmoothingCrossEntropy(object):
    def __init__(self, epsilon: float = 0.1, reduction: str = 'mean'):
        self.epsilon = epsilon
        self.reduction = reduction

        class_num = [1101, 6704, 527, 323, 1083, 120, 135]
        class_weight = torch.Tensor([9993/i for i in class_num])
        if torch.cuda.is_available():
            class_weight = class_weight.cuda()
        self.base_loss = torch.nn.CrossEntropyLoss(reduction='mean', weight=class_weight)

    def _reduce_loss(self, loss: Tensor, reduction: str = 'mean'):
        if reduction == 'mean':
            return loss.mean()
        elif reduction == 'sum':
            return loss.sum()
        else:
            return loss

    def _linear_combination(self, x, y, epsilon):
        return epsilon * x + (1 - epsilon) * y

    def __call__(self, preds, target) -> Tensor:
        target = torch.argmax(target, dim=1)
        n = preds.size()[-1]
        log_preds = F.log_softmax(preds, dim=-1)
        loss = self._reduce_loss(-log_preds.sum(dim=-1), self.reduction)
        nll = F.nll_loss(log_preds, target.long(), reduction=self.reduction)
        return self._linear_combination(loss / n, nll, self.epsilon)


class HostConvNet(ResNet18):
    def __init__(self) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=5)
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=5)
        self.conv3 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=5)
        self.conv3_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(in_features=128 * 24 * 24, out_features=512)
        self.fc2 = nn.Linear(in_features=512, out_features=25)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2(x), 2))
        x = F.relu(F.max_pool2d(self.conv3_drop(self.conv3(x)), 2))
        x = x.view(-1, 128 * 24 * 24)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return x


class InferModule(nn.Module):

    def __init__(self) -> None:
        super().__init__()
        self.fc1 = nn.Linear(50, 20)
        self.fc2 = nn.Linear(20, 7)

    def forward(self, input):
        out = F.relu(self.fc1(input))
        out = self.fc2(out)
        return out


class IRMHostScheduler(HeteroNNHostScheduler):

    def __init__(self,
                 feature_key: str,
                 batch_size: int,
                 data_dir: str,
                 csv_file: str,
                 param_file: str,
                 max_rounds: int = 0,
                 calculation_timeout: int = 300,
                 schedule_timeout: int = 30,
                 log_rounds: int = 0) -> None:
        self.data_dir = data_dir
        self.csv_file = csv_file
        self.param_file = param_file
        super().__init__(feature_key=feature_key,
                         max_rounds=max_rounds,
                         calculation_timeout=calculation_timeout,
                         schedule_timeout=schedule_timeout,
                         log_rounds=log_rounds)
        self.batch_size = batch_size

        self.is_cuda = torch.cuda.is_available()
        # if self.is_cuda:
        #     torch.backends.cudnn.benchmark = True

    @property
    def dataset(self) -> _CheXpertDataset:
        if not hasattr(self, '_dataset'):
            self._dataset = _CheXpertDataset(
                data_dir=self.data_dir,
                csv_file=self.csv_file,
                transform=transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.RandomAffine(degrees=10, translate=(0.02, 0.02)),
                    transforms.RandomHorizontalFlip(),
                    transforms.ToTensor(),
                    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
                ])
            )
        return self._dataset

    def load_local_ids(self) -> List[str]:
        return list(self.dataset.images)

    def split_dataset(self, id_intersection: Set[str]) -> Tuple[Set[str], Set[str]]:
        ids = list(id_intersection)
        # 模拟随机拆分训练集和测试集
        ids.sort(key=lambda x: md5(bytes(x.encode())).digest())
        train_num = round(len(ids) * 0.8)
        train_ids = ids[:train_num]
        test_ids = ids[train_num:]

        logger.info(f'Got {len(train_ids)} intersecting samples for training.')
        logger.info(f'Got {len(test_ids)} intersecting samples for testing.')

        return set(train_ids), set(test_ids)

    def build_feature_model(self) -> nn.Module:
        model = ResNet18(num_classes=7)
        param_file = os.path.join(self.data_dir, self.param_file)
        with open(param_file, 'rb') as f:
            state_dict = torch.load(f)
            model.load_state_dict(state_dict, strict=False)
        # 替换分类层
        model.fc = nn.Linear(model.layer1[0].expansion * 512, 25)
        return model.cuda() if torch.cuda.is_available() else model

    def build_feature_optimizer(self, feature_model: nn.Module) -> Optimizer:
        return Adam(feature_model.parameters(),
                    lr=1e-4,
                    betas=(0.9, 0.999),
                    weight_decay=5e-4)

    def iterate_train_feature(self,
                              feature_model: nn.Module,
                              train_ids: Set[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        train_ids: list = list(train_ids)
        # 模拟每一轮训练的随机排序效果
        train_ids.sort(key=lambda x: md5(bytes((x + str(self.current_round)).encode())).digest())

        self.train_dataset = Subset(self.dataset, train_ids)
        train_loader = DataLoader(self.train_dataset,
                                  batch_size=self.batch_size,
                                  shuffle=False)

        for image_batch, label_batch in train_loader:
            if self.is_cuda:
                image_batch = image_batch.cuda()
                label_batch = label_batch.cuda()
            features = feature_model(image_batch)
            yield features.cpu(), label_batch.cpu()

    @torch.no_grad()
    def iterate_test_feature(self,
                             feature_model: nn.Module,
                             test_ids: Set[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        test_ids: list = list(test_ids)
        test_ids.sort()

        self.test_dataset = Subset(self.dataset, test_ids)
        test_loader = DataLoader(self.test_dataset,
                                 batch_size=self.batch_size,
                                 shuffle=False)

        for image_batch, label_batch in test_loader:
            if self.is_cuda:
                image_batch = image_batch.cuda()
                label_batch = label_batch.cuda()
            features = feature_model(image_batch)
            yield features.cpu(), label_batch.cpu()

    def build_infer_model(self) -> nn.Module:
        model = InferModule()
        return model.cuda() if torch.cuda.is_available() else model

    def build_infer_optimizer(self, infer_model: nn.Module) -> Optimizer:
        return SGD(infer_model.parameters(), lr=0.001, momentum=0.9)

    def train_a_batch(self, feature_projection: Dict[str, torch.Tensor], labels: torch.Tensor):
        # loss_fn = _LabelSmoothingCrossEntropy()
        fusion_tensor = torch.concat((feature_projection['demo_host'],
                                      feature_projection['demo_collaborator']), dim=1)
        if self.is_cuda:
            fusion_tensor = fusion_tensor.cuda()
            labels = labels.cuda()
        output = self.infer_model(fusion_tensor)
        output = F.log_softmax(output, dim=-1)
        target = torch.argmax(labels, dim=1)
        loss = F.nll_loss(output, target.long())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    @torch.no_grad()
    def run_test(self,
                 batched_feature_projections: List[torch.Tensor],
                 batched_labels: List[torch.Tensor]):
        # loss_fn = _LabelSmoothingCrossEntropy()
        correct = 0
        test_loss = 0.0
        start = time()
        for _feature_projection, _lables in zip(batched_feature_projections, batched_labels):
            fusion_tensor = torch.concat((_feature_projection['demo_host'],
                                          _feature_projection['demo_collaborator']), dim=1)
            if self.is_cuda:
                fusion_tensor = fusion_tensor.cuda()
                _lables = _lables.cuda()
            output = self.infer_model(fusion_tensor)
            output = F.log_softmax(output, dim=-1)
            target = torch.argmax(_lables, dim=1)
            test_loss += F.nll_loss(output, target.long())
            pred = output.max(1, keepdim=True)[1]
            _lables = _lables.max(1, keepdim=True)[1]
            correct += pred.eq(_lables.view_as(pred)).sum().item()

        test_loss /= len(self.test_dataset)
        accuracy = correct / len(self.test_dataset)
        correct_rate = 100. * accuracy
        logger.info(f'Test set: Average loss: {test_loss:.4f}')
        logger.info(
            f'Test set: Accuracy: {accuracy} ({correct_rate:.2f}%)'
        )

        end = time()

        self.tb_writer.add_scalar('timer/run_time', end - start, self.current_round)
        self.tb_writer.add_scalar('test_results/average_loss', test_loss, self.current_round)
        self.tb_writer.add_scalar('test_results/accuracy', accuracy, self.current_round)
        self.tb_writer.add_scalar('test_results/correct_rate', correct_rate, self.current_round)

    def validate_context(self):
        super().validate_context()
        assert self.dataset and len(self.dataset) > 0, '加载数据集失败'
