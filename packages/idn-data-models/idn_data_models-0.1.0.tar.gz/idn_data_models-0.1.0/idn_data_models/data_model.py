from dataclasses import dataclass
from datetime import datetime
from functools import reduce

@dataclass(frozen=True, slots=True)
class DevicePacket:
    "A single packet of data produced by the device"
    # [samples] Array of samples (eg. 20)
    ch1: list[int]
    # [samples]
    ch2: list[int]
    # [imuSamples][xyz] Array of 3D samples
    acc: list[list[int]]
    magn: list[list[int]]
    gyro: list[list[int]]

    def __hash__(self):
        def plushash(a: int, b: int):
            return hash(a) + hash(b)

        def hashreduce(x):
            return reduce(plushash, x)

        def hashmap(x):
            return hashreduce(map(hashreduce, x))

        return hashmap([self.ch1, self.ch2] + self.acc + self.magn + self.gyro)


@dataclass(frozen=True, slots=True)
class Message:
    """
    A Message encapsulates encrypted device packets with metadata.
    The IDUN SDK sends Messages with device data to the IDUN Cloud.
    """
    deviceTimestamp: str
    deviceID: str
    recordingID: str
    connectionID: str | None = None
    payload: str | None = None
    impedance: float | None = None
    stop: bool | None = None
    "Signal that the frontend sends to stop the recording"
    recorded: bool | None = None
    "Signal that the recorder sends to signal that batch processing is complete"
    enableStreamer: bool | None = None
    "Signal that the frontend can send to disable live streaming"


def emptyPacket() -> DevicePacket:
    return DevicePacket([], [], [[]], [[]], [[]])
