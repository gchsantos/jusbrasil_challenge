from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BaseMessage:
    type: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ReturnBaseMessage(BaseMessage):
    message: str
    description: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ErrorMessage(ReturnBaseMessage):
    def __init__(self, *, description: str, type: str = "Error"):
        super().__init__(
            type=type,
            message="An Error ocurred",
            description=description,
        )
