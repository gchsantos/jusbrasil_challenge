import logging
import json

from jusbrasil_challenge.messages import ErrorMessage

logg = logging.getLogger(__name__)


class BaseException(Exception):
    name: str = "BaseError"
    logger: logging.Logger = logg

    def __init__(
        self, *args: object, level: int = logging.ERROR, exc_info=True, **kwargs
    ) -> None:
        self.message = self.build_message(*args, **kwargs)
        self.level = level
        self.exc_info = exc_info
        self.log()
        super().__init__(self.message)

    def build_message(self, message) -> dict:
        return json.loads(ErrorMessage(description=message, type=self.name).to_json())

    def log(self, message=None, **kwargs) -> None:
        logg.log(self.level, message or self.message, exc_info=self.exc_info, **kwargs)
