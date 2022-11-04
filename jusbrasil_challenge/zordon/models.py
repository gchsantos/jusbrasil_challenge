import uuid
from typing import List, Dict

from django.db import models
from django.contrib.auth.models import User

from .constants import LINE_STATUS
from robots.core.constants import ROBOTS_HANDLER_MAP


class BatchGenerator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    refresh_lawsuit = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="solicitation"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def generate(
        self, generator_cnjs: Dict[str, List["BatchLine"]], public_consultation: bool
    ):
        grouped_batch_lines: Dict[str, List[BatchLine]] = dict()

        for uf in generator_cnjs:
            [setattr(gen_cnj, "generator", self) for gen_cnj in generator_cnjs[uf]]
            grouped_batch_lines[uf] = BatchLine.objects.bulk_create(generator_cnjs[uf])

        for uf in grouped_batch_lines:
            [
                ROBOTS_HANDLER_MAP[uf].delay(
                    batch_line.cnj, batch_line.id, self.user.id
                )
                for batch_line in grouped_batch_lines[uf]
            ]

        BatchConsultation.objects.create(generator=self, public=public_consultation)

    def has_finished(self) -> bool:
        return False if self.batch_lines.filter(status=LINE_STATUS.PENDING) else True


class BatchLine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cnj = models.CharField(max_length=25)
    uf = models.CharField(max_length=3)
    generator = models.ForeignKey(
        BatchGenerator, on_delete=models.CASCADE, related_name="lines"
    )
    status = models.SmallIntegerField(
        choices=LINE_STATUS.get_status(), default=LINE_STATUS.PENDING
    )
    details = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)

    def get_line_status(self) -> LINE_STATUS:
        return LINE_STATUS(self.status).name

    def update_status(self, status: LINE_STATUS):
        self.status = status
        self.save()


class BatchConsultation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generator = models.OneToOneField(
        BatchGenerator, on_delete=models.CASCADE, related_name="consultation"
    )
    public = models.BooleanField(default=False)
