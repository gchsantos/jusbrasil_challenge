import logging
import json

from jusbrasil_challenge.messages import ErrorMessage

logg = logging.getLogger(__name__)


class BaseCaptureException(Exception):
    name: str = "BaseCaptureError"
    logger: logging.Logger = logg

    def __init__(self, *args: object, **kwargs) -> None:
        self.message = self.build_message(*args, **kwargs)
        super().__init__(self.message)

    def build_message(self, error: str) -> dict:
        message: str = f"An error occurred while capturing the lawsuit: {error}"
        return json.loads(ErrorMessage(description=message, type=self.name).to_json())
