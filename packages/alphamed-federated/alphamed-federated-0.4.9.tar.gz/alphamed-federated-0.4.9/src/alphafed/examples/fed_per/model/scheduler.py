"""HomoFedPer Scheduler."""
import io
import json
import os
import sys
import traceback
from abc import abstractmethod
from typing import Dict, Tuple, final
from zipfile import ZipFile

import torch
from torch.nn import Module, Sequential

from alphafed import logger
from alphafed.fed_avg import FedAvgScheduler
from alphafed.fed_avg.fed_avg import ResetRound, SkipRound
from alphafed.scheduler import TaskComplete, TaskFailed

from .contractor import CollaboratorCompleteEvent, HomoFedPerContractor


class HomoFedPerScheduler(FedAvgScheduler):

    _FINISHED = 'finished'

    def __init__(self,
                 max_rounds: int = 0,
                 merge_epochs: int = 1,
                 calculation_timeout: int = 300,
                 schedule_timeout: int = 30,
                 log_rounds: int = 0):
        super().__init__(max_rounds=max_rounds,
                         merge_epochs=merge_epochs,
                         calculation_timeout=calculation_timeout,
                         schedule_timeout=schedule_timeout,
                         log_rounds=log_rounds,
                         involve_aggregator=False)

    def _init_contractor(self) -> HomoFedPerContractor:
        return HomoFedPerContractor(task_id=self.task_id)

    @abstractmethod
    def build_global_model(self) -> Module:
        """Return a global model object which will be used for training."""

    @final
    @property
    def global_model(self) -> Module:
        """Get the model object which is used for training."""
        if not hasattr(self, '_global_model'):
            self._global_model = self.build_global_model()
        return self._global_model

    @abstractmethod
    def build_personalized_layer(self) -> Module:
        """Return a personalized layer object which will be used for training."""

    @final
    @property
    def personalized_layer(self) -> Module:
        """Get the model object which is used for training."""
        if not hasattr(self, '_personalized_layer'):
            self._personalized_layer = self.build_personalized_layer()
        return self._personalized_layer

    @final
    def build_model(self) -> Module:
        if self.is_aggregator:
            return self.global_model
        else:
            return Sequential(
                self.global_model,
                self.personalized_layer
            )

    def state_dict(self) -> Dict[str, torch.Tensor]:
        return self.global_model.state_dict()

    def load_state_dict(self, state_dict: Dict[str, torch.Tensor]):
        return self.global_model.load_state_dict(state_dict)

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

    def _recover_progress(self):
        """Try to recover and continue from last running."""
        if not os.path.isfile(self._context_file):
            raise TaskFailed('Failed to recover progress: missing cached context.')

        with open(self._context_file, 'r') as f:
            context_info: dict = json.load(f)
        round = context_info.get('round')
        ckpt_file = context_info.get('ckpt_file')
        assert round and isinstance(round, int) and round > 0, f'Invalid round: {round} .'
        assert ckpt_file and isinstance(ckpt_file, str), f'Invalid ckpt_file: {ckpt_file} .'
        if not os.path.isfile(ckpt_file):
            raise TaskFailed('Failed to recover progress: missing checkpoint parameters.')

        self.current_round = round
        with open(ckpt_file, 'rb') as f:
            state_dict = torch.load(f)
            if self.is_aggregator:
                self.global_model.load_state_dict(state_dict)
            else:
                self.model.load_state_dict(state_dict)

    def _save_model(self):
        """Save latest model state."""
        with open(self._ckpt_file, 'wb') as f:
            if self.is_aggregator:
                torch.save(self.global_model.state_dict(), f)
            else:
                torch.save(self.model.state_dict(), f)
        self.push_log('Saved latest parameters locally.')

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

                    self._switch_status(self._IN_A_ROUND)
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
                        self._close_task()  # 聚合方退出

        except TaskComplete:
            self._close_task()  # 数据持有方退出
            logger.info('training task complete')

    def _check_and_run_test(self):
        """Run test if match configured conditions."""
        if self.is_aggregator:
            return
        if (
            self.current_round == 1
            or (self.log_rounds > 0 and self.current_round % self.log_rounds == 0)
            or self.current_round == self.max_rounds
        ):
            self.push_log('Begin to make a model test.')
            self.run_test()
            self.push_log('Finished a round of test.')

    def _close_task(self):
        """Close the FedAvg calculation.

        As an aggregator, broadcasts the finish task event to all participants,
        uploads the final parameters and tells L1 task manager the task is complete.
        As a participant, do nothing.
        """
        self.push_log(f'Closing task {self.task_id} ...')
        self.contractor: HomoFedPerContractor
        if self.is_aggregator:
            # 任务成功结束，聚合方处理
            self.contractor.finish_task()
            _, model_file_path = self._prepare_task_output()
            # 报告上传和模型上传
            self.contractor.upload_metric_report(receivers=[self.id])
            self.contractor.upload_model(receivers=[self.id],
                                         model_file=model_file_path)
            self._wait_for_all_complete()
            self.contractor.notify_task_completion(result=True)

        else:  # 数据持有方
            report_file_path, model_file_path = self._prepare_task_output()
            # 报告上传和模型上传
            self.contractor.upload_metric_report(receivers=[self.id],
                                                 report_file=report_file_path)
            self.contractor.upload_model(receivers=[self.id],
                                         model_file=model_file_path)
            self.contractor.notify_collaborator_complete(peer_id=self.id, host=self._aggregator)
        self._switch_status(self._FINISHED)
        self.push_log(f'Task {self.task_id} closed. Byebye!')

    def _prepare_task_output(self) -> Tuple[str, str]:
        """Generate final output files of the task.

        Return:
            Local paths of the report file and model file.
        """
        self.push_log('Uploading task achievement and closing task ...')

        report_file_path = None
        if not self.is_aggregator:
            report_file = os.path.join(self._result_dir, "report.zip")
            with ZipFile(report_file, 'w') as report_zip:
                for path, _, filenames in os.walk(self._log_dir):
                    rel_dir = os.path.relpath(path=path, start=self._result_dir)
                    rel_dir = rel_dir.lstrip('.')  # ./file => file
                    for _file in filenames:
                        rel_path = os.path.join(rel_dir, _file)
                        report_zip.write(os.path.join(path, _file), rel_path)
            report_file_path = os.path.abspath(report_file)

        model_file = os.path.join(
            self._result_dir,
            "global_model.pt" if self.is_aggregator else "personalized_model.pt"
        )
        with open(model_file, 'wb') as f:
            torch.save(self.global_model.state_dict() if self.is_aggregator else self.model.state_dict(), f)
        model_file_path = os.path.abspath(model_file)

        self.push_log('Task achievement files are ready.')
        return report_file_path, model_file_path

    def _wait_for_all_complete(self):
        """Wait for all collaborators complete their tasks."""
        self.push_log('Waiting for all collaborators complete their tasks ...')
        results = {_peer_id: False for _peer_id in self.participants if _peer_id != self.id}
        for _event in self.contractor.contract_events():
            if isinstance(_event, CollaboratorCompleteEvent):
                results[_event.peer_id] = True
                if all(results.values()):
                    break
        self.push_log('All collaborators have completed their tasks.')

    def _run_as_data_owner(self):
        try:
            self._wait_for_starting_round()
            self._switch_status(self._UPDATING)
            self._wait_for_updating_model()
            self._save_model()
            self._switch_status(self._CALCULATING)
            self.push_log('Begin to run calculation ...')
            self._execute_training()
            self.push_log('Local calculation complete.')

            self._wait_for_uploading_model()
            buffer = io.BytesIO()
            torch.save(self.state_dict(), buffer)
            self.push_log('Pushing local update to the aggregator ...')
            self.data_channel.send_stream(source=self.id,
                                          target=self._aggregator,
                                          data_stream=buffer.getvalue())
            self.push_log('Successfully pushed local update to the aggregator.')

            self._check_and_run_test()

            self._switch_status(self._CLOSING_ROUND)
            self._wait_for_closing_round()
        except SkipRound:
            pass

        self.push_log(f'ID: {self.id} finished training task of round {self.current_round}.')
