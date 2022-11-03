from typing import Dict, Callable

from .. import al, ce

ROBOTS_HANDLER_MAP: Dict[str, Callable] = {
    "AL": al.capture_task,
    "CE": ce.capture_task,
}
