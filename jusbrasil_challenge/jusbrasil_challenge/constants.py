from enum import Enum

CNJ_REGEX_PATTERN = r"\d{7}-?\d{2}.\d{4}.(\d.\d{2}).\d{4}"


class CNJ_UF_IDENTIFIER(Enum):
    AL = "8.02"
    CE = "8.06"
