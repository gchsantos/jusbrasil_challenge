from celery import shared_task
from celery.utils.log import get_task_logger

from .core.esaj_capture_robot import EsajCaptureRobot
from .core.task_base import BaseTaskWithRetry
from .core.exceptions import BaseCaptureException


logger = get_task_logger(__name__)


class RobotCE(EsajCaptureRobot):
    url: str = "https://esaj.tjce.jus.br/cpopg/open.do"

    def __init__(self, **kwargs):
        super().__init__(url=self.url)

    def capture_pipeline(self, cnj: str, batch_line_id: str, uid: str):
        return f"Hello CEARÁ! {cnj, batch_line_id, uid}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def capture_task(self, cnj: str, batch_line_id: str, uid: str):
    self.update_state(state="STARTED", meta={"user_id": uid})
    RobotCE().capture_pipeline(cnj, batch_line_id, uid)
