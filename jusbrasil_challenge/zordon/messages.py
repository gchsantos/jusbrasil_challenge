from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase

from jusbrasil_challenge.messages import ReturnBaseMessage


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BatchInsertDataMessage:
    cnj: str
    refresh_lawsuit: bool = False


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BatchInsertReturnDataMessage(ReturnBaseMessage):
    consultation_id: str

    def __init__(self, consultation_id: str):
        self.consultation_id = consultation_id
        super().__init__(
            type="BatchInsert",
            message="The solicitation was inserted in queue sucessfuly",
            description="Insertion of lawsuits in the robot's queue through the CNJ",
        )
