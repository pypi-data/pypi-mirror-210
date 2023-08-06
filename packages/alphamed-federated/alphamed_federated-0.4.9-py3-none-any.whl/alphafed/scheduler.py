"""Algorithm scheduler."""

import inspect
import os
import sys
from abc import ABC, abstractmethod
from typing import Set, Tuple
from zipfile import ZipFile

import cloudpickle as pickle

from . import is_mock_mode, logger, task_logger
from .contractor import TaskContractor


class ConfigError(Exception):
    ...


class TaskFailed(Exception):
    ...


class TaskComplete(Exception):
    ...


class DataChecker(ABC):
    """To verify local data state."""

    @abstractmethod
    def verify_data(self) -> Tuple[bool, str]:
        """Verify if local data is ready or not.

        Return:
            Tuple[verification result, explanation of the cause of the failure]
        """

    def submit(self, task_id: str):
        """Submit the data checker of the task to the task manager.

        `Only for platform developers`:
        This method is running in `notebook` context, so it cannot access the common
        local directory shared by federated-service. Thus it have to upload files in a stream.
        """
        assert task_id and isinstance(task_id, str), 'Must specify task ID.'

        save_dir = os.path.join('/tmp', task_id)
        os.makedirs(save_dir, exist_ok=True)
        pickle_file = os.path.join(save_dir, 'entry.pickle')
        with open(pickle_file, 'wb') as f:
            pickle.dump(self, f)

        current_dir = os.path.abspath('.')
        dependencies: Set[str] = set()
        # sys.modules could change in the iteration.
        for _module in dict(sys.modules).values():
            try:
                _module_file = inspect.getabsfile(_module)
                if _module_file.startswith(current_dir):
                    dependencies.add(_module_file)
            except (TypeError, ModuleNotFoundError):
                pass

        zip_file = os.path.join(save_dir, 'src.zip')
        offset = len(current_dir)
        with ZipFile(zip_file, 'w') as src_zip:
            # include pickle of code in notebook cell
            src_zip.write(pickle_file, os.path.basename(pickle_file))
            # include dependent python files under same directory
            for _file in dependencies:
                src_zip.write(_file, _file[offset:])
            # include requirements.txt if exists
            requirements_file = os.path.join(current_dir, 'requirements.txt')
            if os.path.exists(requirements_file):
                src_zip.write(requirements_file, os.path.basename(requirements_file))

        with open(zip_file, 'rb') as src_zip:
            task_contractor = TaskContractor(task_id=task_id)
            file_url = task_contractor.upload_file(upload_name='src.zip',
                                                   fp=src_zip,
                                                   persistent=True)
        task_contractor._submit_data_checker(resource_url=file_url,
                                             entry_type=TaskContractor._ENTRY_PICKLE)
        logger.info('Submit the data checker complete.')


class Scheduler(ABC):

    def submit(self, task_id: str):
        """Submit the task scheduler to the task manager.

        `Only for platform developers`:
        This method is running in `notebook` context, so it cannot access the common
        local directory shared by federated-service. Thus it have to upload files in a stream.
        """
        assert task_id and isinstance(task_id, str), f'invalid task ID: {task_id}'

        save_dir = os.path.join('/tmp', task_id)
        os.makedirs(save_dir, exist_ok=True)
        pickle_file = os.path.join(save_dir, 'entry.pickle')
        with open(pickle_file, 'wb') as f:
            pickle.dump(self, f)

        current_dir = os.path.abspath('.')
        dependencies: Set[str] = set()
        # sys.modules could change in the iteration.
        for _module in dict(sys.modules).values():
            try:
                _module_file = inspect.getabsfile(_module)
                if _module_file.startswith(current_dir):
                    dependencies.add(_module_file)
            except (TypeError, ModuleNotFoundError):
                pass

        zip_file = os.path.join(save_dir, 'src.zip')
        offset = len(current_dir)
        with ZipFile(zip_file, 'w') as src_zip:
            # include pickle of code in notebook cell
            src_zip.write(pickle_file, os.path.basename(pickle_file))
            # include dependent python files under same directory
            for _file in dependencies:
                src_zip.write(_file, _file[offset:])
            # include requirements.txt if exists
            requirements_file = os.path.join(current_dir, 'requirements.txt')
            if os.path.exists(requirements_file):
                src_zip.write(requirements_file, os.path.basename(requirements_file))

        with open(zip_file, 'rb') as src_zip:
            task_contractor = TaskContractor(task_id=task_id)
            file_url = task_contractor.upload_file(upload_name='src.zip',
                                                   fp=src_zip,
                                                   persistent=True)
        task_contractor._submit_scheduler(resource_url=file_url,
                                          entry_type=TaskContractor._ENTRY_PICKLE)
        logger.info('Submit the scheduler complete.')

    def push_log(self, message: str):
        """Push a running log message to the task manager."""
        assert message and isinstance(message, str), f'invalid log message: {message}'
        if not is_mock_mode() and hasattr(self, 'task_id') and self.task_id:
            task_logger.info(message, extra={"task_id": self.task_id})
        logger.info(message)

    def _switch_status(self, _status: str):
        """Switch to a new status and leave a log."""
        self.status = _status
        logger.debug(f'{self.status=}')

    @abstractmethod
    def _run(self, id: str, task_id: str, is_initiator: bool = False, recover: bool = False):
        """Run the scheduler.

        This function is used by the context manager, DO NOT modify it, otherwize
        there would be strange errors raised.

        Args:
            id:
                the node id of the running context
            task_id:
                the id of the task to be scheduled
            is_initiator:
                is this scheduler the initiator of the task
            recover:
                whether to try recovering from last failed running
        """
