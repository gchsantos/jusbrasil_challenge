import logging
import json

from jusbrasil_challenge.exceptions import BaseException
from jusbrasil_challenge.messages import ErrorMessage


logg = logging.getLogger(__name__)


class MissingValueException(BaseException):
    name: str = "MissingValueError"
    logger: logging.Logger = logg


class UnsupportedCNJException(BaseException):
    name: str = "CNJUnsupportedError"
    logger: logging.Logger = logg

    def build_message(self, cnj: str) -> dict:
        message: str = f"CNJ '{cnj}' is not supported by the application"
        return json.loads(ErrorMessage(description=message, type=self.name).to_json())
