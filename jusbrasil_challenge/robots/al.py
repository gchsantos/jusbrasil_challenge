from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction

from .core.esaj_capture_robot import EsajCaptureRobot
from .core.task_base import BaseTaskWithRetry
from .core.dataclasses import RefinedLawsuitData
from zordon.constants import LINE_STATUS

logger = get_task_logger(__name__)


class RobotAL(EsajCaptureRobot):
    instances_urls = [
        {
            "instance": 1,
            "url": "https://www2.tjal.jus.br/cpopg/open.do",
            "show_url": "https://www2.tjal.jus.br/cpopg/show.do?processo.numero=",
        },
        {
            "instance": 2,
            "url": "https://www2.tjal.jus.br/cposg5/search.do?cbPesquisa=NUMPROC&tipoNuProcesso=UNIFICADO&dePesquisaNuUnificado=",
            "show_url": "https://www2.tjal.jus.br/cposg5/show.do?processo.codigo=",
        },
    ]

    def __init__(self, **kwargs):
        super().__init__(self.instances_urls)


@shared_task(bind=True, base=BaseTaskWithRetry)
def capture_task(self, cnj: str, batch_line_id: str, uid: str):
    from zordon.models import BatchLine, Lawsuit

    self.update_state(state="STARTED", meta={"user_id": uid})
    status, lawsuit_datas = RobotAL().capture_pipeline(cnj)

    if status == LINE_STATUS.SUCCESS:
        with transaction.atomic():
            for lawsuit_data in lawsuit_datas:
                instance = lawsuit_data["instance"]
                lawsuit: RefinedLawsuitData = lawsuit_data["capture_response"]
                lawsuit = Lawsuit.objects.create(
                    batch_line_id=batch_line_id,
                    instance=instance,
                    value=lawsuit.value,
                    lawsuit_class=lawsuit.lawsuit_class,
                    subject=lawsuit.subject,
                    distribution=lawsuit.distribution,
                    area=lawsuit.area,
                    judge=lawsuit.judge,
                )

        BatchLine.objects.get(id=batch_line_id).update_status(status)
