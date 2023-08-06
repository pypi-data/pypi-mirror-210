"""DP FedAvg scheduler.

Reference: https://arxiv.org/abs/1710.06963
"""


import io
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from math import sqrt
from typing import Dict, final

import torch

from ..scheduler import ConfigError
from .dp_contractor import DPCheckinEvent, DPFedAvgContractor
from .fed_avg import AggregationError, FedAvgScheduler

__all__ = ['DPFedAvgScheduler']


class DPFedAvgScheduler(FedAvgScheduler, metaclass=ABCMeta):
    """Implementation of DPFedAvg."""

    def __init__(self,
                 w_cap: int,
                 q: float,
                 S: float,
                 z: float,
                 max_rounds: int = 0,
                 merge_epochs: int = 1,
                 calculation_timeout: int = 300,
                 schedule_timeout: int = 30,
                 log_rounds: int = 0,
                 involve_aggregator: bool = False):
        """Init.

        :args
            :w_hat
                Per-user example cap. (See the paper.)
            :q
                User selection probability between (0, 1]. (See the paper.)
            :S
                Sensitivity bound. (See the paper.)
            :z
                Noise scale. (See the paper.)
            :merge_epochs
                The number of epochs to run before aggregation is performed.
            :calculation_timeout
                Seconds to timeout for calculation in a round. Takeing off timeout
                by setting its value to 0.
            :schedule_timeout
                Seconds to timeout for process scheduling. Takeing off timeout
                by setting its value to 0.
            :log_rounds
                The number of rounds to run testing and log the result. Skip it
                by setting its value to 0.
        """
        super().__init__(max_rounds=max_rounds,
                         merge_epochs=merge_epochs,
                         calculation_timeout=calculation_timeout,
                         schedule_timeout=schedule_timeout,
                         log_rounds=log_rounds,
                         involve_aggregator=involve_aggregator)
        self.w_cap = w_cap
        self.q = float(q)
        self.S = float(S)
        self.z = float(z)

        self._theta_0 = None
        self._w_ks: Dict[str, float] = {}

        self._validate_dp_config()

    def _validate_dp_config(self):
        if not isinstance(self.w_cap, int) or self.w_cap < 1:
            raise ConfigError('Per-user example cap must be a positive interger.')
        if not isinstance(self.q, float) or self.q <= 0 or self.q > 1:
            raise ConfigError('Probability q must in range (0, 1].')
        if not isinstance(self.S, float) or self.S < 0:
            raise ConfigError('Sensitivity must be greater than zero.')
        if not isinstance(self.z, float) or self.z < 0:
            raise ConfigError('Noise scale must be greater than zero.')

    def _setup_context(self, id: str, task_id: str, is_initiator: bool = False):
        super()._setup_context(id, task_id, is_initiator)
        if self.involve_aggregator:
            self._w_ks[self.id] = self._calc_w_k(len(self.train_loader.dataset))
        self.contractor = DPFedAvgContractor(task_id=self.task_id)

    def _calc_w_k(self, n_k: int) -> float:
        return min(float(n_k) / self.w_cap, 1.0)

    @property
    def W(self) -> float:
        return sum(self._w_ks.values())

    @abstractmethod
    def train_a_batch(self, *batch_train_data):
        """Train for a single batch of data in an epoch.

        :args
            :batch_train_data
                A list of data in a batch from training data loader.
        """

    def _handle_check_in(self, _event: DPCheckinEvent):
        if _event.peer_id not in self.gethered:
            self.gethered.append(_event.peer_id)
            self._w_ks[_event.peer_id] = self._calc_w_k(_event.n_k)
            self.push_log(f'Welcome a new participant ID: {_event.peer_id}.')
            self.push_log(f'There are {len(self.gethered) + 1} participants now.')
        self.contractor.respond_check_in(round=self.current_round,
                                         aggregator=self.id,
                                         nonce=_event.nonce,
                                         requester_id=_event.peer_id)

    def _check_in_task(self) -> bool:
        """Try to check in the task."""
        nonce = self.contractor.checkin(peer_id=self.id, n_k=len(self.train_loader.dataset))
        return self._wait_for_check_in_response(nonce=nonce, timeout=self.schedule_timeout)

    def _execute_training(self):
        self.model.train()
        self._theta_0 = deepcopy(tuple(self.model.parameters()))
        for _ in range(self.merge_epochs):
            for batch_data in self.train_loader:
                self.train_a_batch(*batch_data)
                self._per_layer_clip()

    @final
    def train_an_epoch(self):
        raise NotImplementedError()

    @torch.no_grad()
    def _per_layer_clip(self):
        m = sum(1 for _param in self.model.parameters() if _param.requires_grad)
        s_layer = self.S / sqrt(m)
        for _param, _param_0 in zip(self.model.parameters(), self._theta_0):
            _param: torch.nn.Parameter
            if not _param.requires_grad:
                continue
            delta = _param - _param_0
            delta = self._pi(delta=delta, S=s_layer)
            _param.zero_().add_(_param_0 + delta)

    def _pi(self, delta: float, S: float) -> float:
        delta_n2 = torch.linalg.norm(delta)
        return delta * min(1, S / delta_n2)

    def _process_aggregation(self):
        self._switch_status(self._WAIT_FOR_AGGR)
        self.contractor.notify_ready_for_aggregation(round=self.current_round)
        self.push_log('Now waiting for executing calculation ...')

        state_dicts = self._wait_for_calculation()
        if len(state_dicts) < len(self.gethered):
            self.push_log('Task failed because of too few calculation results gathered.')
            raise AggregationError(f'Too few results gathered: {len(state_dicts)} copies.')
        self.push_log(f'Received {len(state_dicts)} copies of calculation results.')

        self._switch_status(self._AGGREGATING)
        self.push_log('Begin to aggregate and update parameters.')

        with torch.no_grad():
            state_dict_0 = self.model.state_dict()
            _trans_model = self.build_model()
            _trans_model.load_state_dict(state_dict_0)
            self._theta_0 = deepcopy(tuple(_trans_model.parameters()))

            accum_delta = tuple(torch.zeros(_param.size()) for _param in self._theta_0)
            for _peer_id, _state_dict in state_dicts.items():
                if _peer_id not in self._w_ks:
                    raise AggregationError(f'The w_s value of ID: {_peer_id} is lost.')
                _trans_model.load_state_dict(_state_dict)
                w_k = self._w_ks[_peer_id]
                for _param, _param_0 in zip(_trans_model.parameters(), self._theta_0):
                    if not _param.requires_grad:
                        continue
                    _param.sub_(_param_0)
                for _delta_param, _accum_delta_param in zip(_trans_model.parameters(), accum_delta):
                    _accum_delta_param.add_(_delta_param * w_k / self.q / self.W)

            sigme = self.z * self.S / self.q / self.W
            _trans_model.load_state_dict(state_dict_0)
            for _param, _delta in zip(_trans_model.parameters(), accum_delta):
                if not _param.requires_grad:
                    continue
                _param.add_(_delta)
                _param.add_(torch.normal(mean=0.0, std=sigme ** 2, size=_param.size()))

            new_state_dict = _trans_model.state_dict()
            self.model.load_state_dict(new_state_dict)
            self.push_log('Obtained a new version of parameters.')

        # TODO M.accum_priv_spending(z)
        # TODO print M.get_privacy_spent()

    def _wait_for_calculation(self) -> Dict[str, Dict[str, torch.Tensor]]:
        """Wait for every calculator finish its task or timeout."""
        if self.involve_aggregator:
            self._execute_training()
            self.push_log(f'The aggregator ID: {self.id} obtained its calculation results.')
            state_dicts = {self.id: self.state_dict()}
        else:
            state_dicts = {}

        self.push_log('Waiting for training results ...')
        training_results = self.data_channel.batch_receive_stream(
            receiver=self.id,
            source_list=self.gethered,
            timeout=self.calculation_timeout
        )
        for _source, _result in training_results.items():
            buffer = io.BytesIO(_result)
            _new_state_dict = torch.load(buffer)
            state_dicts[_source] = _new_state_dict
            self.push_log(f'Received calculation results from ID: {_source}')

        return state_dicts
