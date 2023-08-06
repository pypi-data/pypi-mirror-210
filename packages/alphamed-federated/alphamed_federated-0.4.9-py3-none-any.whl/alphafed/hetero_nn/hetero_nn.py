"""The host of a hetero_nn task.

Reference: https://arxiv.org/pdf/2007.06849.pdf
"""

import io
import json
import os
import shutil
import sys
import traceback
from abc import ABC, ABCMeta, abstractmethod
from tempfile import TemporaryFile
from typing import Dict, List, Set, Tuple, final
from zipfile import ZipFile

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter

from .. import get_result_dir, get_runtime_dir, logger
from ..data_channel import SharedFileDataChannel
from ..scheduler import ConfigError, Scheduler, TaskComplete, TaskFailed
from .contractor import (CheckinEvent, CheckinResponseEvent, CloseRoundEvent,
                         CloseTestRoundEvent, CollaboratorCompleteEvent,
                         CompleteTaskEvent, ContractEvent, FailTaskEvent,
                         HeteroNNContractor, ReadyForFusionEvent,
                         ResetRoundEvent, StartRoundEvent, StartTestRoundEvent,
                         SyncStateEvent, SyncStateResponseEvent)
from .psi import RSAPSICollaboratorScheduler, RSAPSIInitiatorScheduler

__all__ = ['HeteroNNHostScheduler', 'HeteroNNCollaboratorScheduler']

_FEATURE_KEY = str


class ResetRound(Exception):
    ...


class _SimplifiedOptimizer(ABC):
    """A simplified optimizer tool to facilitate update parameters."""

    @abstractmethod
    def zero_grad(self):
        """To clean grad of parameters, as a normal PyTorch Optimizer."""

    @abstractmethod
    def step(self):
        """To update parameters, as a normal PyTorch Optimizer."""


class HeteroNNScheduler(Scheduler, metaclass=ABCMeta):
    """Base scheduler for heteto_nn tasks."""

    _INIT = 'init'
    _GETHORING = 'gethoring'
    _ID_INTERSECTION = 'id_intersection'
    _READY = 'ready'
    _SYNCHRONIZING = 'synchronizing'
    _IN_A_ROUND = 'in_a_round'
    _PROJECTING = 'projecting'
    _FINISHING = 'finishing'
    _UPDATING = 'updating'
    _PERSISTING = 'persisting'
    _TESTING = 'testing'
    _CLOSING_ROUND = 'closing_round'

    def __init__(self) -> None:
        super().__init__()
        self.feature_model
        self.feature_optimizer

        self._id_intersection = None
        self._local_features: torch.Tensor = None
        self._example_feature_inputs = None

    @abstractmethod
    def _setup_context(self, id: str, task_id: str, is_initiator: bool = False):
        assert id, 'must specify a unique id for every participant'
        assert task_id, 'must specify a task_id for every participant'

        self.id = id
        self.task_id = task_id
        self.is_host = is_initiator
        self._result_dir = get_result_dir(self.task_id)
        self._log_dir = os.path.join(self._result_dir, 'tb_logs')
        self.tb_writer = SummaryWriter(log_dir=self._log_dir)

        self.contractor = HeteroNNContractor(task_id=task_id)
        self.data_channel = SharedFileDataChannel(self.contractor)

    @abstractmethod
    def load_local_ids(self) -> List[str]:
        """Load all local data IDs for PSI."""

    @abstractmethod
    def split_dataset(self, id_intersection: Set[str]) -> Tuple[Set[str], Set[str]]:
        """Split dataset into train set and test set.

        NOTE: Must make sure each node gets the same split results.

        :return
            A tuple of ID set of training dataset and of testing dataset:
            (Set[train_ids], Set[test_ids]).
        """

    @abstractmethod
    def build_feature_model(self) -> nn.Module:
        """Return a model object to project input to features.

        The output of feature model MUST be a (str_keyword, torch.Tensor) tuple, where
        str_keyword is used by the host to distinguish features from collaborators
        and Tensor is a two dimension (batch, feature_vector) tensor as the input
        of projection layer.
        """

    @property
    def feature_model(self) -> nn.Module:
        if not hasattr(self, '_feature_model'):
            self._feature_model = self.build_feature_model()
        return self._feature_model

    @abstractmethod
    def build_feature_optimizer(self, feature_model: nn.Module) -> optim.Optimizer:
        """Return a optimizer object to facilitate training feature model.

        :args
            :feature_model
                The feature model object to train & test.
        """

    @final
    @property
    def feature_optimizer(self) -> optim.Optimizer:
        if not hasattr(self, '_feature_optimizer'):
            assert self.feature_model, 'Must initialize feature model at first.'
            self._feature_optimizer = self.build_feature_optimizer(self.feature_model)
        return self._feature_optimizer

    @final
    @property
    def id_intersection(self) -> Set[str]:
        """Return the intersection of whole dataset IDs."""
        assert self._id_intersection is not None, 'Have not run ID intersection process.'
        return self._id_intersection

    @final
    @property
    def train_ids(self) -> Set[str]:
        """Return the ID set of training dataset intersection."""
        if not hasattr(self, '_train_ids'):
            assert self.id_intersection, 'Must get the whole ID intersection at first.'
            self._train_ids, self._test_ids = self.split_dataset(self.id_intersection.copy())
        return self._train_ids

    @final
    @property
    def test_ids(self) -> Set[str]:
        """Return the ID set of testing dataset intersection."""
        if not hasattr(self, '_test_ids'):
            assert self.id_intersection, 'Must get the whole ID intersection at first.'
            self._train_ids, self._test_ids = self.split_dataset(self.id_intersection.copy())
        return self._test_ids

    @abstractmethod
    def _launch_process(self):
        """Run the main process of the task."""

    @abstractmethod
    def _recover_progress():
        """Try to recover progress from last running."""

    @abstractmethod
    def _clean_progress(self):
        """Clean existing progress data."""

    def _run(self, id: str, task_id: str, is_initiator: bool = False, recover: bool = False):
        self._setup_context(id=id, task_id=task_id, is_initiator=is_initiator)
        self.push_log(message='Local context is ready.')
        try:
            if recover:
                self._recover_progress()
            else:
                self._clean_progress()
            self._launch_process()
        except Exception:
            err_stack = '\n'.join(traceback.format_exception(*sys.exc_info()))
            self.push_log(err_stack)


class HeteroNNHostScheduler(HeteroNNScheduler):
    """Schedule the process of the host in a hetero_nn task."""

    _WAITING_FOR_FEATURES = 'wait_4_feature'
    _GETTING_GRAD = 'calc_loss'
    _DISTRIBUTING_FEATURE_GRAD = 'distribute_grad'

    def __init__(self,
                 feature_key: str,
                 max_rounds: int = 0,
                 calculation_timeout: int = 300,
                 schedule_timeout: int = 30,
                 log_rounds: int = 0,
                 is_feature_trainable: bool = True) -> None:
        r"""Init.

        :args
            :feature_key
                A unique key of feature used by the host to distinguish features
                from collaborators.
            :max_rounds
                Maximal number of training rounds.
            :calculation_timeout
                Seconds to timeout for calculation in a round. Takeing off timeout
                by setting its value to 0.
            :schedule_timeout
                Seconds to timeout for process scheduling. Takeing off timeout
                by setting its value to 0.
            :log_rounds
                The number of rounds to run testing and log the result. Skip it
                by setting its value to 0.
            :is_feature_trainable
                Decide whether or not train the feature model
        """
        super().__init__()
        self._switch_status(self._INIT)

        self.feature_key = feature_key
        self.max_rounds = max_rounds
        self.calculation_timeout = calculation_timeout
        self.schedule_timeout = schedule_timeout
        self.log_rounds = log_rounds
        self.is_feature_trainable = is_feature_trainable  # TODO 暂时不考虑

        self._validate_config()

        self.infer_model
        self.infer_optimizer

        self.current_round = 1
        self._partners: List[str] = []

        self._example_project_input = None
        self._example_infer_input = None

        self._alpha_map: Dict[str, Dict[_FEATURE_KEY, torch.Tensor]] = {}
        self._feature_fusion_map: Dict[_FEATURE_KEY, torch.Tensor] = {}
        self._batched_test_features: List[List[Dict[_FEATURE_KEY, torch.Tensor]]] = []

    def _validate_config(self):
        if not self.feature_key or not isinstance(self.feature_key, str):
            raise ConfigError('Must specify a feature_key of type string.')

    @abstractmethod
    def build_infer_model(self) -> nn.Module:
        """Return a model object to infer business results."""

    @final
    @property
    def infer_model(self) -> nn.Module:
        if not hasattr(self, '_infer_model'):
            self._infer_model = self.build_infer_model()
        return self._infer_model

    @abstractmethod
    def build_infer_optimizer(self, infer_model: nn.Module) -> optim.Optimizer:
        """Return a optimizer object to facilitate training infer model.

        :args
            :infer_model
                The infer model object to train & test.
        """

    @final
    @property
    def infer_optimizer(self) -> optim.Optimizer:
        if not hasattr(self, '_infer_optimizer'):
            self._infer_optimizer = self.build_infer_optimizer(self.infer_model)
        return self._infer_optimizer

    @final
    @property
    def optimizer(self) -> _SimplifiedOptimizer:
        """Return a general optimizer to wrap the 3 (feature, project, infer) optimizers."""

        class _OptimizerImpl(_SimplifiedOptimizer):

            def __init__(self, host_obj: HeteroNNHostScheduler) -> None:
                super().__init__()
                self.host_obj = host_obj

            def zero_grad(self):
                self.host_obj.infer_optimizer.zero_grad()
                self.host_obj.feature_optimizer.zero_grad()

            def step(self):
                self.host_obj.infer_optimizer.step()
                self.host_obj.feature_optimizer.step()

        if not hasattr(self, '_optimizer'):
            self._optimizer = _OptimizerImpl(host_obj=self)
        return self._optimizer

    @abstractmethod
    def iterate_train_feature(self,
                              feature_model: nn.Module,
                              train_ids: Set[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        """Iterate over train dataset and features a batch of data each time.

        :args
            :feature_model
                The feature model object to train & test.
            :train_ids
                The ID set of train dataset.
        :return
            A tuple of a batch of train data and their labels. (train_data, labels)
        """

    @abstractmethod
    def iterate_test_feature(self,
                             feature_model: nn.Module,
                             test_ids: Set[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        """Iterate over test dataset and features a batch of data each time.

        :args
            :feature_model
                The feature model object to train & test.
            :train_ids
                The ID set of test dataset.
        :return
            A tuple of a batch of test data and their labels. (test_data, labels)
        """

    @abstractmethod
    def train_a_batch(self, feature_projection: Dict[str, torch.Tensor], labels: torch.Tensor):
        """Train a batch of data in infer model.

        :args
            :feature_projection
                A map containing features from all nodes of type feature_key => feature_tensor.
            :labels
                Corresponding labels of the batch of data.
        """

    @abstractmethod
    def run_test(self,
                 batched_feature_projection: List[Dict[str, torch.Tensor]],
                 batched_labels: List[torch.Tensor]):
        """Define the testing steps.

        If you do not want to do testing after training, simply make it pass.

        :args
            :batched_feature_projections
                A list of feature projection grouped by batch of testing data. Each batch
                is a map containing features from all nodes of type feature_key => feature_tensor.
            :batched_labels
                A list of labels grouped by batch of testing data.
        """

    def validate_context(self):
        """Validate if the local running context is ready.

        For example: check if train and test dataset could be loaded successfully.
        """
        if self.feature_model is None:
            raise ConfigError('Failed to initialize a feature model.')
        if not isinstance(self.feature_model, nn.Module):
            err_msg = 'Support feature model of type torch.Module only.'
            err_msg += f'Got a {type(self.feature_model)} object.'
            raise ConfigError(err_msg)
        if self.feature_optimizer is None:
            raise ConfigError('Failed to initialize a feature optimizer.')
        if not isinstance(self.feature_optimizer, optim.Optimizer):
            err_msg = 'Support feature optimizer of type torch.optim.Optimizer only.'
            err_msg += f'Got a {type(self.feature_optimizer)} object.'
            raise ConfigError(err_msg)

        if self.infer_model is None:
            raise ConfigError('Failed to initialize a infer model.')
        if not isinstance(self.infer_model, nn.Module):
            err_msg = 'Support infer model of type torch.Module only.'
            err_msg += f'Got a {type(self.infer_model)} object.'
            raise ConfigError(err_msg)
        if self.infer_optimizer is None:
            raise ConfigError('Failed to initialize a infer optimizer.')
        if not isinstance(self.infer_optimizer, optim.Optimizer):
            err_msg = 'Support infer optimizer of type torch.optim.Optimizer only.'
            err_msg += f'Got a {type(self.infer_optimizer)} object.'
            raise ConfigError(err_msg)

        if not self._partners:
            raise TaskFailed('No partners.')

    def is_task_finished(self) -> bool:
        """By default true if reach the max rounds configured."""
        return self._is_reach_max_rounds()

    def _init_partners(self):
        """Query and set all partners in this task."""
        self._partners = self.contractor.query_partners()
        self._partners.remove(self.id)

    def _setup_context(self, id: str, task_id: str, is_initiator: bool = False):
        super()._setup_context(id=id, task_id=task_id, is_initiator=is_initiator)

        self._init_partners()
        self._check_in_status = {_partner: False for _partner in self._partners}
        self._is_gathering_complete = False

        self._runtime_dir = get_runtime_dir(self.task_id)
        self._context_file = os.path.join(self._runtime_dir, ".context.json")
        self._checkpoint_dir = os.path.join(self._runtime_dir, 'checkpoint')
        self._feature_ckpt_file = os.path.join(self._checkpoint_dir, 'feature_model_ckp.pt')
        self._infer_ckpt_file = os.path.join(self._checkpoint_dir, 'infer_model_ckp.pt')

        self.push_log(message='Begin to validate local context.')
        self.validate_context()

    def _recover_progress(self):
        if not os.path.isfile(self._context_file):
            raise TaskFailed('Failed to recover progress: missing cached context.')

        with open(self._context_file, 'r') as f:
            context_info = json.load(f)
        round = context_info.get('round')
        feature_ckpt_file = context_info.get('feature_ckpt_file')
        infer_ckpt_file = context_info.get('infer_ckpt_file')
        assert round and isinstance(round, int) and round > 0, f'Invalid round: {round} .'
        assert (
            feature_ckpt_file and isinstance(feature_ckpt_file, str)
        ), f'Invalid feature_ckpt_file: {feature_ckpt_file} .'
        assert (
            infer_ckpt_file and isinstance(infer_ckpt_file, str)
        ), f'Invalid infer_ckpt_file: {infer_ckpt_file} .'
        if not os.path.isfile(feature_ckpt_file) or not os.path.isfile(infer_ckpt_file):
            raise TaskFailed('Failed to recover progress: missing checkpoint parameters.')

        self.current_round = round
        with open(feature_ckpt_file, 'rb') as f:
            state_dict = torch.load(f)
            self.feature_model.load_state_dict(state_dict)
        with open(infer_ckpt_file, 'rb') as f:
            state_dict = torch.load(f)
            self.infer_model.load_state_dict(state_dict)

    def _clean_progress(self):
        """Clean existing progress data."""
        shutil.rmtree(self._runtime_dir, ignore_errors=True)
        shutil.rmtree(self._result_dir, ignore_errors=True)
        os.makedirs(self._runtime_dir, exist_ok=True)
        os.makedirs(self._checkpoint_dir, exist_ok=True)
        os.makedirs(self._result_dir, exist_ok=True)
        os.makedirs(self._log_dir, exist_ok=True)

    def _is_reach_max_rounds(self) -> bool:
        """Is the max rounds configuration reached."""
        return self.current_round >= self.max_rounds

    def _validate_feature_dict(self, features: Dict[str, torch.Tensor]):
        """Validate feature format."""
        if not features or not isinstance(features, dict) or len(features) != 1:
            self.push_log(f'Received invalid features: {features}')
            err_msg = r'Invalid feature type. It must be a dict of {feature_key: feature tensor}.'
            raise TaskFailed(err_msg)
        _key, _val = features.copy().popitem()
        if not _key or not isinstance(_key, str):
            self.push_log(f'Received invalid feature key: {_key}')
            raise TaskFailed('Invalid feature type. It must contain a keyword of string.')
        if _val is None or not isinstance(_val, torch.Tensor) or _val.dim() != 2:
            self.push_log(f'Received invalid feature value: {_val}')
            raise TaskFailed('Invalid feature type. Its value must be a tensor of two dimension.')

    def _launch_process(self):
        try:
            assert self.status == self._INIT, 'must begin from initial status'
            self.push_log(f'Node {self.id} is up.')

            self._switch_status(self._GETHORING)
            self._check_in()

            self._switch_status(self._READY)
            while self.status == self._READY:
                try:
                    self._switch_status(self._SYNCHRONIZING)
                    self._sync_state()

                    if not self._id_intersection:
                        self._switch_status(self._ID_INTERSECTION)
                        self._make_id_intersection()

                    self._switch_status(self._IN_A_ROUND)
                    self._run_a_round()
                    self._switch_status(self._READY)
                    delattr(self, '_train_ids')
                    delattr(self, '_test_ids')
                except ResetRound:
                    self.push_log('WARNING: Reset runtime context, there might be an error raised.')
                    self._switch_status(self._READY)
                    self._id_intersection = None
                    delattr(self, '_train_ids')
                    delattr(self, '_test_ids')
                    continue

                if self.is_task_finished():
                    self.push_log(f'Obtained the final results of task {self.task_id}')
                    self._switch_status(self._FINISHING)
                    self._close_task(is_succ=True)

                self.current_round += 1

        except TaskFailed as err:
            logger.exception(err)
            self._close_task(is_succ=False)

    def _check_in(self):
        """Check in task and connect every partners."""
        self.push_log('Waiting for participants taking part in ...')
        for _event in self.contractor.contract_events():
            if isinstance(_event, CheckinEvent):
                self._handle_check_in(_event)
                if all(self._check_in_status.values()):
                    self._is_gathering_complete = True
                    break
        self.push_log('All partners have gethored.')

    def _handle_check_in(self, _event: CheckinEvent):
        self._check_in_status[_event.peer_id] = True
        self.push_log(f'Welcome a new partner ID: {_event.peer_id}.')
        self.push_log(f'There are {sum(self._check_in_status.values())} partners now.')
        self.contractor.respond_check_in(round=self.current_round,
                                         host=self.id,
                                         nonce=_event.nonce,
                                         requester_id=_event.peer_id)
        if self._is_gathering_complete:
            self.contractor.sync_state(round=self.current_round, host=self.id)

    def _sync_state(self):
        """Synchronize state before each round, so it's easier to manage the process.

        As a host, iterates round, broadcasts and resets context of the new round.
        """
        self.push_log(f'Initiate state synchronization of round {self.current_round}.')
        self.contractor.sync_state(round=self.current_round, host=self.id)

        sync_status = {_partner: False for _partner in self._partners}
        self.push_log('Waiting for synchronization responses ...')
        for _event in self.contractor.contract_events(timeout=0):
            if isinstance(_event, SyncStateResponseEvent):
                if _event.round != self.current_round:
                    continue
                if sync_status.get(_event.peer_id) is False:
                    sync_status[_event.peer_id] = True
                    self.push_log(f'Successfully synchronized state with ID: {_event.peer_id}.')
                if sum(sync_status.values()) == len(self._partners):
                    break
            elif isinstance(_event, CheckinEvent):
                self._handle_check_in(_event)

        self.push_log(f'Successfully synchronized state in round {self.current_round}')

    def _make_id_intersection(self) -> List[str]:
        """Make PSI and get id intersection for training."""
        local_ids = self.load_local_ids()
        psi_scheduler = RSAPSIInitiatorScheduler(
            task_id=self.task_id,
            initiator_id=self.id,
            ids=local_ids,
            collaborator_ids=self._partners,
            contractor=self.contractor
        )
        self._id_intersection = psi_scheduler.make_intersection()

    def _run_a_round(self):
        try:
            self._start_round()
            self.infer_model.train()
            self.feature_model.train()
            for _feature_batch, _labels in self.iterate_train_feature(
                self.feature_model, self.train_ids
            ):
                self.push_log('Featured a batch of data.')
                self._local_features = _feature_batch
                self._switch_status(self._WAITING_FOR_FEATURES)
                self._collect_features()
                self._switch_status(self._GETTING_GRAD)
                self.train_a_batch(self._feature_fusion_map, _labels)
                self._switch_status(self._DISTRIBUTING_FEATURE_GRAD)
                self._distribute_feature_grad()

            self._switch_status(self._PERSISTING)
            self._save_model()
            self._save_runtime_context()
            self._switch_status(self._TESTING)
            self._check_and_run_test()
            self._switch_status(self._CLOSING_ROUND)
            self._close_round()
        except TaskFailed as err:
            err_stack = '\n'.join(traceback.format_exception(*sys.exc_info()))
            self.push_log(err_stack)
            self.contractor.reset_round()
            raise ResetRound(err)

    def _start_round(self):
        """Prepare and start calculation of a round."""
        self.push_log(f'Begin the training of round {self.current_round}.')
        self.contractor.start_round(round=self.current_round)
        self.push_log(f'Calculation of round {self.current_round} is started.')

    def _collect_features(self) -> Dict[str, torch.Tensor]:
        """Collect all input features from all partners."""
        self.push_log('Waiting for collecting all features from partners ...')
        self.contractor.notify_ready_for_fusion(self.current_round)
        feature_map: Dict[str, Dict[str, torch.Tensor]] = {
            self.id: {self.feature_key: self._local_features}
        }

        feature_results = self.data_channel.batch_receive_stream(
            receiver=self.id,
            source_list=self._partners,
            timeout=self.calculation_timeout
        )
        for _source, _feature_stream in feature_results.items():
            buffer = io.BytesIO(_feature_stream)
            features = torch.load(buffer)
            self._validate_feature_dict(features)
            feature_map[_source] = features
            self.push_log(f'Received features from ID: {_source}')

        if len(feature_map) == len(self._partners) + 1:  # plus self
            self._alpha_map = feature_map
            features = dict(feature_dict.copy().popitem()
                            for feature_dict in self._alpha_map.values())
            self._feature_fusion_map = features
        else:
            raise TaskFailed('Failed to collect all features.')

    def _distribute_feature_grad(self):
        """Distribute feature grad tensors to collaborators."""
        self.push_log('Distributing features grad tensors ...')
        for _partner, _feature_dict in self._alpha_map.items():
            if _partner == self.id:
                continue
            _, feature_tensor = _feature_dict.copy().popitem()
            with TemporaryFile() as tf:
                torch.save(feature_tensor.grad, tf)
                tf.seek(0)
                self.data_channel.send_stream(source=self.id,
                                              target=_partner,
                                              data_stream=tf.read())
        self.push_log('Distributed all features grad tensors to collaborators.')

    def _save_model(self):
        """Save latest model state."""
        with open(self._feature_ckpt_file, 'wb') as f:
            torch.save(self.feature_model.state_dict(), f)
        with open(self._infer_ckpt_file, 'wb') as f:
            torch.save(self.infer_model.state_dict(), f)
        self.push_log('Saved latest parameters locally.')

    def _save_runtime_context(self):
        """Save runtime context information in case of restoring."""
        context_info = {
            'round': self.current_round,
            'feature_ckpt_file': self._feature_ckpt_file,
            'infer_ckpt_file': self._infer_ckpt_file
        }
        with open(self._context_file, 'w') as f:
            f.write(json.dumps(context_info, ensure_ascii=False))
        self.push_log('Saved latest runtime context.')

    @torch.no_grad()
    def _check_and_run_test(self):
        """Run test if match configured conditions."""
        if (
            self.current_round == 1
            or (self.log_rounds > 0 and self.current_round % self.log_rounds == 0)
            or self.current_round == self.max_rounds
        ):
            self.push_log('Start a round of test.')

            self.feature_model.eval()
            self.infer_model.eval()

            self.contractor.start_test_round(round=self.current_round)

            batched_host_features = []
            batched_labels = []
            for _feature_batch, _labels in self.iterate_test_feature(
                self.feature_model, self.test_ids
            ):
                batched_host_features.append((self.feature_key, _feature_batch))
                batched_labels.append(_labels)

            self._switch_status(self._WAITING_FOR_FEATURES)
            self._wait_for_testing_features()
            self._batched_test_features.append(batched_host_features)
            self._switch_status(self._PROJECTING)
            batched_feature_projections = [dict(_batch)
                                           for _batch in zip(*self._batched_test_features)]
            self.push_log('Fused test data features.')

            self.run_test(batched_feature_projections=batched_feature_projections,
                          batched_labels=batched_labels)
            self.push_log('Complete a round of test.')

        self.push_log('Skip or close a round of testing.')
        self.contractor.close_test_round(round=self.current_round)

    def _wait_for_testing_features(self):
        """Wait for collecting test dataset features."""
        self.push_log('Waiting for collecting test dataset features ...')
        self._batched_test_features = []

        test_feature_results = self.data_channel.batch_receive_stream(
            receiver=self.id,
            source_list=self._partners,
            timeout=self.calculation_timeout
        )
        for _source, _feature_stream in test_feature_results.items():
            buffer = io.BytesIO(_feature_stream)
            batched_features: dict = torch.load(buffer)
            _key, _feature_list = batched_features.copy().popitem()
            self._batched_test_features.append([(_key, _feature_batch)
                                                for _feature_batch in _feature_list])
            self.push_log(f'Received test dataset features from ID: {_source}.')

        if len(self._batched_test_features) < len(self._partners):
            raise TaskFailed('Failed to collect all testing features.')

    def _close_round(self):
        """Close current round when finished."""
        self.contractor.close_round(round=self.current_round)
        self.push_log(f'The training of Round {self.current_round} complete.')

    def _close_task(self, is_succ: bool = True):
        """Close the task.

        Broadcasts the finish task event to all participants,
        uploads the final parameters and tells L1 task manager the task is complete.
        """
        self.push_log(f'Closing task {self.task_id} ...')

        self._switch_status(self._FINISHING)
        if is_succ:
            report_file_path, model_file_path = self._prepare_task_output()
            self.contractor.upload_metric_report(receivers=self.contractor.EVERYONE,
                                                 report_file=report_file_path)
            self.contractor.upload_model(receivers=[self.id],
                                         model_file=model_file_path)
            self.contractor.finish_task(is_succ=True)
            self._wait_for_all_complete()
            self.contractor.notify_task_completion(result=True)
            self.push_log(f'Task {self.task_id} complete. Byebye!')
        else:
            self.contractor.finish_task(is_succ=False)
            self.push_log(f'Task {self.task_id} failed. Byebye!')

    def _prepare_task_output(self) -> Tuple[str, str]:
        """Generate final output files of the task.

        :return
            Local paths of the report file and model file.
        """
        self.push_log('Generating task achievement files ...')

        report_file = os.path.join(self._result_dir, 'report.zip')
        with ZipFile(report_file, 'w') as report_zip:
            for path, _, filenames in os.walk(self._log_dir):
                rel_dir = os.path.relpath(path=path, start=self._result_dir)
                rel_dir = rel_dir.lstrip('.')  # ./file => file
                for _file in filenames:
                    rel_path = os.path.join(rel_dir, _file)
                    report_zip.write(os.path.join(path, _file), rel_path)
        report_file_path = os.path.abspath(report_file)

        # torch.jit doesn't work with a TemporaryFile
        feature_model_file = os.path.join(self._result_dir,
                                          f'feature_model_{self.feature_key}.pt')
        with open(feature_model_file, 'wb') as f:
            torch.save(self.feature_model.state_dict(), f)
        infer_model_file = f'{os.path.join(self._result_dir, "infer_model.pt")}'
        with open(infer_model_file, 'wb') as f:
            torch.save(self.infer_model.state_dict(), f)
        model_file = os.path.join(self._result_dir, 'model.zip')
        with ZipFile(model_file, 'w') as model_zip:
            model_zip.write(feature_model_file, os.path.basename(feature_model_file))
            model_zip.write(infer_model_file, os.path.basename(infer_model_file))
        model_file_path = os.path.abspath(model_file)

        self.push_log('Task achievement files are ready.')
        return report_file_path, model_file_path

    def _wait_for_all_complete(self):
        """Wait for all collaborators complete their tasks."""
        self.push_log('Waiting for all collaborators complete their tasks ...')
        results = {_peer_id: False for _peer_id in self._partners}
        for _event in self.contractor.contract_events():
            if isinstance(_event, CollaboratorCompleteEvent):
                results[_event.peer_id] = True
                if all(results.values()):
                    break
        self.push_log('All collaborators have completed their tasks.')


class HeteroNNCollaboratorScheduler(HeteroNNScheduler):
    """Schedule the process of a collaborator in a hetero_nn task."""

    _WAITING_FOR_FEATUE_GRAD = 'wait_4_feature_grad'

    def __init__(self,
                 feature_key: str,
                 schedule_timeout: int = 30,
                 is_feature_trainable: bool = True) -> None:
        """Init.

        :args
            :feature_key
                A unique key of feature used by the host to distinguish features
                from collaborators.
            :schedule_timeout
                Seconds to timeout for process scheduling. Takeing off timeout
                by setting its value to 0.
            :is_feature_trainable
                Decide whether or not train the feature model
        """
        super().__init__()
        self._switch_status(self._INIT)

        self.feature_key = feature_key
        self.schedule_timeout = schedule_timeout
        self.is_feature_trainable = is_feature_trainable

        self._validate_config()

        self.current_round = 0

        self.host = None

        self._feature_grad: torch.Tensor = None

    def _validate_config(self):
        if not self.feature_key or not isinstance(self.feature_key, str):
            raise ConfigError('Must specify a feature_key of type string.')

    def validate_context(self):
        """Validate if the local running context is ready.

        For example: check if train and test dataset could be loaded successfully.
        """
        if self.feature_model is None:
            raise ConfigError('Failed to initialize a feature model.')
        if not isinstance(self.feature_model, nn.Module):
            err_msg = 'Support feature model of type torch.Module only.'
            err_msg += f'Got a {type(self.feature_model)} object.'
            raise ConfigError(err_msg)
        if self.feature_optimizer is None:
            raise ConfigError('Failed to initialize a feature optimizer.')
        if not isinstance(self.feature_optimizer, optim.Optimizer):
            err_msg = 'Support feature optimizer of type torch.optim.Optimizer only.'
            err_msg += f'Got a {type(self.feature_optimizer)} object.'
            raise ConfigError(err_msg)

    @abstractmethod
    def iterate_train_feature(self,
                              feature_model: nn.Module,
                              train_ids: Set[str]) -> torch.Tensor:
        """Iterate over train dataset and features a batch of data each time.

        :args
            :feature_model
                The feature model object to train & test.
            :train_ids
                The ID set of train dataset.
        """

    @abstractmethod
    def iterate_test_feature(self,
                             feature_model: nn.Module,
                             test_ids: Set[str]) -> torch.Tensor:
        """Iterate over test dataset and features a batch of data each time.

        :args
            :feature_model
                The feature model object to train & test.
            :train_ids
                The ID set of test dataset.
        """

    def _setup_context(self, id: str, task_id: str, is_initiator: bool = False):
        super()._setup_context(id=id, task_id=task_id, is_initiator=is_initiator)

        self._runtime_dir = get_runtime_dir(self.task_id)
        self._context_file = os.path.join(self._runtime_dir, ".context.json")
        self._checkpoint_dir = os.path.join(self._runtime_dir, 'checkpoint')
        self._feature_ckpt_file = os.path.join(self._checkpoint_dir, "feature_model_ckp.pt")

        self.push_log(message='Begin to validate local context.')
        self.validate_context()

    def _recover_progress(self):
        if not os.path.isfile(self._context_file):
            raise TaskFailed('Failed to recover progress: missing cached context.')

        with open(self._context_file, 'r') as f:
            context_info = json.load(f)
        feature_ckpt_file = context_info.get('feature_ckpt_file')
        assert (
            feature_ckpt_file and isinstance(feature_ckpt_file, str)
        ), f'Invalid feature_ckpt_file: {feature_ckpt_file} .'
        if not os.path.isfile(feature_ckpt_file):
            raise TaskFailed('Failed to recover progress: missing checkpoint parameters.')

        self.current_round = round
        with open(feature_ckpt_file, 'rb') as f:
            state_dict = torch.load(f)
            self.feature_model.load_state_dict(state_dict)

    def _clean_progress(self):
        """Clean existing progress data."""
        shutil.rmtree(self._runtime_dir, ignore_errors=True)
        shutil.rmtree(self._result_dir, ignore_errors=True)
        os.makedirs(self._runtime_dir, exist_ok=True)
        os.makedirs(self._checkpoint_dir, exist_ok=True)
        os.makedirs(self._result_dir, exist_ok=True)

    def _launch_process(self):
        try:
            assert self.status == self._INIT, 'must begin from initial status'
            self.push_log(f'Node {self.id} is up.')

            self._switch_status(self._GETHORING)
            self._check_in()

            self._switch_status(self._READY)
            while self.status == self._READY:
                try:
                    self._switch_status(self._SYNCHRONIZING)
                    self._sync_state()

                    if not self._id_intersection:
                        self._switch_status(self._ID_INTERSECTION)
                        self._make_id_intersection()

                    self._switch_status(self._IN_A_ROUND)
                    self._run_a_round()
                    self._switch_status(self._READY)
                    delattr(self, '_train_ids')
                    delattr(self, '_test_ids')
                except ResetRound:
                    self.push_log('WARNING: Reset runtime context, there might be an error raised.')
                    self._switch_status(self._READY)
                    self._id_intersection = None
                    delattr(self, '_train_ids')
                    delattr(self, '_test_ids')
                    continue

        except TaskComplete:
            logger.info('Task complete')
            self._close_task(is_succ=True)

        except TaskFailed as err:
            logger.exception(err)
            self._close_task(is_succ=False)

    def _check_in(self):
        """Check in task."""
        is_checked_in = False
        # the host may be in special state so can not response
        # correctly nor in time, then retry periodically
        self.push_log('Checking in the task ...')
        while not is_checked_in:
            nonce = self.contractor.checkin(peer_id=self.id)
            logger.debug('_wait_for_check_in_response ...')
            for _event in self.contractor.contract_events(timeout=self.schedule_timeout):
                if isinstance(_event, CheckinResponseEvent):
                    if _event.nonce != nonce:
                        continue
                    self.current_round = _event.round
                    self.host = _event.host
                    is_checked_in = True
                    break

                elif isinstance(_event, FailTaskEvent):
                    raise TaskFailed('Aborted by host.')

        self.push_log(f'Node {self.id} have taken part in the task.')

    def _sync_state(self):
        """Synchronize state before each round, so it's easier to manage the process.

        As a partner, synchronizes state and gives a response.
        """
        self.push_log('Waiting for synchronizing state with the host ...')
        for _event in self.contractor.contract_events():
            if isinstance(_event, SyncStateEvent):
                self.current_round = _event.round
                self.contractor.respond_sync_state(round=self.current_round,
                                                   peer_id=self.id,
                                                   host=_event.host)
                self.push_log('Successfully synchronized state with the host.')
                return
            elif isinstance(_event, FailTaskEvent):
                raise TaskFailed('Aborted by host.')
            elif isinstance(_event, CompleteTaskEvent):
                raise TaskComplete()
            elif isinstance(_event, ResetRoundEvent):
                raise ResetRound()

        self.push_log(f'Successfully synchronized state in round {self.current_round}')

    def _make_id_intersection(self) -> List[str]:
        """Make PSI and get id intersection for training."""
        local_ids = self.load_local_ids()
        psi_scheduler = RSAPSICollaboratorScheduler(
            task_id=self.task_id,
            collaborator_id=self.id,
            ids=local_ids,
            contractor=self.contractor
        )
        self._id_intersection = psi_scheduler.collaborate_intersection()

    def _run_a_round(self):
        self._wait_for_starting_round()
        self.feature_model.train()
        for _batch_features in self.iterate_train_feature(self.feature_model, self.train_ids):
            self.push_log('Featured a batch of data.')
            self._switch_status(self._PROJECTING)
            self._local_features = _batch_features
            self._send_feature()

            self._switch_status(self._WAITING_FOR_FEATUE_GRAD)
            self._wait_for_feature_grad()
            self._switch_status(self._UPDATING)
            self.feature_optimizer.zero_grad()
            self._local_features.backward(self._feature_grad)
            self.feature_optimizer.step()

        self._switch_status(self._PERSISTING)
        self._save_model()
        self._save_runtime_context()

        self._switch_status(self._TESTING)
        self._wait_for_testing_round()

        self._switch_status(self._CLOSING_ROUND)
        self._wait_for_closing_round()

        self.push_log(f'ID: {self.id} finished training task of round {self.current_round}.')

    def _wait_for_starting_round(self):
        """Wait for starting a new round of training ..."""
        self.push_log(f'Waiting for training of round {self.current_round} begin ...')
        for _event in self.contractor.contract_events():
            if isinstance(_event, StartRoundEvent):
                assert (
                    _event.round == self.current_round
                ), f'Lost synchronization, host: {_event.round}; local: {self.current_round}.'
                self.push_log(f'Training of round {self.current_round} begins.')
                return
            elif isinstance(_event, FailTaskEvent):
                raise TaskFailed('Aborted by host.')
            elif isinstance(_event, ResetRoundEvent):
                raise ResetRound()

    def _send_feature(self):
        """Send local features of a batch of data to the host."""
        self.push_log('Waiting for sending features ...')
        for _event in self.contractor.contract_events():
            if isinstance(_event, ReadyForFusionEvent):
                assert (
                    _event.round == self.current_round
                ), f'Lost synchronization, host: {_event.round}; local: {self.current_round}.'
                break
            elif isinstance(_event, FailTaskEvent):
                raise TaskFailed('Aborted by host.')
            elif isinstance(_event, ResetRoundEvent):
                raise ResetRound()

        self.push_log('Begin to send features.')
        with TemporaryFile() as tf:
            torch.save({self.feature_key: self._local_features}, tf)
            tf.seek(0)
            self.data_channel.send_stream(source=self.id,
                                          target=self.host,
                                          data_stream=tf.read())
        self.push_log('Sending features complete.')

    def _wait_for_feature_grad(self):
        """Wait for cipher grad of feature model output."""
        def reset_handler(event: ContractEvent):
            if isinstance(event, ResetRoundEvent):
                raise ResetRound()

        self.push_log('Waiting for cipher grad of feature model output ...')
        _, stream = self.data_channel.receive_stream(
            receiver=self.id,
            complementary_handler=reset_handler,
            source=self.host
        )
        buffer = io.BytesIO(stream)
        self._feature_grad = torch.load(buffer)
        self.push_log('Received and decrypted cipher grad of feature model output.')

    def _save_model(self):
        """Save latest model state."""
        with open(self._feature_ckpt_file, 'wb') as f:
            torch.save(self.feature_model.state_dict(), f)
        self.push_log('Saved latest parameters locally.')

    def _save_runtime_context(self):
        """Save runtime context information in case of restoring."""
        context_info = {
            'feature_ckpt_file': self._feature_ckpt_file
        }
        with open(self._context_file, 'w') as f:
            f.write(json.dumps(context_info, ensure_ascii=False))
        self.push_log('Saved latest runtime context.')

    def _wait_for_testing_round(self):
        """Wait for handle a round of testing."""
        self.push_log('Waiting for start a round of testing ...')
        for _event in self.contractor.contract_events():
            if isinstance(_event, StartTestRoundEvent):
                assert (
                    _event.round == self.current_round
                ), f'Lost synchronization, host: {_event.round}; local: {self.current_round}.'

                self.feature_model.eval()
                features = {
                    self.feature_key: list(self.iterate_test_feature(self.feature_model,
                                                                     self.test_ids))
                }
                with TemporaryFile() as tf:
                    torch.save(features, tf)
                    tf.seek(0)
                    self.data_channel.send_stream(source=self.id,
                                                  target=self.host,
                                                  data_stream=tf.read())
                self.push_log('Sent all batches of feature to the host.')

            elif isinstance(_event, CloseTestRoundEvent):
                self.push_log('Skipped or closed a round of testing.')
                return
            elif isinstance(_event, FailTaskEvent):
                raise TaskFailed('Aborted by host.')
            elif isinstance(_event, ResetRoundEvent):
                raise ResetRound()

    def _wait_for_closing_round(self):
        """Wait for closing current round of training."""
        self.push_log(f'Waiting for closing signal of training round {self.current_round} ...')
        for _event in self.contractor.contract_events():
            if isinstance(_event, CloseRoundEvent):
                if _event.round != self.current_round:
                    continue
                return
            elif isinstance(_event, CompleteTaskEvent):
                raise TaskComplete()
            elif isinstance(_event, ResetRoundEvent):
                raise ResetRound()

    def _close_task(self, is_succ: bool = True):
        """Close the task and upload the final parameters."""
        self.push_log(f'Closing task {self.task_id} ...')

        self._switch_status(self._FINISHING)
        if is_succ:
            model_file_path = self._prepare_task_output()
            self.contractor.upload_metric_report(receivers=self.contractor.EVERYONE)
            self.contractor.upload_model(receivers=[self.id],
                                         model_file=model_file_path)
            self.contractor.notify_collaborator_complete(peer_id=self.id, host=self.host)
            self.push_log(f'Task {self.task_id} complete. Byebye!')
        else:
            self.push_log(f'Task {self.task_id} failed. Byebye!')

    def _prepare_task_output(self) -> Tuple[str, str]:
        """Generate final output files of the task.

        :return
            Local paths of the model file.
        """
        self.push_log('Generating task achievement files ...')

        # torch.jit doesn't work with a TemporaryFile
        feature_model_file = os.path.join(self._result_dir,
                                          f'feature_model_{self.feature_key}.pt')
        with open(feature_model_file, 'wb') as f:
            torch.save(self.feature_model.state_dict(), f)
        model_file_path = os.path.abspath(feature_model_file)

        self.push_log('Task achievement files are ready.')
        return model_file_path
