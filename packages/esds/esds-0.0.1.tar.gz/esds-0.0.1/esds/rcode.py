from enum import Enum

class RCode(Enum):
    SUCCESS = 0
    FAIL = 1
    TIMEOUT_EXPIRE = 2
    RECEIVER_TURNED_OFF = 3
    RECEIVER_UNAVAILABLE = 4
    UNKNOWN = 5

