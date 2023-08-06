"""计算参与方之间传输数据的数据通道."""

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Tuple

from alphafed.contractor.common import ContractEvent

__all__ = ['DataChannel', 'SendingError']


class DataChannel(ABC):
    """数据传输通道."""

    @abstractmethod
    def send_stream(self,
                    source: str,
                    target: str,
                    data_stream: bytes,
                    connection_timeout: int = 30,
                    timeout: int = 60,
                    **kwargs) -> str | None:
        """Send data stream to the target.

        Args:
            source:
                the ID of the data sender.
            target:
                the ID of the receiver.
            data_stream:
                data_stream content.
            connection_timeout:
                the timeout seconds to establish the connection.
            timeout:
                the timeout seconds to complete the data transmission, set to 0 to disable timeout.

        Return:
            The Node ID of the receiver or None if fails.
        """

    @abstractmethod
    def batch_send_stream(self,
                          source: str,
                          target: List[str],
                          data_stream: bytes,
                          connection_timeout: int = 30,
                          timeout: int = 60,
                          ensure_all_succ: bool = False,
                          **kwargs) -> List[str] | None:
        """Send data stream to receivers.

        Args:
            source:
                the ID of the data sender.
            target:
                the ID list of receivers.
            data_stream:
                data_stream content.
            connection_timeout:
                the timeout seconds to establish the connection.
            timeout:
                the timeout seconds to complete the data transmission, set to 0 to disable timeout.
            ensure_all_succ:
                If set True, raise an exception when any target fails the transmission,
                otherwise return the Node id list whose transmissions are complete.
        Return:
            The ID list of accepting nodes or None if fails.
        """

    @abstractmethod
    def receive_stream(self,
                       receiver: str,
                       source: str,
                       complementary_handler: Callable[[ContractEvent], None] = None,
                       timeout: int = 0,
                       **kwargs) -> Tuple[str, bytes] | None:
        """Receive data stream from a sender.

        Args:
            receiver:
                the ID of the receiver.
            source:
                The node ID from which transmission will be accepted. Must be specified
                for security reasons.
            complementary_handler:
                A handler function which is used to deal with events received in the
                period of transmission except `ApplySendingDataEvent`.

                Because the process of algorithm could be very complicated, it's possible
                to receive various contract events during data transmission. When it's
                necessary to do some actions on those events, the logic could be passed
                in by `complementary_handler` function. The implementation of
                `complementary_handler` should accept only one argument of type
                `ContractEvent`, and it will be invoked any time a contract event other
                than `ApplySendingDataEvent` is received by:
                    complementary_handler(event_obj)
            timeout:
                Timeout in seconds to receive data stream.
        Return:
            Tuple[sender, data_stream]
            sender:
                The node ID of the sender.
                The data stream received or None if any error.
        """

    @abstractmethod
    def batch_receive_stream(self,
                             receiver: str,
                             source_list: List[str],
                             complementary_handler: Callable[[ContractEvent], None] = None,
                             timeout: int = 0,
                             ensure_all_succ: bool = False,
                             **kwargs) -> Dict[str, bytes] | None:
        """Simultaneously receive data stream from multiple senders.

        Args:
            receiver:
                the ID of the receiver.
            source_list:
                The white list of node IDs from which transmission will be accepted.
                Must be specified for security reasons.
            complementary_handler:
                A handler function which is used to deal with events received in the
                period of transmission except `ApplySendingDataEvent`.

                Because the process of algorithm could be very complicated, it's possible
                to receive various contract events during data transmission. When it's
                necessary to do some actions on those events, the logic could be passed
                in by `complementary_handler` function. The implementation of
                `complementary_handler` should accept only one argument of type
                `ContractEvent`, and it will be invoked any time a contract event other
                than `ApplySendingDataEvent` is received by:
                    complementary_handler(event_obj)
            timeout:
                Timeout in seconds to receive data stream.
            ensure_all_succ:
                If set True, raise an exception when any source in accept list fails
                the transmission, otherwise return the Node id list whose transmissions
                are complete.

        Return:
            Dict[sender, data_stream]
            sender:
                The node ID of the sender.
            data_stream:
                The data stream received.
        """


class SendingError(Exception):
    ...
