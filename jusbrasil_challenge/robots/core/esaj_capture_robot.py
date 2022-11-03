from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


class EsajCaptureRobot:
    def __init__(self, url, **kwargs) -> None:
        super().__init__(**kwargs)
        self.url = url

    def capture_pipeline(self, cnj: str, batch_line_id: str, uid: str):
        ...

    def search_lawsuit_by_cnj(self, cnj: str) -> str:
        ...
