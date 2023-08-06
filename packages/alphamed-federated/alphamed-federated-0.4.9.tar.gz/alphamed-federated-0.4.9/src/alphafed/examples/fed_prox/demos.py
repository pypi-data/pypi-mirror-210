"""Process demo."""

import os
from time import time

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from torch import optim
from torch.utils.data import DataLoader

from ... import get_dataset_dir, logger
from .model.scheduler import FedProxScheduler
from .model.net import ConvNet
from . import DEV_TASK_ID

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class DemoFedProxScheduler(FedProxScheduler):

    def __init__(self,
                 max_rounds: int = 0,
                 merge_epochs: int = 1,
                 mu: float = 0.01,
                 batch_size: int = 64,
                 learning_rate: float = 0.01,
                 momentum: float = 0.5,
                 schedule_timeout: int = 30,
                 calculation_timeout: int = 300,
                 log_rounds: int = 0,
                 involve_aggregator: bool = False) -> None:
        super().__init__(max_rounds=max_rounds,
                         merge_epochs=merge_epochs,
                         mu=mu,
                         schedule_timeout=schedule_timeout,
                         calculation_timeout=calculation_timeout,
                         log_rounds=log_rounds,
                         involve_aggregator=involve_aggregator)
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.momentum = momentum

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.seed = 42
        torch.manual_seed(self.seed)

    def build_model(self) -> nn.Module:
        model = ConvNet()
        return model.to(self.device)

    def build_optimizer(self, model: nn.Module) -> optim.Optimizer:
        return optim.SGD(model.parameters(),
                         lr=self.learning_rate,
                         momentum=self.momentum)

    def build_train_dataloader(self) -> DataLoader:
        return DataLoader(
            torchvision.datasets.MNIST(
                get_dataset_dir(self.task_id),
                train=True,
                download=True,
                transform=torchvision.transforms.Compose([
                    torchvision.transforms.ToTensor(),
                    torchvision.transforms.Normalize((0.1307,), (0.3081,))
                ])
            ),
            batch_size=self.batch_size,
            shuffle=True
        )

    def build_test_dataloader(self) -> DataLoader:
        return DataLoader(
            torchvision.datasets.MNIST(
                get_dataset_dir(self.task_id),
                train=False,
                download=True,
                transform=torchvision.transforms.Compose([
                    torchvision.transforms.ToTensor(),
                    torchvision.transforms.Normalize((0.1307,), (0.3081,))
                ])
            ),
            batch_size=self.batch_size,
            shuffle=False
        )

    def validate_context(self):
        super().validate_context()
        assert self.train_loader and len(self.train_loader) > 0, 'failed to load train data'
        logger.info(f'There are {len(self.train_loader.dataset)} samples for training.')
        assert self.test_loader and len(self.test_loader) > 0, 'failed to load test data'
        logger.info(f'There are {len(self.test_loader.dataset)} samples for testing.')

    def train_an_epoch(self) -> None:
        self.model.train()
        for data, labels in self.train_loader:
            data: torch.Tensor
            labels: torch.Tensor
            data, labels = data.to(self.device), labels.to(self.device)
            self.optimizer.zero_grad()
            output = self.model(data)
            # 这里必须使用 calc_prox_loss 计算损失
            loss = self.calc_prox_loss(F.nll_loss, output, labels)
            loss.backward()
            self.optimizer.step()

    def run_test(self):
        start = time()
        self.model.eval()
        test_loss = 0
        correct = 0
        with torch.no_grad():
            for data, labels in self.test_loader:
                data: torch.Tensor
                labels: torch.Tensor
                data, labels = data.to(self.device), labels.to(self.device)
                output: torch.Tensor = self.model(data)
                test_loss += F.nll_loss(output, labels, reduction='sum').item()
                pred = output.max(1, keepdim=True)[1]
                correct += pred.eq(labels.view_as(pred)).sum().item()

        test_loss /= len(self.test_loader.dataset)
        accuracy = correct / len(self.test_loader.dataset)
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


def get_task_id() -> str:
    return DEV_TASK_ID


def get_scheduler() -> FedProxScheduler:
    pickle_file = './scheduler.pickle'
    import cloudpickle as pickle

    if os.path.exists(pickle_file):
        os.remove(pickle_file)

    scheduler = DemoFedProxScheduler(max_rounds=3,
                                     merge_epochs=2,
                                     mu=0.01,
                                     batch_size=128,
                                     learning_rate=0.01,
                                     momentum=0.9)

    with open(pickle_file, 'w+b') as pf:
        pickle.dump(scheduler, pf)

    with open(pickle_file, 'rb') as f:
        scheduler = pickle.load(f)
        return scheduler
