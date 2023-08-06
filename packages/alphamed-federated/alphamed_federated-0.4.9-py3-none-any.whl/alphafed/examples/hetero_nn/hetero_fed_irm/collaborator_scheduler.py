"""Hetero FedIRM scheduler demo."""

import os
from hashlib import md5
from typing import List, Set, Tuple

import pandas as pd
import torch
import torch.backends.cudnn
import torch.nn.functional as F
from PIL import Image
from torch import nn
from torch.optim import Adam, Optimizer
from torch.utils.data import DataLoader, Dataset, Subset
from torchvision import transforms

from alphafed import logger
from alphafed.hetero_nn import HeteroNNCollaboratorScheduler


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


class CollaboratorConvNet(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3)
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3)
        self.conv3 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3)
        self.conv3_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(in_features=128 * 26 * 26, out_features=128)
        self.fc2 = nn.Linear(in_features=128, out_features=25)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2(x), 2))
        x = F.relu(F.max_pool2d(self.conv3_drop(self.conv3(x)), 2))
        x = x.view(-1, 128 * 26 * 26)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return x


class IRMCollaboratorScheduler(HeteroNNCollaboratorScheduler):

    def __init__(self,
                 feature_key: str,
                 batch_size: int,
                 data_dir: str,
                 csv_file: str,
                #  param_file: str,
                 schedule_timeout: int = 30,
                 is_feature_trainable: bool = True) -> None:
        self.data_dir = data_dir
        self.csv_file = csv_file
        # self.param_file = param_file
        super().__init__(feature_key=feature_key,
                         schedule_timeout=schedule_timeout,
                         is_feature_trainable=is_feature_trainable)
        self.batch_size = batch_size

        self.is_cuda = torch.cuda.is_available()
        if self.is_cuda:
            torch.backends.cudnn.benchmark = True

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
        model = CollaboratorConvNet()
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

        for image_batch, _ in train_loader:
            if self.is_cuda:
                image_batch = image_batch.cuda()
            features = feature_model(image_batch)
            yield features.cpu()

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

        for image_batch, _ in test_loader:
            if self.is_cuda:
                image_batch = image_batch.cuda()
            features = feature_model(image_batch)
            yield features.cpu()
