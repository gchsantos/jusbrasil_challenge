import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jusbrasil_challenge.settings")

app = Celery("jusbrasil_challenge")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.task_routes = (
    [
        ("robots.al.*", {"queue": "batch_al"}),
        ("robots.ce.*", {"queue": "batch_ce"}),
    ],
)
