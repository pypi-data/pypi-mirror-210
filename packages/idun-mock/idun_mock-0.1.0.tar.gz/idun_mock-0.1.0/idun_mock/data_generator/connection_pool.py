import random, datetime, secrets
from enum import Enum
from pathlib import Path
from uuid import uuid4
from idun_data_models import Message, DevicePacket

class GeneratorTime(Enum):
    IDEAL_DEVICE = 1
    "Simulates an ideal device with perfect clock that sends 1 data packet every 80ms"
    CLIENT = 2
    "Uses the client's local time for each message's timestamp"

class DeviceConnectionPool:
    """
    DeviceConnectionPool generates device and connection IDs for mock messages.
    It simulates streams of messages arriving simultaneously from a given number of devices,
    which stop after a random number of messages (geometric distribution).
    The last message for each device has a `stop` field set to true.
    The next time the device is picked, it will start a new connection.
    The device payload isn't encrypted.
    """

    def __init__(
        self,
        devices: int,
        connections_per_device: int,
        p_connection_end: float,
        p_impedance_measurement: float,
        mock_recorded: bool,
        random_seed: int = 0,
        generator_time_type: GeneratorTime = GeneratorTime.IDEAL_DEVICE,
        enableStreamer= True,
    ) -> None:
        start_time=datetime.datetime.now()
        self.devices = [
            str(i) for i in range(0, devices)
        ]
        self.openDeviceIdx = list(range(0, devices))
        self.device_time = [start_time for i in range(0, devices)]
        self.connections_per_device = connections_per_device
        self.p_connection_end = p_connection_end
        self.generator_time_type = generator_time_type
        self.p_impedance_measurement = p_impedance_measurement
        self.mock_recorded = mock_recorded
        self.enableStreamer = enableStreamer
        self.connections = {d: 0 for d in range(0, devices)}
        self.first_message = {d: True for d in range(0, devices)}
        self.random = random.Random()
        self.random.seed(random_seed)
        self.connection_prefix = uuid4()

    def next_message(self) -> Message | None:
        device = self.random.choice(self.openDeviceIdx)
        deviceID = str(self.devices[device])
        connection = self.connections[device]
        if connection == self.connections_per_device:
            self.openDeviceIdx.remove(device)
            return None
        # Never end the connection at the first message
        connectionEnd = (
            not self.first_message[device]
            and self.random.random() < self.p_connection_end
        )
        self.first_message[device] = False

        # Advance the device time by the real duration of a device packet; ie 80ms
        self.device_time[device] = self.device_time[device] + datetime.timedelta(milliseconds=80)
        if self.generator_time_type == GeneratorTime.IDEAL_DEVICE:
            message_timestamp = str(self.device_time[device])
        elif self.generator_time_type == GeneratorTime.CLIENT:
            message_timestamp = str(datetime.datetime.now())
        else:
            # Is there another case?
            message_timestamp = str(datetime.datetime.now())

        # Advance state
        if connectionEnd:
            self.connections[device] += 1
            self.first_message[device] = True
        # With a small probability, emit an impedance measurement. Otherwise, emit a normal device message.
        if self.random.random() < self.p_impedance_measurement:
            # Send an impedance message
            return Message(
                deviceTimestamp=message_timestamp,
                deviceID=deviceID,
                recordingID=connectionUUID(self.connection_prefix, connection, device),
                connectionID=deviceID,
                stop=connectionEnd,
                recorded=self.mock_recorded and connectionEnd,
                payload=None,
                impedance=self.random.random(),
                enableStreamer=self.enableStreamer,
            )
        else:
            return Message(
                deviceTimestamp=message_timestamp,
                deviceID=deviceID,
                recordingID=connectionUUID(self.connection_prefix, connection, device),
                connectionID=str(device),
                stop=connectionEnd,
                recorded=self.mock_recorded and connectionEnd,
                payload=random_payload(deviceID),
                enableStreamer=self.enableStreamer,
            )

    def allRecordingIDs(self) -> list:
        return [
            {
                "deviceID": device,
                "recordingID": connectionUUID(
                    self.connection_prefix, connection, device
                ),
            }
            for device in self.devices
            for connection in range(0, self.connections_per_device)
        ]

    def done(self) -> bool:
        return all(
            [c >= self.connections_per_device for c in self.connections.values()]
        )


def connectionUUID(prefix, recordingID, deviceID) -> str:
    # NOTE: this should be a UUID, but for the moment a concatenation will do
    return str(prefix) + str(recordingID) + str(deviceID)


def random_device_packet() -> DevicePacket:
    """
    Generate mock data for GDK 2.0, with mock data of two channels and counter
    """

    def randomSampleList(nSamples=20):
        return random.sample(range(0, 256), nSamples)

    def samplePointList(*args):
        return list(map(list, zip(*args)))

    return DevicePacket(
        ch1=randomSampleList(),
        ch2=randomSampleList(),
        acc=samplePointList(randomSampleList(), randomSampleList(), randomSampleList()),
        magn=samplePointList(
            randomSampleList(), randomSampleList(), randomSampleList()
        ),
        gyro=samplePointList(
            randomSampleList(), randomSampleList(), randomSampleList()
        ),
    )


def static_recordingKey(deviceID=None) -> bytes:
    "Decryption key to be used with the `random_payload` function."
    keys = {
        None: "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",  # old static key
        "0": "7e89fbec9fa8cf257a04ad4fe603f57a85adec2598b6d3f98229c02c3ecad00c",
    }
    if deviceID not in keys:
        key = keys[None]
    else:
        key = keys[deviceID]
    return bytes.fromhex(key)


def random_recordingKey() -> bytes:
    "Dynamically generated decryption key"
    return secrets.token_bytes(32)


def random_payload(deviceID=None) -> str:
    """
    Pick a random base64 encoded IGEB data packet from a short list of test samples.

    Example:

    Take a random device payload `p` and convert it into a dictionary that looks like a `DevicePacket`.
    ```
    from idun_guardian_client.igeb_utils_internal import decrypt_data, convert_igeb_data
    p= random_payload()
    d= convert_igeb_data(decrypt_data(base64.b64decode(p)[2:-1]))
    ```

    ! Bug: We can't use `dacite.from_dict` to create a DevicePacket:
    ```
    dacite.exceptions.WrongTypeError: wrong value type for field "acc" - should be "list" instead of value
    "[[-1.014, 2.337, -9.746], [-1.014, 2.337, -9.746], [-1.014, 2.337, -9.746], [-1.014, 2.337, -9.746], [-1.014, 2.337, -9.746], [-1.014, 2.337, -9.746], [-1.014, 2.337, -9.746], [-1.014, 2.337, -9.746], [-1.014, 2.337, -9.746], [-1.014, 2.337, -9.746], [-0.9380000000000001, 2.3770000000000002, -9.693], [-0.9380000000000001, 2.3770000000000002, -9.693], [-0.9380000000000001, 2.3770000000000002, -9.693], [-0.9380000000000001, 2.3770000000000002, -9.693], [-0.9380000000000001, 2.3770000000000002, -9.693], [-0.9380000000000001, 2.3770000000000002, -9.693], [-0.9380000000000001, 2.3770000000000002, -9.693], [-0.9380000000000001, 2.3770000000000002, -9.693], [-0.9380000000000001, 2.3770000000000002, -9.693], [-0.9380000000000001, 2.3770000000000002, -9.693]]"
    of type "list"
    ```
    """
    test_data_path = (
        Path(__file__).parent / f"igeb_test_packets-{deviceID}.txt"
    ).resolve()
    if not test_data_path.is_file():
        test_data_path = (Path(__file__).parent / "igeb_test_packets.txt").resolve()
    with open(test_data_path, "rt", encoding="ascii") as testdata_f:
        lines = testdata_f.readlines()
    return random.sample(lines, 1)[0].strip()
