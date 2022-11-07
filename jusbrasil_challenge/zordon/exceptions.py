import logging
import json

from jusbrasil_challenge.exceptions import BaseException
from jusbrasil_challenge.messages import ErrorMessage


logg = logging.getLogger(__name__)


class MissingValueException(BaseException):
    name: str = "MissingValueError"
    logger: logging.Logger = logg

    def __init__(self, message: str) -> None:
        super().__init__(message=message, level=logging.WARNING, exc_info=False)


class UnsupportedCNJException(BaseException):
    name: str = "CNJUnsupportedError"
    logger: logging.Logger = logg

    def build_message(self, cnj: str) -> dict:
        message: str = f"CNJ '{cnj}' is not supported by the application"
        return json.loads(ErrorMessage(description=message, type=self.name).to_json())


class BatchConsultationException(BaseException):
    name: str = "BatchConsultationError"
    logger: logging.Logger = logg

    def __init__(self, message: str) -> None:
        super().__init__(message=message, level=logging.WARNING, exc_info=False)

    def build_message(self, message: str, consultation_id="") -> dict:
        if not message:
            message = f"An error occurred while capturing batch's consultation information. consultation_id: {consultation_id}"
        return json.loads(ErrorMessage(description=message, type=self.name).to_json())


class UnauthorizedConsultationException(BaseException):
    name: str = "UnauthorizedConsultation"
    logger: logging.Logger = logg

    def __init__(self, consultation_id) -> None:
        super().__init__(
            consultation_id=consultation_id, level=logging.WARNING, exc_info=False
        )

    def build_message(self, consultation_id: str) -> dict:
        message: str = f"Your profile is not authorized to get infos through this consultation_id '{consultation_id}'"
        return json.loads(ErrorMessage(description=message, type=self.name).to_json())
