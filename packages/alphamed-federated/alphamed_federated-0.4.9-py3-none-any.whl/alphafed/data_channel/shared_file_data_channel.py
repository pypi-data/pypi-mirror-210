"""通过共享文件方式传输数据的数据通道."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from tempfile import TemporaryFile
from time import sleep
from typing import Callable, Dict, List, Tuple

import requests

from alphafed.contractor.common import ContractEvent

from .. import logger
from ..contractor import (AcceptSharedFileSendingDataEvent,
                          ApplySharedFileSendingDataEvent,
                          DenySendingDataEvent, TaskMessageContractor)
from .data_channel import DataChannel, SendingError

__all__ = ['SharedFileDataChannel']


class SharedFileDataChannel(DataChannel):
    """共享文件数据传输通道."""

    def __init__(self, contractor: TaskMessageContractor) -> None:
        super().__init__()
        self.contractor = contractor
        self._received = {}

    def send_stream(self,
                    source: str,
                    target: str,
                    data_stream: bytes,
                    connection_timeout: int = 30,
                    timeout: int = 60) -> str | None:
        received = self.batch_send_stream(source=source,
                                          target=[target],
                                          data_stream=data_stream,
                                          connection_timeout=connection_timeout,
                                          timeout=timeout,
                                          ensure_all_succ=True)
        return received[0] if received else None

    def batch_send_stream(self,
                          source: str,
                          target: List[str],
                          data_stream: bytes,
                          connection_timeout: int = 30,
                          timeout: int = 60,
                          ensure_all_succ: bool = False) -> List[str] | None:
        assert source and isinstance(source, str), f'Invalid source ID: {source}'
        assert (
            target and isinstance(target, list) and all(isinstance(_id, str) for _id in target)
        ), f'Invalid target ID list `{target}`.'
        assert data_stream, 'Must specify some data to send.'
        assert isinstance(data_stream, bytes), '`data_stream` must be a bytes object.'
        assert isinstance(connection_timeout, int), '`connection_timeout` must be an int value.'
        assert timeout is None or isinstance(timeout, int), '`timeout` must be None or an int value.'
        if not timeout or timeout < 0:
            timeout = 0
        assert isinstance(ensure_all_succ, bool), '`ensure_all_succ` must be True or False'

        start_at = datetime.utcnow().timestamp()
        current = start_at
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._do_send_stream,
                                     source=source,
                                     target=target,
                                     data_stream=data_stream,
                                     connection_timeout=connection_timeout)
            while not timeout or current - start_at < timeout:
                if future.done():
                    error = future.exception()
                    if error is not None:
                        # reraise to print exception stack
                        try:
                            raise error
                        except Exception:
                            logger.exception('Something wrong in transmission.')
                    break
                else:
                    sleep(0.1)
                    current = datetime.utcnow().timestamp()

            result = future.result()
            if ensure_all_succ and len(result) != len(target):
                failed = [_id for _id in target if _id not in result]
                raise SendingError(f'Failed to send data stream to `{failed}`.')
            else:
                return result

    def _do_send_stream(self,
                        source: str,
                        target: List[str],
                        data_stream: bytes,
                        connection_timeout: int = 30) -> None:
        """Perform sending data stream to a receiver.

        :args
            :source
                the ID of the data sender
            :target
                the ID list of the receiver
            :data_stream
                data_stream content
            :connection_timeout
                the timeout seconds to establish the connection
        """
        with TemporaryFile() as tf:
            tf.write(data_stream)
            tf.seek(0)
            file_url = self.contractor.upload_file(fp=tf)

        session_id = self.contractor.apply_sending_data(source=source,
                                                        target=target,
                                                        file_url=file_url)

        # 监听 L1 返回的处理结果
        accepted = []
        rejected = []
        for _event in self.contractor.contract_events(timeout=connection_timeout):
            if isinstance(_event, DenySendingDataEvent) and _event.session_id == session_id:
                rejected.append(_event.rejecter)
                logger.warn(' '.join([
                    f'Sending data application refused by `{_event.rejecter}`',
                    f'because of `{_event.cause}`.'
                ]))
            elif (
                isinstance(_event, AcceptSharedFileSendingDataEvent)
                and _event.session_id == session_id
            ):
                accepted.append(_event.receiver)
            else:
                continue

            if len(accepted) + len(rejected) == len(target):
                break

        logger.debug('Sending data stream complete.')
        return accepted

    def receive_stream(self,
                       receiver: str,
                       source: str,
                       complementary_handler: Callable[[ContractEvent], None] = None,
                       timeout: int = 0) -> Tuple[str, bytes] | None:
        received = self.batch_receive_stream(receiver=receiver,
                                             complementary_handler=complementary_handler,
                                             timeout=timeout,
                                             source_list=[source],
                                             ensure_all_succ=True)
        return received.popitem() if received else None

    def batch_receive_stream(self,
                             receiver: str,
                             source_list: List[str],
                             complementary_handler: Callable[[ContractEvent], None] = None,
                             timeout: int = 0,
                             ensure_all_succ: bool = False) -> Dict[str, bytes] | None:
        assert (
            receiver and isinstance(receiver, str)
        ), f"Must specify the receiver's ID: {receiver} ."
        assert isinstance(timeout, int), f"Timeout must be an integer: {timeout} ."
        if not timeout or timeout < 0:
            timeout = 0
        assert (
            source_list
            and isinstance(source_list, list)
            and all(isinstance(_id, str) for _id in source_list)
        ), f'Invalid source_list is specified: {source_list}'

        start_at = datetime.utcnow().timestamp()
        current = start_at
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._do_receive_stream,
                                     receiver=receiver,
                                     complementary_handler=complementary_handler,
                                     timeout=timeout,
                                     source_list=source_list)
            while not timeout or current - start_at < timeout:
                if future.done():
                    error = future.exception()
                    if error is not None:
                        # reraise to print exception stack
                        try:
                            raise error
                        except Exception:
                            logger.exception('Something wrong in transmission.')
                    break
                else:
                    sleep(0.1)
                    current = datetime.utcnow().timestamp()

            if ensure_all_succ and len(self._received) != len(source_list):
                failed = [_id for _id in source_list if _id not in self._received]
                raise SendingError(f'Failed to receive data stream from `{failed}`.')
            else:
                return self._received

    def _do_receive_stream(self,
                           receiver: str,
                           complementary_handler: Callable[[ContractEvent], None] = None,
                           timeout: int = 0,
                           source_list: List[str] = None):
        self._received = {}
        if timeout > 0:
            start = datetime.utcnow().timestamp()
        start_count = 0
        with ThreadPoolExecutor() as executor:
            while timeout <= 0 or datetime.utcnow().timestamp() - start < timeout:
                # Listen event, and jump out and inspect receive state every 1 second.
                # If each receiving process is started, stop listening.
                if start_count == len(source_list):
                    # only inspect receive state
                    if len(self._received) == len(source_list):
                        return
                else:
                    # listen events
                    for _event in self.contractor.contract_events(timeout=1):
                        if isinstance(_event, ApplySharedFileSendingDataEvent):
                            if source_list and _event.source not in source_list:
                                self.contractor.deny_sending_data(target=_event.source,
                                                                  session_id=_event.session_id,
                                                                  rejecter=receiver,
                                                                  cause='Not in accept list.')
                                continue

                            self.contractor.accept_sending_data(target=_event.source,
                                                                session_id=_event.session_id,
                                                                receiver=receiver)
                            executor.submit(self._download_data,
                                            sender=_event.source,
                                            file_url=_event.file_url)
                            start_count += 1
                        elif complementary_handler is not None:
                            complementary_handler(_event)
                        break  # fetch one each time

    def _download_data(self, sender: str, file_url: str):
        resp = requests.get(file_url)
        self._received[sender] = resp.content
