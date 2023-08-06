import threading
import random
import time
from dataclasses import asdict
from idun_data_models import Message
from idun_tools import logger
from .connection_pool import DeviceConnectionPool


def generate(
    kinesis_client,
    devices: int,
    connections_per_device: int,
    p_connection_end: float,
    p_impedance_measurement: float = 0,
    mock_recorded: bool = False,
    random_seed: int = 0,
    stop: threading.Event = threading.Event(),
) -> set[Message]:
    """
    Generate random device messages and put them on the Kinesis stream.
    When the connection pool finishes or a stop signal arrives, it terminates, and returns a set of all messages.
    """
    logger.info("> Generating test data")
    connectionPool = DeviceConnectionPool(
        devices=devices,
        connections_per_device=connections_per_device,
        p_connection_end=p_connection_end,
        p_impedance_measurement=p_impedance_measurement,
        mock_recorded=mock_recorded,
        random_seed=random_seed,
    )
    messageSet = set()
    while not stop.is_set() and not connectionPool.done():
        data = connectionPool.next_message()
        if data:
            kinesis_client.put_record(
                Data=asdict(data),
                PartitionKey=data.deviceID,
            )
            messageSet.add(data)
    logger.info("> Stop generating test data")
    return messageSet



def randomDecodedPayload():
    "Return a random, decoded payload. Mock the decoding function."
    return {
        "eeg_ch1": list(
            map(
                lambda x: {
                    "timestamp": time.time(),
                    "value": random.random(),
                },
                range(0, 20),
            )
        ),
        "acc": list(
            map(
                lambda x: {
                    "timestamp": time.time(),
                    "x": random.random(),
                    "y": random.random(),
                    "z": random.random(),
                },
                range(0, 3),
            )
        ),
        "magn": list(
            map(
                lambda x: {
                    "timestamp": time.time(),
                    "x": random.random(),
                    "y": random.random(),
                    "z": random.random(),
                },
                range(0, 3),
            )
        ),
        "gyro": list(
            map(
                lambda x: {
                    "timestamp": time.time(),
                    "x": random.random(),
                    "y": random.random(),
                    "z": random.random(),
                },
                range(0, 3),
            )
        ),
    }
