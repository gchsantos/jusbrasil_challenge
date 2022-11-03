import logging
import json

from jusbrasil_challenge.messages import ErrorMessage

logg = logging.getLogger(__name__)


class BaseException(Exception):
    name: str = "BaseError"
    logger: logging.Logger = logg

    def __init__(self, *args: object, **kwargs) -> None:
        self.message = self.build_message(*args, **kwargs)
        self.log()
        super().__init__(self.message)

    def build_message(self, message) -> dict:
        return json.loads(ErrorMessage(description=message, type=self.name).to_json())

    def log(self, *args, message=None, **kwargs):
        self.logger.exception(message or self.message)
