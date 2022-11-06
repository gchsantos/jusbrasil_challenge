from celery import shared_task
from django.db import transaction

from .core.esaj_capture_robot import EsajCaptureRobot
from .core.task_base import BaseTaskWithRetry
from .core.dataclasses import RefinedLawsuitData
from zordon.constants import LINE_STATUS


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
    from zordon.models import BatchLine, LawsuitGenerator

    self.update_state(state="STARTED", meta={"user_id": uid})

    try:
        status, lawsuit_datas = RobotAL().capture_pipeline(cnj)

        if status == LINE_STATUS.SUCCESS:
            with transaction.atomic():
                for lawsuit_data in lawsuit_datas:
                    instance = lawsuit_data["instance"]
                    refinned_lawsuit: RefinedLawsuitData = lawsuit_data[
                        "capture_response"
                    ]
                    lawsuit_generator = LawsuitGenerator.objects.create(
                        batch_line_id=batch_line_id,
                        instance=instance,
                        value=refinned_lawsuit.value,
                        lawsuit_class=refinned_lawsuit.lawsuit_class,
                        subject=refinned_lawsuit.subject,
                        distribution=refinned_lawsuit.distribution,
                        area=refinned_lawsuit.area,
                        judge=refinned_lawsuit.judge,
                    )

                    lawsuit_generator.generate(
                        refinned_lawsuit.progress_table,
                        refinned_lawsuit.concerned_parties_table,
                    )

            BatchLine.objects.get(id=batch_line_id).update_status(status)
    except Exception as e:
        if self.request.retries == self.max_retries:
            BatchLine.objects.get(id=batch_line_id).update_status(
                LINE_STATUS.ERROR, str(e)
            )
        raise
