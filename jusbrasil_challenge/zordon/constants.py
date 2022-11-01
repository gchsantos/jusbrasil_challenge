from enum import IntEnum


class LINE_STATUS(IntEnum):
    PENDING = 1
    SUCCESS = 2
    ERROR = 3

    @classmethod
    def get_status(cls):
        return [(key.value, key.name) for key in cls]
