from typing import List, Union

from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase

from jusbrasil_challenge.messages import ReturnBaseMessage


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BatchInsertDataMessage:
    cnjs: Union[List[str], str]
    refresh_lawsuit: bool = False
    public_consultation: bool = False

    def __init__(self, **kwargs):
        self.cnjs = (
            [kwargs["cnjs"]] if isinstance(kwargs.get("cnjs"), str) else kwargs["cnjs"]
        )
        self.refresh_lawsuit = kwargs.get("refresh_lawsuit")
        self.public_consultation = kwargs.get("public_consultation")


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BatchInsertDataReturnMessage(ReturnBaseMessage):
    consultation_id: str

    def __init__(self, consultation_id: str):
        self.consultation_id = consultation_id
        super().__init__(
            type="BatchInsert",
            message="The solicitation was inserted in queue sucessfuly",
            description="Insertion of lawsuits in the robot's queue through the CNJ",
        )


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BatchConsultationData:
    ...


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BatchConsultationReturnMessage(ReturnBaseMessage):
    consultation_id: str
    batch_consultations: List[dict]

    def __init__(self, consultation_id, batch_consultations=[]):
        self.consultation_id = consultation_id
        self.batch_consultations = batch_consultations

        if self.batch_consultations:
            self.message = "success capturing consultation information"
        else:
            self.message = "consultation was not found"

        super().__init__(
            type="BatchConsultation",
            message=self.message,
            description="Get batch's captured information through the consultation_id",
        )
