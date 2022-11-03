import logging
import json

from jusbrasil_challenge.exceptions import BaseException
from jusbrasil_challenge.messages import ErrorMessage

logg = logging.getLogger("jusbrasil_challenge.mq_gestor.exceptions")


class ConnectionFailedException(BaseException):
    name: str = "MQConnectionFailedError"
    logger: logging.Logger = logg

    def build_message(self, error: str) -> dict:
        message: str = f"There was an error trying to connect to the message queue manager: {error}"
        return json.loads(ErrorMessage(description=message, type=self.name).to_json())


class QueueNotDefinedException(BaseException):
    name: str = "QueueNotDefinedError"
    logger: logging.Logger = logg

    def build_message(self) -> dict:
        message: str = f"No queue has been defined for the operation"
        return json.loads(ErrorMessage(description=message, type=self.name).to_json())
