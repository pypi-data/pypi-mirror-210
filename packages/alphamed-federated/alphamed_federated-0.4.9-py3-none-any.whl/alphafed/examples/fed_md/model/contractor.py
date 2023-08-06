"""Homo FedMD contractor."""

from dataclasses import dataclass
import secrets
from typing import Dict, List
from alphafed.contractor.common import ContractEvent
from alphafed.contractor.task_message_contractor import TaskMessageContractor, TaskMessageEventFactory


@dataclass
class CheckinEvent(ContractEvent):
    """An event of checkin for a specific task."""

    TYPE = 'checkin'

    peer_id: str
    nonce: str

    @classmethod
    def contract_to_event(cls, contract: dict) -> 'CheckinEvent':
        event_type = contract.get('type')
        peer_id = contract.get('peer_id')
        nonce = contract.get('nonce')
        assert event_type == cls.TYPE, f'合约类型错误: {event_type}'
        assert peer_id and isinstance(peer_id, str), f'invalid peer_id: {peer_id}'
        assert nonce or isinstance(nonce, str), f'invalid nonce: {nonce}'
        return CheckinEvent(peer_id=peer_id, nonce=nonce)


@dataclass
class CheckinResponseEvent(ContractEvent):
    """An event of responding checkin event."""

    TYPE = 'checkin_response'

    round: int
    aggregator: str
    nonce: str

    @classmethod
    def contract_to_event(cls, contract: dict) -> 'CheckinResponseEvent':
        event_type = contract.get('type')
        round = contract.get('round')
        aggregator = contract.get('aggregator')
        nonce = contract.get('nonce')
        assert event_type == cls.TYPE, f'合约类型错误: {event_type}'
        assert isinstance(round, int) and round >= 0, f'invalid round: {round}'
        assert aggregator and isinstance(aggregator, str), f'invalid aggregator: {aggregator}'
        assert nonce and isinstance(nonce, str), f'invalid nonce: {nonce}'
        return CheckinResponseEvent(round=round, aggregator=aggregator, nonce=nonce)


@dataclass
class SyncStateEvent(ContractEvent):
    """An event of synchronising task state."""

    TYPE = 'sync_state'

    round: int
    aggregator: str

    @classmethod
    def contract_to_event(cls, contract: dict) -> 'SyncStateEvent':
        event_type = contract.get('type')
        round = contract.get('round')
        aggregator = contract.get('aggregator')
        assert event_type == cls.TYPE, f'合约类型错误: {event_type}'
        assert isinstance(round, int) and round >= 0, f'invalid round: {round}'
        assert aggregator and isinstance(aggregator, str), f'invalid aggregator: {aggregator}'
        return SyncStateEvent(round=round, aggregator=aggregator)


@dataclass
class SyncStateResponseEvent(ContractEvent):
    """An event of responding to synchronising task state event."""

    TYPE = 'sync_state_response'

    round: int
    peer_id: str

    @classmethod
    def contract_to_event(cls, contract: dict) -> 'SyncStateResponseEvent':
        event_type = contract.get('type')
        round = contract.get('round')
        peer_id = contract.get('peer_id')
        assert event_type == cls.TYPE, f'合约类型错误: {event_type}'
        assert isinstance(round, int) and round >= 0, f'invalid round: {round}'
        assert peer_id and isinstance(peer_id, str), f'invalid peer_id: {peer_id}'
        return SyncStateResponseEvent(round=round, peer_id=peer_id)


@dataclass
class FinishTaskEvent(ContractEvent):
    """An event of finishing the specified task."""

    TYPE = 'finish_task'

    @classmethod
    def contract_to_event(cls, contract: dict) -> 'FinishTaskEvent':
        event_type = contract.get('type')
        assert event_type == cls.TYPE, f'合约类型错误: {event_type}'
        return FinishTaskEvent()


@dataclass
class ResetRoundEvent(ContractEvent):
    """An event of resetting context of current training round."""

    TYPE = 'reset_round'

    @classmethod
    def contract_to_event(cls, contract: dict) -> 'ResetRoundEvent':
        event_type = contract.get('type')
        assert event_type == cls.TYPE, f'合约类型错误: {event_type}'
        return ResetRoundEvent()


@dataclass
class StartRoundEvent(ContractEvent):
    """An event of starting a new round of training."""

    TYPE = 'start_round'

    round: int
    calculators: List[str]
    aggregator: str

    @classmethod
    def contract_to_event(cls, contract: dict) -> 'StartRoundEvent':
        event_type = contract.get('type')
        round = contract.get('round')
        calculators = contract.get('calculators')
        aggregator = contract.get('aggregator')
        assert event_type == cls.TYPE, f'合约类型错误: {event_type}'
        assert isinstance(round, int) and round > 0, f'invalid round: {round}'
        assert (
            calculators and isinstance(calculators, list)
            and all(_peer_id and isinstance(_peer_id, str) for _peer_id in calculators)
        ), f'invalid participants: {calculators}'
        assert aggregator and isinstance(aggregator, str), f'invalid aggregator: {aggregator}'
        return StartRoundEvent(round=round,
                               calculators=calculators,
                               aggregator=aggregator)


@dataclass
class CloseRoundEvent(ContractEvent):
    """An event of closing a specific round of training."""

    TYPE = 'close_round'

    round: int

    @classmethod
    def contract_to_event(cls, contract: dict) -> 'CloseRoundEvent':
        event_type = contract.get('type')
        round = contract.get('round')
        assert event_type == cls.TYPE, f'合约类型错误: {event_type}'
        assert isinstance(round, int) and round > 0, f'invalid round: {round}'
        return CloseRoundEvent(round=round)


@dataclass
class RoundTrainFinishEvent(ContractEvent):
    """An event of finishing a round of alignment and fine-tune training."""

    TYPE = 'round_train_finish'

    round: int
    peer_id: str

    @classmethod
    def contract_to_event(cls, contract: dict) -> 'RoundTrainFinishEvent':
        event_type = contract.get('type')
        round = contract.get('round')
        peer_id = contract.get('peer_id')
        assert event_type == cls.TYPE, f'合约类型错误: {event_type}'
        assert isinstance(round, int) and round >= 0, f'invalid round: {round}'
        assert peer_id and isinstance(peer_id, str), f'invalid peer_id: {peer_id}'
        return RoundTrainFinishEvent(round=round, peer_id=peer_id)


@dataclass
class PartnerCloseEvent(ContractEvent):
    """An event of finishing a round of alignment and fine-tune training."""

    TYPE = 'partner_close'

    peer_id: str

    @classmethod
    def contract_to_event(cls, contract: dict) -> 'PartnerCloseEvent':
        event_type = contract.get('type')
        peer_id = contract.get('peer_id')
        assert event_type == cls.TYPE, f'合约类型错误: {event_type}'
        assert peer_id and isinstance(peer_id, str), f'invalid peer_id: {peer_id}'
        return PartnerCloseEvent(peer_id=peer_id)


class HomoFedMDEventFactory(TaskMessageEventFactory):

    _CLASS_MAP: Dict[str, ContractEvent] = {
        CheckinEvent.TYPE: CheckinEvent,
        CheckinResponseEvent.TYPE: CheckinResponseEvent,
        SyncStateEvent.TYPE: SyncStateEvent,
        SyncStateResponseEvent.TYPE: SyncStateResponseEvent,
        FinishTaskEvent.TYPE: FinishTaskEvent,
        ResetRoundEvent.TYPE: ResetRoundEvent,
        StartRoundEvent.TYPE: StartRoundEvent,
        CloseRoundEvent.TYPE: CloseRoundEvent,
        RoundTrainFinishEvent.TYPE: RoundTrainFinishEvent,
        PartnerCloseEvent.TYPE: PartnerCloseEvent,
        **TaskMessageEventFactory._CLASS_MAP
    }


class HomoFedMDContractor(TaskMessageContractor):

    def __init__(self, task_id: str):
        super().__init__(task_id=task_id)
        self._event_factory = HomoFedMDEventFactory

    def checkin(self, peer_id: str) -> str:
        """Checkin to the task.

        :return
            A nonce string used for identifying matched sync_state reply.
        """
        nonce = secrets.token_hex(16)
        event = CheckinEvent(peer_id=peer_id, nonce=nonce)
        self._new_contract(targets=self.EVERYONE, event=event)
        return nonce

    def respond_check_in(self,
                         round: int,
                         aggregator: str,
                         nonce: str,
                         requester_id: str):
        """Respond checkin event."""
        event = CheckinResponseEvent(round=round, aggregator=aggregator, nonce=nonce)
        self._new_contract(targets=[requester_id], event=event)

    def sync_state(self,
                   round: int,
                   aggregator: str,
                   targets: str = TaskMessageContractor.EVERYONE):
        """Help for synchronising task state."""
        event = SyncStateEvent(round=round, aggregator=aggregator)
        self._new_contract(targets=targets, event=event)

    def respond_sync_state(self, round: int, peer_id: str, aggregator: str):
        """Help for synchronising task state."""
        event = SyncStateResponseEvent(round=round, peer_id=peer_id)
        self._new_contract(targets=[aggregator], event=event)

    def reset_round(self):
        """Reset current training round."""
        event = ResetRoundEvent()
        self._new_contract(targets=self.EVERYONE, event=event)

    def start_round(self,
                    calculators: List[str],
                    round: int,
                    aggregator: str):
        """Create a round of training."""
        event = StartRoundEvent(round=round,
                                calculators=calculators,
                                aggregator=aggregator)
        self._new_contract(targets=self.EVERYONE, event=event)

    def close_round(self, round: int):
        """Start a round of training."""
        event = CloseRoundEvent(round=round)
        self._new_contract(targets=self.EVERYONE, event=event)

    def notice_train_complete(self, round: int, peer_id: str, aggregator: str):
        """Notice aggregator that local training is complete."""
        event = RoundTrainFinishEvent(round=round, peer_id=peer_id)
        self._new_contract(targets=[aggregator], event=event)

    def finish_task(self):
        """Finish the specified task."""
        event = FinishTaskEvent()
        self._new_contract(targets=self.EVERYONE, event=event)

    def close_partner(self, peer_id: str, aggregator: str):
        event = PartnerCloseEvent(peer_id=peer_id)
        self._new_contract(targets=[aggregator], event=event)
