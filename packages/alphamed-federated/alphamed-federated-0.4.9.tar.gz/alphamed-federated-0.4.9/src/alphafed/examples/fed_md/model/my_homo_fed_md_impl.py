"""Homo FedPer 算法应用示例."""

import math
from time import time

import torch
import torch.nn.functional as F
from loss import loss_kd
from net import ConvNet
from scheduler import HomoFedMDScheduler
from torch import Tensor
from torch.nn import Module
from torch.optim import SGD, Optimizer
from torch.utils.data import DataLoader, Subset
from torchvision import transforms
from torchvision.datasets import MNIST

from alphafed import logger


class DemoHomoFedMDScheduler(HomoFedMDScheduler):

    def __init__(self,
                 max_rounds: int,
                 pretrain_public_epochs: int,
                 pretrain_private_epochs: int,
                 align_epochs: int,
                 fine_tune_epochs: int,
                 calculation_timeout: int = 300,
                 schedule_timeout: int = 30,
                 log_rounds: int = 0):
        super().__init__(max_rounds=max_rounds,
                         pretrain_public_epochs=pretrain_public_epochs,
                         pretrain_private_epochs=pretrain_private_epochs,
                         align_epochs=align_epochs,
                         fine_tune_epochs=fine_tune_epochs,
                         calculation_timeout=calculation_timeout,
                         schedule_timeout=schedule_timeout,
                         log_rounds=log_rounds)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.seed = 42
        torch.manual_seed(self.seed)
        self.batch_size = 128

    def build_model(self) -> Module:
        net = ConvNet()
        return net.to(self.device)

    def build_optimizer(self, model: Module) -> Optimizer:
        learning_rate = 0.01
        momentum = 0.9
        return SGD(model.parameters(), lr=learning_rate, momentum=momentum)
    
    def build_public_train_dataloader(self) -> DataLoader:
        dataset = MNIST(
            '/data/MNIST/',
            train=True,
            download=True,
            transform=transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,))
            ])
        )
        return DataLoader(
            Subset(dataset=dataset, indices=list(range(50000))),
            batch_size=self.batch_size,
            shuffle=False
        )
    
    def build_private_train_dataloader(self) -> DataLoader:
        dataset = MNIST(
            '/data/MNIST/',
            train=True,
            download=True,
            transform=transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,))
            ])
        )
        return DataLoader(
            Subset(dataset=dataset, indices=list(range(50000, 60000))),
            batch_size=self.batch_size,
            shuffle=True
        )
    
    def build_test_dataloader(self) -> DataLoader:
        return DataLoader(
            MNIST(
                '/data/MNIST/',
                train=False,
                download=True,
                transform=transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize((0.1307,), (0.3081,))
                ])
            ),
            batch_size=self.batch_size,
            shuffle=False
        )

    @torch.no_grad()
    def calc_local_logits(self) -> Tensor:
        logits = []
        self.model.eval()
        for data, _ in self.public_train_loader:
            data: Tensor
            data = data.to(self.device)
            logits.append(self.model(data))
        return torch.cat(logits, dim=0)

    def pretrain_an_epoch_on_public_data(self):
        self.model.train()
        for data, labels in self.public_train_loader:
            data: Tensor
            labels: Tensor
            data, labels = data.to(self.device), labels.to(self.device)
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = F.nll_loss(output, labels)
            loss.backward()
            self.optimizer.step()

    def pretrain_an_epoch_on_private_data(self):
        self.model.train()
        for data, labels in self.private_train_loader:
            data: Tensor
            labels: Tensor
            data, labels = data.to(self.device), labels.to(self.device)
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = F.nll_loss(output, labels)
            loss.backward()
            self.optimizer.step()

    def align_train_an_epoch(self, global_logits: Tensor):
        self.model.train()
        
        # re-organize global_logits into batches
        chunks = math.ceil(len(global_logits) / self.batch_size)
        logits_batches = torch.chunk(input=global_logits, chunks=chunks, dim=0)
        
        for (data, labels), teacher_logits in zip(self.public_train_loader, logits_batches):
            data: Tensor
            labels: Tensor
            data, labels = data.to(self.device), labels.to(self.device)
            teacher_logits = teacher_logits.to(self.device)
            self.optimizer.zero_grad()
            output = self.model(data)            
            loss = loss_kd(output, labels, teacher_logits)
            loss.backward()
            self.optimizer.step()

    def fine_tune_an_epoch(self):
        self.pretrain_an_epoch_on_private_data()

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
