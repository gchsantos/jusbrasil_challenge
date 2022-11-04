from typing import Dict, Callable

from .. import al, ce

ROBOTS_HANDLER_MAP: Dict[str, Callable] = {
    "AL": al.capture_task,
    "CE": ce.capture_task,
}

NOT_FOUND_MESSAGES = [
    "Não foi possível obter os dados do processo. Por favor tente novamente mais tarde.",
    "Não existem informações disponíveis para os parâmetros informados.",
]
