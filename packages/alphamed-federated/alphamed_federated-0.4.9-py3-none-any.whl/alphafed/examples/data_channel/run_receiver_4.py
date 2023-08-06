import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHONPATH = os.path.join(CURRENT_DIR, os.pardir, os.pardir, os.pardir)
sys.path.insert(0, PYTHONPATH)

if True:
    from alphafed import logger
    from alphafed.contractor import (ContractEvent, DenySendingDataEvent,
                                     TaskMessageContractor)
    from alphafed.data_channel import (GRPCDataChannel, SendingError,
                                       SharedFileDataChannel)
    from alphafed.examples.data_channel import (DEV_TASK_ID, RECEIVER_4_ID,
                                                SENDER_ID)


contractor = TaskMessageContractor(task_id=DEV_TASK_ID)


def log_obviously(msg: str):
    logger.info('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    logger.info(msg)
    logger.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')


def noisy_handler(event: ContractEvent):
    log_obviously(f'Received a noisy event: {event}')


def wait_4_going_on():
    for _event in contractor.contract_events():
        if isinstance(_event, DenySendingDataEvent):
            return


def test_grpc():
    data_channel = GRPCDataChannel(contractor=contractor)
    # The original ports are occupied by alphamed-federated-service
    data_channel._ports = [i for i in range(21000, 21010)]

    # receive data
    sender, data_stream = data_channel.receive_stream(receiver=RECEIVER_4_ID,
                                                      source=SENDER_ID,
                                                      complementary_handler=noisy_handler)
    original_msg = data_stream.decode('utf-8')
    log_obviously(f'Received a message: {original_msg} from {sender}.')
    wait_4_going_on()

    # deny transmission
    _, data_stream = data_channel.receive_stream(receiver=RECEIVER_4_ID,
                                                 source='no one',
                                                 timeout=5)
    if data_stream is None:
        log_obviously('Nothing received.')
    else:
        log_obviously('Why received something from no one?')
    wait_4_going_on()


def test_shared_file():
    data_channel = SharedFileDataChannel(contractor=contractor)

    # receive data
    sender, data_stream = data_channel.receive_stream(receiver=RECEIVER_4_ID,
                                                      source=SENDER_ID,
                                                      complementary_handler=noisy_handler)
    original_msg = data_stream.decode('utf-8')
    log_obviously(f'Received a message: {original_msg} from {sender}.')
    wait_4_going_on()

    # deny transmission
    try:
        _, data_stream = data_channel.receive_stream(receiver=RECEIVER_4_ID,
                                                     source='no one',
                                                     timeout=5)
    except SendingError:
        log_obviously('Timeout.')
    wait_4_going_on()


def test_batch_send():
    # all complete
    data_channel = SharedFileDataChannel(contractor=contractor)
    sender, data_stream = data_channel.receive_stream(receiver=RECEIVER_4_ID, source=SENDER_ID)
    original_msg = data_stream.decode('utf-8')
    log_obviously(f'Received a message: {original_msg} from {sender}.')
    wait_4_going_on()

    # partly complete and not respond
    wait_4_going_on()

    # partly complete and not respond
    wait_4_going_on()


def test_batch_receive():
    # all complete
    data_channel = SharedFileDataChannel(contractor=contractor)
    data_channel.send_stream(source=RECEIVER_4_ID,
                             target=SENDER_ID,
                             data_stream=b'data_stream')
    wait_4_going_on()

    # partly complete and not send
    wait_4_going_on()

    # partly complete and send
    wait_4_going_on()


test_grpc()
test_shared_file()
test_batch_send()
test_batch_receive()
