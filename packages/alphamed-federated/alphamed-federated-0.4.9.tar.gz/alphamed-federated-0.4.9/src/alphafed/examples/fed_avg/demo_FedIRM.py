import os

import numpy as np
import pandas as pd
import torch
# import torch.backends.cudnn as cudnn
import torch.nn.functional as F
from imblearn.metrics import sensitivity_score, specificity_score
from PIL import Image
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             roc_auc_score)
from torch import Tensor, nn
from torch.optim import Adam, Optimizer
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from ... import logger
from ...fed_avg import FedAvgScheduler
from .res_net import ResNet18

__all__ = ['DemoFedIRM']


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class _CheXpertDataset(Dataset):

    def __init__(self, root_dir, csv_file, transform=None):
        """.

        Args:
            data_dir: path to image directory.
            csv_file: path to the file containing images
                with corresponding labels.
            transform: optional transform to be applied on a sample.
        """
        super(_CheXpertDataset, self).__init__()
        file = pd.read_csv(csv_file)

        self.root_dir = root_dir
        self.images = file['ImageID'].values
        self.labels = file.iloc[:, 1:].values.astype(int)
        self.transform = transform

        logger.info('Total # images:{}, labels:{}'.format(
            len(self.images), len(self.labels)))

    def __getitem__(self, index):
        """.

        Args:
            index: the index of item
        Returns:
            image and its labels
        """
        items = self.images[index]
        image_name = os.path.join(self.root_dir, self.images[index]) + '.jpg'
        image = Image.open(image_name).convert('RGB')
        label = self.labels[index]
        if self.transform is not None:
            image = self.transform(image)
        return items, index, image, torch.FloatTensor(label)

    def __len__(self):
        return len(self.images)


class _TransformTwice:
    def __init__(self, transform):
        self.transform = transform

    def __call__(self, inp):
        out1 = self.transform(inp)
        out2 = self.transform(inp)
        return out1, out2


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


class DemoFedIRM(FedAvgScheduler):

    def __init__(self,
                 root_path: str,
                 csv_file_train: str,
                 csv_file_test: str,
                 max_rounds: int = 0,
                 merge_epochs: int = 1,
                 calculation_timeout: int = 300,
                 schedule_timeout: int = 30,
                 log_rounds: int = 0,
                 is_deterministic: bool = True,
                 seed: int = 1337,
                 label_uncertainty: str = 'U-Ones',
                 drop_rate: float = 0.2,
                 batch_size: int = 32,
                 base_lr: float = 1e-4,
                 involve_aggregator: bool = False):
        super().__init__(max_rounds=max_rounds,
                         merge_epochs=merge_epochs,
                         calculation_timeout=calculation_timeout,
                         schedule_timeout=schedule_timeout,
                         log_rounds=log_rounds,
                         involve_aggregator=involve_aggregator)
        self.is_deterministic = is_deterministic
        self.seed = seed
        self.label_uncertainty = label_uncertainty
        self.drop_rate = drop_rate
        self.root_path = root_path
        self.csv_file_train = csv_file_train
        self.csv_file_test = csv_file_test
        self.batch_size = batch_size
        self.base_lr = base_lr

        self.is_cuda = torch.cuda.is_available()
        # torch.backends.cudnn.enabled = self.is_cuda
        # if self.is_cuda and self.is_deterministic:
        #     cudnn.benchmark = False
        #     cudnn.deterministic = True
        #     torch.cuda.manual_seed(self.seed)

    def build_model(self) -> nn.Module:
        model = ResNet18(num_classes=7)
        model = model.cuda() if self.is_cuda else model
        return model

    def build_optimizer(self, model: nn.Module) -> Optimizer:
        return Adam(model.parameters(),
                    lr=self.base_lr,
                    betas=(0.9, 0.999),
                    weight_decay=5e-4)

    def build_train_dataloader(self) -> DataLoader:
        train_dataset = _CheXpertDataset(
            root_dir=self.root_path,
            csv_file=self.csv_file_train,
            transform=_TransformTwice(transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.RandomAffine(degrees=10, translate=(0.02, 0.02)),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]))
        )
        train_loader = DataLoader(dataset=train_dataset,
                                  batch_size=self.batch_size,
                                  shuffle=True)
        return train_loader

    def build_test_dataloader(self) -> DataLoader:
        test_dataset = _CheXpertDataset(
            root_dir=self.root_path,
            csv_file=self.csv_file_test,
            transform=transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ])
        )
        test_dataloader = DataLoader(dataset=test_dataset,
                                     batch_size=self.batch_size,
                                     shuffle=False)
        return test_dataloader

    def train_an_epoch(self):
        self.model.train()

        loss_fn = _LabelSmoothingCrossEntropy()

        for _, _, (image_batch, ema_image_batch), label_batch in self.train_loader:
            if self.is_cuda:
                image_batch = image_batch.cuda()
                ema_image_batch = ema_image_batch.cuda()
                label_batch = label_batch.cuda()
            outputs = self.model(image_batch)
            aug_outputs = self.model(ema_image_batch)
            loss = loss_fn(outputs, label_batch.long()) + loss_fn(aug_outputs, label_batch.long())
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

    def _compute_metrics_test(self, gt, pred, thresh):
        """Compute accuracy, precision, recall and F1-score from prediction scores.

        Args:
            gt:
                Pytorch tensor on GPU, shape = [n_samples, n_classes] true binary labels.
            pred:
                Pytorch tensor on GPU, shape = [n_samples, n_classes]
                can either be probability estimates of the positive class,
                confidence values, or binary decisions.
        Returns:
            List of AUROCs of all classes.
        """
        AUROCs, Accus, Senss, Specs, Pre, F1 = [], [], [], [], [], []
        gt_np = gt.cpu().detach().numpy()
        pred_np = pred.cpu().detach().numpy()

        class_names = [
            'Melanoma',
            'Melanocytic nevus',
            'Basal cell carcinoma',
            'Actinic keratosis',
            'Benign keratosis',
            'Dermatofibroma',
            'Vascular lesion'
        ]

        for i, cls in enumerate(class_names):
            try:
                AUROCs.append(roc_auc_score(gt_np[:, i], pred_np[:, i]))
            except ValueError as error:
                logger.info('Error in computing accuracy for {}.\n Error msg:{}'.format(i, error))
                AUROCs.append(0)

            try:
                Accus.append(accuracy_score(gt_np[:, i], (pred_np[:, i] >= thresh)))
            except ValueError as error:
                logger.info('Error in computing accuracy for {}.\n Error msg:{}'.format(i, error))
                Accus.append(0)

            try:
                Senss.append(sensitivity_score(gt_np[:, i], (pred_np[:, i] >= thresh)))
            except ValueError:
                logger.info('Error in computing precision for {}.'.format(i))
                Senss.append(0)

            try:
                Specs.append(specificity_score(gt_np[:, i], (pred_np[:, i] >= thresh)))
            except ValueError:
                logger.info('Error in computing F1-score for {}.'.format(i))
                Specs.append(0)

            try:
                Pre.append(precision_score(gt_np[:, i], (pred_np[:, i] >= thresh)))
            except ValueError:
                logger.info('Error in computing F1-score for {}.'.format(i))
                Pre.append(0)

            try:
                F1.append(f1_score(gt_np[:, i], (pred_np[:, i] >= thresh)))
            except ValueError:
                logger.info('Error in computing F1-score for {}.'.format(i))
                F1.append(0)

        return AUROCs, Accus, Senss, Specs, Pre, F1

    @torch.no_grad()
    def _epochVal_metrics_test(self, data_loader: DataLoader, thresh: float):
        training = self.model.training
        self.model.eval()

        gt = torch.FloatTensor()
        pred = torch.FloatTensor()
        if self.is_cuda:
            gt, pred = gt.cuda(), pred.cuda()

        gt_study = {}
        pred_study = {}
        studies = []

        for i, (study, _, image, label) in enumerate(data_loader):
            if self.is_cuda:
                image, label = image.cuda(), label.cuda()
            output = self.model(image)

            output = F.softmax(output, dim=1)

            for i in range(len(study)):
                if study[i] in pred_study:
                    assert torch.equal(gt_study[study[i]], label[i])
                    pred_study[study[i]] = torch.max(
                        pred_study[study[i]], output[i])
                else:
                    gt_study[study[i]] = label[i]
                    pred_study[study[i]] = output[i]
                    studies.append(study[i])

        for study in studies:
            gt = torch.cat((gt, gt_study[study].view(1, -1)), 0)
            pred = torch.cat((pred, pred_study[study].view(1, -1)), 0)

        AUROCs, Accus, Senss, Specs, pre, F1 = self._compute_metrics_test(
            gt, pred, thresh=thresh)

        self.model.train(training)

        return AUROCs, Accus, Senss, Specs, pre, F1

    def run_test(self):
        AUROCs, Accus, Senss, Specs, pre, F1 = self._epochVal_metrics_test(
            data_loader=self.test_loader, thresh=0.4
        )
        AUROC_avg = np.array(AUROCs).mean()
        Accus_avg = np.array(Accus).mean()
        Senss_avg = np.array(Senss).mean()
        Specs_avg = np.array(Specs).mean()

        class_list = ['MEL', 'NV', 'BCC', 'AKIEC', 'BKL', 'DF', 'VASC']
        result_str = ', '.join((f'AUROC: {AUROC_avg:6f}',
                                f'TEST Accus: {Accus_avg:6f}',
                                f'TEST Senss: {Senss_avg:6f}',
                                f'TEST Specs: {Specs_avg:6f}',
                                f'pre: {pre}',
                                f'F1: {F1}'))
        logger.info(f'Test after training: {result_str}')

        self.tb_writer.add_scalar('test_results/AUROC', AUROC_avg, self.current_round)
        self.tb_writer.add_scalar('test_results/Accus', Accus_avg, self.current_round)
        self.tb_writer.add_scalar('test_results/Senss', Senss_avg, self.current_round)
        self.tb_writer.add_scalar('test_results/Specs', Specs_avg, self.current_round)
        self.tb_writer.add_scalars('test_results/pre', dict(zip(class_list, pre)), self.current_round)
        self.tb_writer.add_scalars('test_results/F1', dict(zip(class_list, F1)), self.current_round)

    def validate_context(self):
        super().validate_context()
        assert self.train_loader and len(self.train_loader) > 0
        assert self.test_loader and len(self.test_loader) > 0
