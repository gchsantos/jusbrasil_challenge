from enum import Enum

CNJ_REGEX_PATTERN = r"[0-9]{7}-[0-9]{2}.[0-9]{4}.([0-9].[0-9]{2}).[0-9]{4}"


class CNJ_UF_IDENTIFIER(Enum):
    AL = "8.02"
    CE = "8.06"
