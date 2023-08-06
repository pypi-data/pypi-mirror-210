"""FedProx Scheduler."""
from copy import deepcopy
import io
from typing import Callable
from torch.nn import Module
import torch
from alphafed.contractor.common import ContractEvent

from alphafed.fed_avg import FedAvgScheduler
from alphafed.fed_avg.contractor import FinishTaskEvent, ResetRoundEvent
from alphafed.fed_avg.fed_avg import ResetRound
from alphafed.scheduler import TaskComplete
from alphafed import logger


__all__ = ['FedProxScheduler']


class FedProxScheduler(FedAvgScheduler):

    def __init__(self,
                 max_rounds: int = 0,
                 merge_epochs: int = 1,
                 mu: float = 0.01,
                 calculation_timeout: int = 300,
                 schedule_timeout: int = 30,
                 log_rounds: int = 0,
                 involve_aggregator: bool = False):
        super().__init__(max_rounds=max_rounds,
                         merge_epochs=merge_epochs,
                         calculation_timeout=calculation_timeout,
                         schedule_timeout=schedule_timeout,
                         log_rounds=log_rounds,
                         involve_aggregator=involve_aggregator)
        self.mu = mu
        self.global_model: Module = None

    def _wait_for_updating_model(self):
        """Wait for receiving latest parameters from aggregator."""
        def _complementary_handler(event: ContractEvent):
            if isinstance(event, FinishTaskEvent):
                raise TaskComplete()
            elif isinstance(event, ResetRoundEvent):
                raise ResetRound()

        self.push_log('Waiting for receiving latest parameters from the aggregator ...')
        _, parameters = self.data_channel.receive_stream(
            receiver=self.id,
            complementary_handler=_complementary_handler,
            source=self._aggregator
        )
        buffer = io.BytesIO(parameters)
        new_state_dict = torch.load(buffer)
        self.load_state_dict(new_state_dict)
        self.global_model = deepcopy(self.model)
        self.push_log('Successfully received latest parameters.')
    
    def calc_prox_loss(self, origin_loss_func: Callable, *args, **kwargs) -> torch.Tensor:
        origin_loss = origin_loss_func(*args, **kwargs)
        proximal_term = 0.0
        for w, w_t in zip(self.model.parameters(), self.global_model.parameters()):
            proximal_term += (w - w_t).norm(2)
        return origin_loss + (self.mu / 2) * proximal_term
