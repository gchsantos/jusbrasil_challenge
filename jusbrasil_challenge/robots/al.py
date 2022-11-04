from celery import shared_task
from celery.utils.log import get_task_logger

from .core.esaj_capture_robot import EsajCaptureRobot
from .core.task_base import BaseTaskWithRetry

logger = get_task_logger(__name__)


class RobotAL(EsajCaptureRobot):
    url = "https://www2.tjal.jus.br/cpopg/open.do"
    search_url = "https://www2.tjal.jus.br/cpopg/show.do?processo.numero="

    def __init__(self, **kwargs):
        super().__init__(self.url, self.search_url)


@shared_task(bind=True, base=BaseTaskWithRetry)
def capture_task(self, cnj: str, batch_line_id: str, uid: str):
    from zordon.models import BatchLine

    self.update_state(state="STARTED", meta={"user_id": uid})
    status, lawsuit_data = RobotAL().capture_pipeline(cnj)
    BatchLine.objects.get(id=batch_line_id).update_status(status)
