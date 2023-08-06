"""Homo FedPer contractor."""

from dataclasses import dataclass

from alphafed.contractor import ContractEvent
from alphafed.fed_avg.contractor import FedAvgContractor, FedAvgEventFactory


@dataclass
class CollaboratorCompleteEvent(ContractEvent):
    """An event of notify a collaborator completes its task."""

    TYPE = 'collab_complete'

    peer_id: str

    @classmethod
    def contract_to_event(cls, contract: dict) -> 'CollaboratorCompleteEvent':
        event_type = contract.get('type')
        peer_id = contract.get('peer_id')
        assert event_type == cls.TYPE, f'合约类型错误: {event_type}'
        assert peer_id and isinstance(peer_id, str), f'invalid peer_id: {peer_id}'
        return CollaboratorCompleteEvent(peer_id=peer_id)


class HomoFedPerEventFactory(FedAvgEventFactory):

    _CLASS_MAP = {
        CollaboratorCompleteEvent.TYPE: CollaboratorCompleteEvent,
        **FedAvgEventFactory._CLASS_MAP,
    }


class HomoFedPerContractor(FedAvgContractor):

    def __init__(self, task_id: str):
        super().__init__(task_id=task_id)
        self._event_factory = HomoFedPerEventFactory

    def notify_collaborator_complete(self, peer_id: str, host: str):
        """Notify the host a collaborator completes its task."""
        event = CollaboratorCompleteEvent(peer_id=peer_id)
        self._new_contract(targets=[host], event=event)
