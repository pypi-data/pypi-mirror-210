"""Define base AutoModel interfaces."""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, unique
from typing import Any, Dict, Optional, Tuple, Type
from zipfile import ZipFile

import torch
from torch import nn, optim
from torch.utils.data import DataLoader

from .. import logger, task_logger
from ..fed_avg import FedAvgScheduler
from ..fed_avg.contractor import AutoFedAvgContractor
from .exceptions import AutoModelError, ConfigError


@unique
class DataType(int, Enum):

    IMAGE = 1
    TEXT = 2
    AUDIO = 3
    VIDEO = 4


@unique
class TaskType(int, Enum):

    IMAGE_CLASSIFICATION = 1  # 图像分类


@unique
class TaskMode(int, Enum):

    LOCAL = 1
    FED_AVG = 2
    HETERO_NN_HOST = 3
    HETERO_NN_COLLABORATOR = 4


@unique
class DatasetMode(int, Enum):

    TRAINING = 1
    VALIDATION = 2
    TESTING = 3
    PREDICTING = 4


@dataclass
class MandatoryConfig:
    """Manage meta data of a auto model."""

    entry_file: str
    entry_module: str
    entry_class: str
    param_file: str

    def __init__(self,
                 entry_file: str,
                 entry_module: str,
                 entry_class: str,
                 param_file: str,
                 **kwargs) -> None:
        self.entry_file = entry_file
        self.entry_module = entry_module
        self.entry_class = entry_class
        self.param_file = param_file

        self.__post_init__()

    def __post_init__(self):
        if (
            (self.entry_file and self.entry_module)
            or (not self.entry_file and not self.entry_module)
        ):
            raise TypeError('Must specify one of entry_module and entry_file.')
        if self.entry_module and not isinstance(self.entry_module, str):
            raise TypeError(f'Invalid entry_module: {self.entry_module}')
        if self.entry_file and not isinstance(self.entry_file, str):
            raise TypeError(f'Invalid entry_file: {self.entry_file}')

    def validate_files(self, resource_dir: str):
        """Validate whether specified files are present."""
        resource_dir = resource_dir or ''
        if self.entry_module:
            entry_dir = os.path.join(resource_dir, self.entry_module)
            if not os.path.isdir(entry_dir):
                raise ConfigError(f'Entry module is not found: `{entry_dir}`.')
        if self.entry_file:
            entry_file = os.path.join(resource_dir, self.entry_file)
            if not os.path.isfile(entry_file):
                raise ConfigError(f'Entry file is not found: `{entry_file}`.')
        param_file = os.path.join(resource_dir, self.param_file)
        if not os.path.isfile(param_file):
            raise ConfigError(f'Param file is not found: `{param_file}`.')


class Preprocessor(ABC):

    @abstractmethod
    def transform(self, *args: Any, **kwargs: Any) -> torch.Tensor:
        """Transform a raw input object into an input tensor."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.transform(*args, **kwargs)


class AutoModel(ABC):
    """An model which supports alphamed AutoML process."""

    def __init__(self, resource_dir: str, **kwargs) -> None:
        super().__init__()
        self.resource_dir = resource_dir

    @abstractmethod
    def train(self):
        """Go into `train` mode as of torch.nn.Module."""

    @abstractmethod
    def eval(self):
        """Go into `eval` mode as of torch.nn.Module."""

    @abstractmethod
    def forward(self, *args, **kwargs):
        """Do a forward propagation as of torch.nn.Module."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.forward(*args, **kwargs)

    @abstractmethod
    def init_dataset(self, dataset_dir: str) -> Tuple[bool, str]:
        """Init local dataset and report the result.

        Args:
            dataset_dir:
                The root dir of the dataset staff.

        Return:
            Tuple[is_verification_successful, the_cause_if_it_is_failed]
        """

    @abstractmethod
    def fine_tune(self,
                  id: str,
                  task_id: str,
                  dataset_dir: str,
                  is_initiator: bool = False,
                  recover: bool = False,
                  **kwargs):
        """Begin to fine-tune on dataset.

        Args:
            id:
                The ID of current node.
            task_id:
                The ID of current task.
            dataset_dir:
                The root dir of the dataset staff.
            is_initiator:
                Is current node the initiator of the task.
            recover:
                Whether run as recover mode. Recover moded is used when last fine-tuning is
                failed for some reasons, and current fine-tuning attempt to continue from
                the failure point rather than from the very begining.
            kwargs:
                Other keywords for specific models.
        """

    def push_log(self, message: str):
        """Push a running log message to the task manager."""
        assert message and isinstance(message, str), f'invalid log message: {message}'
        if hasattr(self, 'task_id') and self.task_id:
            task_logger.info(message, extra={"task_id": self.task_id})
        else:
            logger.warn('Failed to push a message because context is not initialized.')


class AutoFedAvgModel(AutoModel):
    """Define interfaces for AutoModels work with FedAvgScheduler."""

    @property
    @abstractmethod
    def training_loader(self) -> DataLoader:
        """Return the dataloader object used in training."""

    @property
    @abstractmethod
    def validation_loader(self) -> DataLoader:
        """Return the dataloader object used in validation."""

    @property
    @abstractmethod
    def testing_loader(self) -> DataLoader:
        """Return the dataloader object used in testing."""

    @property
    @abstractmethod
    def model(self) -> nn.Module:
        """Return the model object used in training and predicting."""

    @property
    @abstractmethod
    def optimizer(self) -> optim.Optimizer:
        """Return the optimizer object used in training."""

    def state_dict(self) -> Dict[str, torch.Tensor]:
        """Get the params that need to train and update.

        Only the params returned by this function will be updated and saved during aggregation.

        Return:
            List[torch.Tensor], The list of model params.
        """
        return self.model.state_dict()

    def load_state_dict(self, state_dict: Dict[str, torch.Tensor]):
        """Load the params that trained and updated.

        Only the params returned by state_dict() should be loaded by this function.
        """
        self.model.load_state_dict(state_dict)

    @abstractmethod
    def train_an_epoch(self) -> Any:
        """Define the training steps in an epoch."""

    @abstractmethod
    def run_test(self) -> Any:
        """Run a round of test."""

    def run_validation(self) -> Any:
        """Run a round of validation."""
        raise NotImplementedError()

    def fine_tuned_files_dict(self) -> Optional[Dict[str, str]]:
        """Return the fine-tuned files used by reinitializing the fine-tuned model.

        The necessary information for reinitialize a fine-tuned model object
        after training, i.e. the new label list, can be saved in files whose
        path will be returned in `fine_tuned_files`. Those files will then be
        included in the result package and be persistent in the task context.
        So that it can be downloaded later and used by reinitializing the
        fine-tuned model.

        The records of files are in format:
        {
            'relative_path_to_resource_dir_root': 'real_path_to_access_file'
        }
        """
        return {}

    @property
    def result_dir(self):
        """Return the directory to store fine-tune result files."""
        if hasattr(self, 'scheduler'):
            return self.scheduler._result_dir
        else:
            raise AutoModelError('Can not save result files before initializing a scheduler.')

    def _fine_tune_impl(self,
                        id: str,
                        task_id: str,
                        dataset_dir: str,
                        scheduler_impl: Type['AutoFedAvgScheduler'],
                        is_initiator: bool = False,
                        recover: bool = False,
                        max_rounds: int = 0,
                        merge_epochs: int = 1,
                        calculation_timeout: int = 300,
                        schedule_timeout: int = 30,
                        log_rounds: int = 0,
                        **kwargs):

        is_dataset_ready, cause_of_failure = self.init_dataset(dataset_dir)
        if not is_dataset_ready:
            raise AutoModelError(f'Failed to initialize dataset. {cause_of_failure}')

        if is_initiator and not self.testing_loader:
            raise AutoModelError('The initiator must provide testing dataset.')
        if not is_initiator and not self.training_loader:
            raise AutoModelError('The collaborator must provide training dataset.')

        involve_aggregator = bool(self.training_loader
                                  and len(self.training_loader) > 0)

        self.scheduler = scheduler_impl(auto_proxy=self,
                                        max_rounds=max_rounds,
                                        merge_epochs=merge_epochs,
                                        calculation_timeout=calculation_timeout,
                                        schedule_timeout=schedule_timeout,
                                        log_rounds=log_rounds,
                                        involve_aggregator=involve_aggregator,
                                        **kwargs)
        self.scheduler._run(id=id,
                            task_id=task_id,
                            is_initiator=is_initiator,
                            recover=recover)

    def push_log(self, message: str):
        return self.scheduler.push_log(message)


class AutoFedAvgScheduler(FedAvgScheduler):

    def __init__(self,
                 auto_proxy: AutoFedAvgModel,
                 max_rounds: int = 0,
                 merge_epochs: int = 1,
                 calculation_timeout: int = 300,
                 schedule_timeout: int = 30,
                 log_rounds: int = 0,
                 involve_aggregator: bool = False,
                 **kwargs):
        super().__init__(max_rounds=max_rounds,
                         merge_epochs=merge_epochs,
                         calculation_timeout=calculation_timeout,
                         schedule_timeout=schedule_timeout,
                         log_rounds=log_rounds,
                         involve_aggregator=involve_aggregator)
        self.auto_proxy = auto_proxy

    def build_model(self) -> nn.Module:
        return self.auto_proxy.model

    def build_optimizer(self, model: nn.Module) -> optim.Optimizer:
        return self.auto_proxy.optimizer

    def build_train_dataloader(self) -> DataLoader:
        return self.auto_proxy.training_loader

    def build_validation_dataloader(self) -> DataLoader:
        return self.auto_proxy.validation_loader

    def build_test_dataloader(self) -> DataLoader:
        return self.auto_proxy.testing_loader

    def state_dict(self) -> Dict[str, torch.Tensor]:
        return self.auto_proxy.state_dict()

    def load_state_dict(self, state_dict: Dict[str, torch.Tensor]):
        return self.auto_proxy.load_state_dict(state_dict)

    @property
    def best_state_dict(self) -> Dict[str, torch.Tensor]:
        """Return the best state of the model by now."""
        return self.state_dict()

    def _init_contractor(self):
        return AutoFedAvgContractor(task_id=self.task_id)

    def _run_a_round(self):
        super()._run_a_round()
        self._report_progress()

    def _report_progress(self) -> bool:
        max_rounds = (self.max_rounds
                      if not self.validation_loader or len(self.validation_loader) == 0
                      else max(int(self.max_rounds * 0.8), 20))
        percent = self.current_round * 100 // max_rounds
        percent = min(percent, 99)
        self.contractor.report_progress(percent=percent)

    def _save_model(self):
        """Save the best or final state of fine tuning."""
        with open(os.path.join(self._checkpoint_dir, 'model_ckpt.pt'), 'wb') as f:
            torch.save(self.best_state_dict, f)
        self.push_log('Saved latest parameters locally.')

    def _prepare_task_output(self) -> Tuple[str, str]:
        """Generate final output files of the task.

        Return:
            Local paths of the report file and model file.
        """
        self.push_log('Uploading task achievement and closing task ...')

        report_file = os.path.join(self._result_dir, "report.zip")
        with ZipFile(report_file, 'w') as report_zip:
            for path, _, filenames in os.walk(self._log_dir):
                rel_dir = os.path.relpath(path=path, start=self._result_dir)
                rel_dir = rel_dir.lstrip('.')  # ./file => file
                for _file in filenames:
                    rel_path = os.path.join(rel_dir, _file)
                    report_zip.write(os.path.join(path, _file), rel_path)
        report_file_path = os.path.abspath(report_file)

        # torch.jit doesn't work with a TemporaryFile
        resource_dir = self.auto_proxy.resource_dir
        resource_zip_file = os.path.join(self._result_dir, 'model.zip')

        with ZipFile(resource_zip_file, 'w') as resource_zip:
            fine_tuned_files_dict = self.auto_proxy.fine_tuned_files_dict() or {}
            # package files of pretrained model
            for path, _, filenames in os.walk(resource_dir):
                rel_dir = os.path.relpath(path=path, start=resource_dir)
                rel_dir = rel_dir.lstrip('.')  # ./file => file
                for _file in filenames:
                    rel_path = os.path.join(rel_dir, _file)
                    # skip fine-tuned results
                    if rel_path not in fine_tuned_files_dict.keys():
                        resource_zip.write(os.path.join(path, _file), rel_path)
            # package files of fine-tuned model
            for arc_path, src_path in fine_tuned_files_dict.items():
                resource_zip.write(src_path, arc_path)
        resource_file_path = os.path.abspath(resource_zip_file)

        self.push_log('Task achievement files are ready.')
        return report_file_path, resource_file_path
