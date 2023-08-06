import os
import sys
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHONPATH = os.path.join(CURRENT_DIR, os.pardir, os.pardir, os.pardir)
sys.path.insert(0, PYTHONPATH)

if True:
    from alphafed import logger
    from alphafed.contractor import DenySendingDataEvent, TaskMessageContractor
    from alphafed.data_channel import GRPCDataChannel, SharedFileDataChannel, SendingError
    from alphafed.examples.data_channel import (DEV_TASK_ID, RECEIVER_2_ID,
                                                RECEIVER_4_ID, SENDER_ID)


noisy_event = DenySendingDataEvent(session_id='test session', rejecter='no one', cause='no cause')
sync_event = noisy_event
targets = [RECEIVER_2_ID, RECEIVER_4_ID]
contractor = TaskMessageContractor(task_id=DEV_TASK_ID)


def log_obviously(msg: str):
    logger.info('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    logger.info(msg)
    logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')


original_msg = 'Hello, 世界！'
data_stream = original_msg.encode('utf-8')
log_obviously(f'The original message are: {original_msg} .')


def test_grpc():
    data_channel = GRPCDataChannel(contractor=contractor)
    # The original ports are occupied by alphamed-federated-service
    data_channel._ports = [i for i in range(21000, 21010)]

    # send noisy event
    contractor._new_contract(targets=targets, event=noisy_event)

    # send data stream
    for _target in targets:
        data_channel.send_stream(source=SENDER_ID, target=_target, data_stream=data_stream)
    log_obviously('Sending by GRPC channel complete.')
    contractor._new_contract(targets=targets, event=sync_event)

    # denied by receivers
    for _target in targets:
        try:
            data_channel.send_stream(source=SENDER_ID, target=_target, data_stream=data_stream)
        except SendingError:
            logger.exception('Transmission Failed.')
    time.sleep(5)
    contractor._new_contract(targets=targets, event=sync_event)


def test_shared_file():
    # send noisy event
    data_channel = SharedFileDataChannel(contractor=contractor)
    contractor._new_contract(targets=targets, event=noisy_event)

    # send data stream
    accepted = []
    for _target in targets:
        received = data_channel.send_stream(source=SENDER_ID,
                                            target=_target,
                                            data_stream=data_stream)
        if received:
            accepted.append(received)
    if len(accepted) == len(targets):
        log_obviously('Sending by shared file channel complete.')
    else:
        log_obviously('Sending by shared file channel failed.')
        log_obviously(f'Accepting list: {accepted} .')
    contractor._new_contract(targets=targets, event=sync_event)

    # denied by receivers
    for _target in targets:
        try:
            received = data_channel.send_stream(source=SENDER_ID,
                                                target=_target,
                                                data_stream=data_stream)
        except SendingError:
            logger.exception('Transmission Failed.')
    time.sleep(5)
    contractor._new_contract(targets=targets, event=sync_event)


def test_batch_send():
    # all complete
    data_channel = SharedFileDataChannel(contractor=contractor)
    accepted = data_channel.batch_send_stream(source=SENDER_ID,
                                              target=targets,
                                              data_stream=data_stream)
    if len(accepted) == len(targets):
        log_obviously('Sending by shared file channel complete.')
    else:
        log_obviously('Sending by shared file channel failed.')
        log_obviously(f'Accepting list: {accepted} .')
    contractor._new_contract(targets=targets, event=sync_event)

    # partly complete and exception raised
    try:
        accepted = data_channel.batch_send_stream(source=SENDER_ID,
                                                  target=targets,
                                                  data_stream=data_stream,
                                                  ensure_all_succ=True)
    except SendingError as err:
        log_obviously(f'Not all successed and catched the exception `{err}`.')
    contractor._new_contract(targets=targets, event=sync_event)

    # partly complete and exception not raised
    accepted = data_channel.batch_send_stream(source=SENDER_ID,
                                              target=targets,
                                              data_stream=data_stream)
    log_obviously(f'Mission complete for `{accepted}`.')
    contractor._new_contract(targets=targets, event=sync_event)


def test_batch_receive():
    # all complete
    data_channel = SharedFileDataChannel(contractor=contractor)
    data_dict = data_channel.batch_receive_stream(receiver=SENDER_ID, source_list=targets)
    if len(data_dict) == len(targets):
        log_obviously('Batch receiving by shared file channel complete.')
    contractor._new_contract(targets=targets, event=sync_event)

    # partly complete and exception raised
    try:
        data_dict = data_channel.batch_receive_stream(receiver=SENDER_ID,
                                                      source_list=targets,
                                                      timeout=10,
                                                      ensure_all_succ=True)
    except SendingError as err:
        log_obviously(f'Not all successed and catched the exception `{err}`.')
    contractor._new_contract(targets=targets, event=sync_event)

    # partly complete and exception not raised
    data_dict = data_channel.batch_receive_stream(receiver=SENDER_ID,
                                                  timeout=10,
                                                  source_list=targets)
    if len(data_dict) == len(targets):
        log_obviously('Receiving from shared file channel complete.')
    else:
        log_obviously('Receiving from shared file channel failed.')
        log_obviously(f'Received from: `{list(data_dict.keys())}`.')
    contractor._new_contract(targets=targets, event=sync_event)


test_grpc()
test_shared_file()
test_batch_send()
test_batch_receive()
