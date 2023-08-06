"""HomoFedMD Scheduler."""

import io
import json
import os
import shutil
import sys
import traceback
from abc import abstractmethod
from typing import Any, List, Tuple, final
from zipfile import ZipFile

import torch
from torch import Tensor
from torch.nn import Module
from torch.optim import Optimizer
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from alphafed import logger
from alphafed.data_channel import SharedFileDataChannel
from alphafed.fs import get_result_dir, get_runtime_dir
from alphafed.scheduler import ConfigError, Scheduler, TaskComplete, TaskFailed

from .contractor import (CheckinEvent, CheckinResponseEvent, CloseRoundEvent,
                         FinishTaskEvent, HomoFedMDContractor,
                         PartnerCloseEvent, ResetRoundEvent,
                         RoundTrainFinishEvent, StartRoundEvent,
                         SyncStateEvent, SyncStateResponseEvent)


class AggregationError(Exception):
    ...


class SkipRound(Exception):
    ...


class ResetRound(Exception):
    ...


class HomoFedMDScheduler(Scheduler):

    _INIT = 'init'
    _GETHORING = 'gethoring'
    _READY = 'ready'
    _SYNCHRONIZING = 'synchronizing'
    _ROUND_START = 'round_start'
    _COLLECTING_LOGITS = 'collect_logits'
    _CALCULATING = 'calculating'
    _UPLOADING_LOGITS = 'upload_logits'
    _WAITING_FOR_GLOBAL_LOGITS = 'wait_4_global_logits'
    _DISTRIBUTE_LOGITS = 'dist_logits'
    _WAITING_FOR_TRAINING = 'wait_4_train'
    _ALIGNING = 'align'
    _FINE_TUNING = 'fine_tune'
    _CLOSING_ROUND = 'close_round'
    _PERSISTING = 'persisting'
    _FINISHING = 'finish'
    _WAITING_FOR_ALL_CLOSED = 'wait_4_all_close'
    _TESTING = 'test'

    def __init__(self,
                 max_rounds: int,
                 pretrain_public_epochs: int,
                 pretrain_private_epochs: int,
                 align_epochs: int,
                 fine_tune_epochs: int,
                 calculation_timeout: int = 300,
                 schedule_timeout: int = 30,
                 log_rounds: int = 0):
        """Init.

        Args:
            max_rounds:
                Maximal number of training rounds.
            pretrain_public_epochs:
                The number of epochs to pre-train on public dataset.
            pretrain_private_epochs:
                The number of epochs to pre-train on private dataset.
            align_epochs:
                The number of epochs to do alignment training on teacher's knowledge.
            fine_tune_epochs:
                The number of epochs to do fine-tune training on private dataset after alignment.
            calculation_timeout:
                Seconds to timeout for calculation in a round. Takeing off timeout
                by setting its value to 0.
            schedule_timeout:
                Seconds to timeout for process scheduling. Takeing off timeout
                by setting its value to 0.
            log_rounds:
                The number of rounds to run testing and log the result. Skip it
                by setting its value to 0.
        """
        super().__init__()
        self._switch_status(self._INIT)

        self.max_rounds = max_rounds
        self.pretrain_public_epochs = pretrain_public_epochs
        self.pretrain_private_epochs = pretrain_private_epochs
        self.align_epochs = align_epochs
        self.fine_tune_epochs = fine_tune_epochs
        self.calculation_timeout = calculation_timeout
        self.schedule_timeout = schedule_timeout
        self.log_rounds = log_rounds

        self._validate_config()
        self.current_round = 1

        self.participants: List[str] = []
        self.gethered: List[str] = []
        self.is_gathering_complete = False

    def _validate_config(self):
        if self.max_rounds <= 0:
            raise ConfigError('max_rounds must be a positive integer')
        if self.pretrain_public_epochs <= 0:
            raise ConfigError('pretrain_public_epochs must be a positive integer')
        if self.pretrain_private_epochs <= 0:
            raise ConfigError('pretrain_private_epochs must be a positive integer')
        if self.align_epochs <= 0:
            raise ConfigError('align_epochs must be a positive integer')
        if self.fine_tune_epochs <= 0:
            raise ConfigError('fine_tune_epochs must be a positive integer')

    @abstractmethod
    def build_model(self) -> Module:
        """Return a model object which will be used for training."""

    @final
    @property
    def model(self) -> Module:
        """Get the model object which is used for training."""
        if not hasattr(self, '_model'):
            self._model = self.build_model()
        return self._model

    @abstractmethod
    def build_optimizer(self, model: Module) -> Optimizer:
        """Return a optimizer object which will be used for training.

        Args:
            model:
                The model object which is used for training.
        """

    @final
    @property
    def optimizer(self) -> Optimizer:
        """Get the optimizer object which is used for training."""
        if not hasattr(self, '_optimizer'):
            self._optimizer = self.build_optimizer(model=self.model)
        return self._optimizer

    @abstractmethod
    def build_public_train_dataloader(self) -> DataLoader:
        """Define the public dataset training dataloader.

        You can transform the dataset, do some preprocess to the dataset.

        Return:
            training dataloader
        """

    @final
    @property
    def public_train_loader(self) -> DataLoader:
        """Get the training dataloader object."""
        if not hasattr(self, '_public_train_loader'):
            self._public_train_loader = self.build_public_train_dataloader()
        return self._public_train_loader

    @abstractmethod
    def build_private_train_dataloader(self) -> DataLoader:
        """Define the private dataset training dataloader.

        You can transform the dataset, do some preprocess to the dataset.

        Return:
            training dataloader
        """

    @final
    @property
    def private_train_loader(self) -> DataLoader:
        """Get the training dataloader object."""
        if not hasattr(self, '_private_train_loader'):
            self._private_train_loader = self.build_private_train_dataloader()
        return self._private_train_loader

    @abstractmethod
    def build_test_dataloader(self) -> DataLoader:
        """Define the testing dataloader.

        You can transform the dataset, do some preprocess to the dataset. If you do not
        want to do testing after training, simply make it return None.

        Args:
            dataset:
                training dataset
        Return:
            testing dataloader
        """

    @final
    @property
    def test_loader(self) -> DataLoader:
        """Get the testing dataloader object."""
        if not hasattr(self, '_test_loader'):
            self._test_loader = self.build_test_dataloader()
        return self._test_loader

    @abstractmethod
    def pretrain_an_epoch_on_public_data(self):
        """One epoch of pretraining process on public dataset."""

    @abstractmethod
    def pretrain_an_epoch_on_private_data(self):
        """One epoch of pretraining process on private dataset."""

    @abstractmethod
    def calc_local_logits(self) -> Tensor:
        """Get local classification logits.

        Return values of model output on public dataset by default.

        Return:
            List[Tensor], The flatterned list of logits result.
        """

    @abstractmethod
    def align_train_an_epoch(self, global_logits: Tensor):
        """Run an epoch of alignment training."""

    @abstractmethod
    def fine_tune_an_epoch(self):
        """Run an epoch of fine tune training."""

    @abstractmethod
    def run_test(self) -> Any:
        """Define the testing steps.

        If you do not want to do testing after training, simply make it pass.
        """

    def _init_contractor(self) -> HomoFedMDContractor:
        return HomoFedMDContractor(task_id=self.task_id)

    def _setup_context(self, id: str, task_id: str, is_initiator: bool = False):
        assert id, 'must specify a unique id for every participant'
        assert task_id, 'must specify a task_id for every participant'

        self.id = id
        self.task_id = task_id
        self._runtime_dir = get_runtime_dir(self.task_id)
        self._context_file = os.path.join(self._runtime_dir, ".context.json")
        self._checkpoint_dir = os.path.join(self._runtime_dir, 'checkpoint')
        self._ckpt_file = os.path.join(self._checkpoint_dir, "model_ckpt.pt")
        self._result_dir = get_result_dir(self.task_id)
        self._log_dir = os.path.join(self._result_dir, 'tb_logs')
        self.tb_writer = SummaryWriter(log_dir=self._log_dir)

        self.is_initiator = is_initiator
        self.is_aggregator = self.is_initiator

        self.contractor = self._init_contractor()
        self.data_channel = SharedFileDataChannel(self.contractor)
        self.model
        self.optimizer

        if self.is_initiator:
            self.participants = self.contractor.query_nodes()
            if len(self.participants) < 2:
                raise TaskFailed('Failed to get participants list.')

        self.push_log(message='Begin to validate local context.')

    def _run(self, id: str, task_id: str, is_initiator: bool = False, recover: bool = False):
        self._setup_context(id=id, task_id=task_id, is_initiator=is_initiator)
        self.push_log(message='Local context is ready.')
        try:
            if self.is_aggregator and recover:
                self._recover_progress()
            else:
                self._clean_progress()
            if not self.is_aggregator:
                for _ in range(self.pretrain_public_epochs):
                    self.pretrain_an_epoch_on_public_data()
                for _ in range(self.pretrain_private_epochs):
                    self.pretrain_an_epoch_on_private_data()
            self._launch_process()
        except Exception:
            err_stack = '\n'.join(traceback.format_exception(*sys.exc_info()))
            self.push_log(err_stack)

    def _recover_progress(self):
        """Try to recover and continue from last running."""
        if not os.path.isfile(self._context_file):
            raise TaskFailed('Failed to recover progress: missing cached context.')

        if self.is_aggregator:
            with open(self._context_file, 'r') as f:
                context_info: dict = json.load(f)
            round = context_info.get('round')
            assert round and isinstance(round, int) and round > 0, f'Invalid round: {round} .'
            self.current_round = round
            
        else:
            with open(self._context_file, 'r') as f:
                context_info: dict = json.load(f)
            ckpt_file = context_info.get('ckpt_file')
            assert ckpt_file and isinstance(ckpt_file, str), f'Invalid ckpt_file: {ckpt_file} .'
            if not os.path.isfile(ckpt_file):
                raise TaskFailed('Failed to recover progress: missing checkpoint parameters.')
            with open(ckpt_file, 'rb') as f:
                state_dict = torch.load(f)
                self.model.load_state_dict(state_dict)

    def _clean_progress(self):
        """Clean existing progress data."""
        shutil.rmtree(self._runtime_dir, ignore_errors=True)
        shutil.rmtree(self._result_dir, ignore_errors=True)
        os.makedirs(self._runtime_dir, exist_ok=True)
        os.makedirs(self._checkpoint_dir, exist_ok=True)
        os.makedirs(self._result_dir, exist_ok=True)
        os.makedirs(self._log_dir, exist_ok=True)

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

                    self._switch_status(self._ROUND_START)
                    self._run_a_round()
                    self._persistent_running_context()
                    self._switch_status(self._READY)
                except ResetRound:
                    self.push_log('WARNING: Reset runtime context, there might be an error raised.')
                    self._switch_status(self._READY)
                    continue

                if self.is_aggregator:
                    is_finished = self.is_task_finished()
                    self._switch_status(self._READY)
                    self.current_round += 1
                    if is_finished:
                        self.push_log(f'Obtained the final results of task {self.task_id}')
                        self._switch_status(self._FINISHING)
                        self._close_task()

        except TaskComplete:
            logger.info('training task complete')

    def _check_in(self):
        """Check in task and get ready.

        As an initiator (and default the first aggregator), records each participants
        and launches election or training process accordingly.
        As a participant, checkins and gets ready for election or training.
        """
        if self.is_initiator:
            self.push_log('Waiting for participants taking part in ...')
            self._wait_for_gathering()
            self.is_gathering_complete = True
        else:
            is_checked_in = False
            # the aggregator may be in special state so can not response
            # correctly nor in time, then retry periodically
            self.push_log('Checking in the task ...')
            while not is_checked_in:
                is_checked_in = self._check_in_task()
            self.push_log(f'Node {self.id} have taken part in the task.')

    def _wait_for_gathering(self):
        """Wait for participants gethering."""
        logger.debug('_wait_for_gathering ...')
        for _event in self.contractor.contract_events():
            if isinstance(_event, CheckinEvent):
                self._handle_check_in(_event)
                if len(self.gethered) == len(self.participants) - 1:
                    return

    def _handle_check_in(self, _event: CheckinEvent):
        if _event.peer_id not in self.gethered:
            self.gethered.append(_event.peer_id)
            self.push_log(f'Welcome a new participant ID: {_event.peer_id}.')
            self.push_log(f'There are {len(self.gethered) + 1} participants now.')
        self.contractor.respond_check_in(round=self.current_round,
                                         aggregator=self.id,
                                         nonce=_event.nonce,
                                         requester_id=_event.peer_id)
        if self.is_gathering_complete:
            self.contractor.sync_state(round=self.current_round, aggregator=self.id)

    def _check_in_task(self) -> bool:
        """Try to check in the task."""
        nonce = self.contractor.checkin(peer_id=self.id)
        return self._wait_for_check_in_response(nonce=nonce,
                                                timeout=self.schedule_timeout)

    def _wait_for_check_in_response(self, nonce: str, timeout: int = 0) -> bool:
        """Wait for checkin response.

        Return True if received response successfully otherwise False.
        """
        logger.debug('_wait_for_check_in_response ...')
        for _event in self.contractor.contract_events(timeout=timeout):
            if isinstance(_event, CheckinResponseEvent):
                if _event.nonce != nonce:
                    continue
                self.current_round = _event.round
                return True
            elif isinstance(_event, FinishTaskEvent):
                raise TaskComplete()
        return False

    def _sync_state(self):
        """Synchronize state before each round, so it's easier to manage the process.

        As an aggregator, iterates round, broadcasts and resets context of the new round.
        As a participant, synchronizes state and gives a response.
        """
        self.push_log('Synchronizing round state ...')
        if self.is_aggregator:
            self.push_log(f'Initiate state synchronization of round {self.current_round}.')
            self.contractor.sync_state(round=self.current_round, aggregator=self.id)
            self._wait_for_sync_response()
        else:
            self._wait_for_sync_state()
        self.push_log(f'Successfully synchronized state in round {self.current_round}')

    def _wait_for_sync_response(self):
        """Wait for participants' synchronizing state response."""
        self.push_log('Waiting for synchronization responses ...')
        synced = set()
        for _event in self.contractor.contract_events(timeout=0):
            if isinstance(_event, SyncStateResponseEvent):
                if _event.round != self.current_round:
                    continue
                synced.add(_event.peer_id)
                self.push_log(f'Successfully synchronized state with ID: {_event.peer_id}.')
                self.push_log(f'Successfully synchronized with {len(synced)} participants.')
                if len(synced) == len(self.gethered):
                    return

            elif isinstance(_event, CheckinEvent):
                self._handle_check_in(_event)

    def _wait_for_sync_state(self, timeout: int = 0) -> bool:
        """Wait for synchronising latest task state.

        Return True if synchronising successfully otherwise False.
        """
        self.push_log('Waiting for synchronizing state with the aggregator ...')
        for _event in self.contractor.contract_events(timeout=timeout):
            if isinstance(_event, SyncStateEvent):
                self.current_round = _event.round
                self.contractor.respond_sync_state(round=self.current_round,
                                                   peer_id=self.id,
                                                   aggregator=_event.aggregator)
                self.push_log('Successfully synchronized state with the aggregator.')
                return
            elif isinstance(_event, FinishTaskEvent):
                self._close_task()
                raise TaskComplete()

    def _run_a_round(self):
        """Perform a round of FedAvg calculation.

        As an aggregator, selects a part of participants as actual calculators
        in the round, distributes latest parameters to them, collects update and
        makes aggregation.
        As a participant, if is selected as a calculator, calculates and uploads
        parameter update.
        """
        if self.is_aggregator:
            try:
                self._run_as_aggregator()
            except AggregationError as err:
                err_stack = '\n'.join(traceback.format_exception(*sys.exc_info()))
                self.push_log(err_stack)
                self.contractor.reset_round()
                raise ResetRound(err)
        else:
            self._run_as_data_owner()

    def _run_as_aggregator(self):
        self._start_round()
        self._switch_status(self._COLLECTING_LOGITS)
        local_logits = self._collecting_local_logits()
        global_logits = torch.stack(local_logits).mean(axis=0)
        self._switch_status(self._DISTRIBUTE_LOGITS)
        self._distribute_global_logits(global_logits)
        self._switch_status(self._WAITING_FOR_TRAINING)
        self._wait_for_training()
        self._switch_status(self._CLOSING_ROUND)
        self._close_round()

    def _start_round(self):
        """Prepare and start calculation of a round."""
        self.push_log(f'Begin the training of round {self.current_round}.')
        self.contractor.start_round(round=self.current_round,
                                    calculators=self.gethered,
                                    aggregator=self.id)
        self.push_log(f'Calculation of round {self.current_round} is started.')

    def _collecting_local_logits(self) -> List[Tensor]:
        """Collect all local classification logits of public dataset from data owners."""
        self.push_log('Collecting local logits ...')
        local_logits_result = self.data_channel.batch_receive_stream(
            receiver=self.id,
            source_list=self.gethered,
            timeout=self.calculation_timeout
        )
        local_logits = []
        for _logits_stream in local_logits_result.values():
            buffer = io.BytesIO(_logits_stream)
            _logits = torch.load(buffer)
            local_logits.append(_logits)

        return local_logits

    def _distribute_global_logits(self, global_logits: Tensor):
        """Distribute global classification logits of public dataset to data owners."""
        self.push_log('Distributing global logits ...')
        buffer = io.BytesIO()
        torch.save(global_logits, buffer)
        results = {_target: False for _target in self.gethered}
        accept_list = self.data_channel.batch_send_stream(source=self.id,
                                                          target=list(results.keys()),
                                                          data_stream=buffer.getvalue())
        self.push_log(f'Successfully distributed global logits to: {accept_list}')
        if len(results.keys()) != len(accept_list):
            reject_list = [_target for _target in results.keys()
                           if _target not in accept_list]
            self.push_log(f'Failed to distribute global logits to: {reject_list}')
        results.update({_target: True for _target in accept_list})

        if not all(results.values()):
            self.push_log('Task failed because not all calculators received global logits successfully.')
            raise AggregationError(f'Distributing global logits failed: `{results}`')
        self.push_log(f'Distributed global logits to {sum(results.values())} calculators.')

    def _wait_for_training(self):
        """Wait for all data owners finishing their alignment and fine-tune training."""
        self.push_log("Waiting for all data owners finishing their alignment and fine-tune training ...")
        results = {_target: False for _target in self.gethered}
        for _event in self.contractor.contract_events():
            if isinstance(_event, RoundTrainFinishEvent) and _event.peer_id in self.gethered:
                results[_event.peer_id] = True
            if all(results.values()):
                break
        self.push_log('All data owners finished their alignment and fine-tune training.')

    def _close_round(self):
        """Close current round when finished."""
        self.contractor.close_round(round=self.current_round)
        self.push_log(f'The training of Round {self.current_round} complete.')

    def _run_as_data_owner(self):
        try:
            self._wait_for_starting_round()
            self._switch_status(self._CALCULATING)
            self.push_log('Begin to run calculation ...')
            logits = self.calc_local_logits()
            self._switch_status(self._UPLOADING_LOGITS)
            self._send_local_logits(logits)
            self._switch_status(self._WAITING_FOR_GLOBAL_LOGITS)
            global_logits = self._wait_for_global_logits()
            self._switch_status(self._ALIGNING)
            for _ in range(self.align_epochs):
                self.align_train_an_epoch(global_logits)
            self._switch_status(self._FINE_TUNING)
            for _ in range(self.fine_tune_epochs):
                self.fine_tune_an_epoch()
            self._switch_status(self._CLOSING_ROUND)
            self._wait_for_closing_round()
            self._switch_status(self._TESTING)
            self._check_and_run_test()
        except SkipRound:
            pass

        self.push_log(f'ID: {self.id} finished training task of round {self.current_round}.')

    def _wait_for_starting_round(self):
        """Wait for starting a new round of training."""
        self.push_log(f'Waiting for training of round {self.current_round} begin ...')
        for _event in self.contractor.contract_events():
            if isinstance(_event, StartRoundEvent):
                if _event.round != self.current_round:
                    continue
                if self.id not in _event.calculators:
                    raise SkipRound()
                self._aggregator = _event.aggregator
                self.push_log(f'Training of round {self.current_round} begins.')
                return
            elif isinstance(_event, FinishTaskEvent):
                raise TaskComplete()
            elif isinstance(_event, ResetRoundEvent):
                raise ResetRound()
            
    def _send_local_logits(self, logits: Tensor):
        self.push_log('Sending local logits to aggregator ....')
        buffer = io.BytesIO()
        torch.save(logits, buffer)
        self.data_channel.send_stream(source=self.id,
                                      target=self._aggregator,
                                      data_stream=buffer.getvalue())
        self.push_log('Senting local logits complete.')

    def _wait_for_global_logits(self) -> Tensor:
        self.push_log('Waiting for global logits from aggregator ....')
        _, logits = self.data_channel.receive_stream(receiver=self.id,
                                                     source=self._aggregator)
        buffer = io.BytesIO(logits)
        global_logits = torch.load(buffer)
        return global_logits

    def _save_model(self):
        """Save latest model state."""
        with open(self._ckpt_file, 'wb') as f:
            torch.save(self.model.state_dict(), f)
        self.push_log('Saved latest parameters locally.')

    def _wait_for_closing_round(self):
        """Wait for closing current round of training."""
        self.push_log(f'Waiting for closing signal of training round {self.current_round} ...')
        self.contractor.notice_train_complete(round=self.current_round,
                                              peer_id=self.id,
                                              aggregator=self._aggregator)
        for _event in self.contractor.contract_events():
            if isinstance(_event, CloseRoundEvent):
                if _event.round != self.current_round:
                    continue
                return
            elif isinstance(_event, FinishTaskEvent):
                raise TaskComplete()
            elif isinstance(_event, ResetRoundEvent):
                raise ResetRound()

    def _check_and_run_test(self):
        """Run test if match configured conditions."""
        if (
            self.current_round == 1
            or (self.log_rounds > 0 and self.current_round % self.log_rounds == 0)
            or self.current_round == self.max_rounds
        ):
            self.push_log('Begin to make a model test.')
            self.run_test()
            self.push_log('Finished a round of test.')

    def is_task_finished(self) -> bool:
        """By default true if reach the max rounds configured."""
        return self.current_round >= self.max_rounds

    def _persistent_running_context(self):
        self._switch_status(self._PERSISTING)
        if not self.is_aggregator:
            self._save_model()
        self._save_runtime_context()

    def _save_runtime_context(self):
        """Save runtime context information in case of restoring."""
        context_info = {
            'round': self.current_round,
            'ckpt_file': '' if self.is_aggregator else self._ckpt_file
        }
        with open(self._context_file, 'w') as f:
            f.write(json.dumps(context_info, ensure_ascii=False))
        self.push_log('Saved latest runtime context.')

    def _close_task(self):
        """Close the FedAvg calculation.

        As an aggregator, broadcasts the finish task event to all participants,
        uploads the final parameters and tells L1 task manager the task is complete.
        As a participant, do nothing.
        """
        self.push_log(f'Closing task {self.task_id} ...')
        if self.is_aggregator:
            self.contractor.finish_task()
            self._switch_status(self._WAITING_FOR_ALL_CLOSED)
            results = {_target: False for _target in self.gethered}
            for _event in self.contractor.contract_events():
                if isinstance(_event, PartnerCloseEvent) and _event.peer_id in self.gethered:
                    results[_event.peer_id] = True
                if all(results.values()):
                    break
            self.contractor.upload_metric_report(receivers=[self.id])
            self.contractor.upload_model(receivers=[self.id])
            self.contractor.notify_task_completion(result=True)

        else:
            report_file_path, model_file_path = self._prepare_task_output()
            # 报告上传和模型上传
            self.contractor.upload_metric_report(receivers=[self.id],
                                                 report_file=report_file_path)
            self.contractor.upload_model(receivers=[self.id],
                                         model_file=model_file_path)
            self.contractor.close_partner(peer_id=self.id, aggregator=self._aggregator)

        self.push_log(f'Task {self.task_id} closed. Byebye!')

    def _prepare_task_output(self) -> Tuple[str, str]:
        """Generate final output files of the task.

        Return:
            Local paths of the report file and model file.
        """
        self.push_log('Uploading task achievement and closing task ...')
        if self.is_aggregator:
            return None, None

        report_file = os.path.join(self._result_dir, "report.zip")
        with ZipFile(report_file, 'w') as report_zip:
            for path, _, filenames in os.walk(self._log_dir):
                rel_dir = os.path.relpath(path=path, start=self._result_dir)
                rel_dir = rel_dir.lstrip('.')  # ./file => file
                for _file in filenames:
                    rel_path = os.path.join(rel_dir, _file)
                    report_zip.write(os.path.join(path, _file), rel_path)
        report_file_path = os.path.abspath(report_file)

        model_file = os.path.join(self._result_dir, "model.pt")
        with open(model_file, 'wb') as f:
            torch.save(self.model.state_dict(), f)
        model_file_path = os.path.abspath(model_file)

        self.push_log('Task achievement files are ready.')
        return report_file_path, model_file_path
