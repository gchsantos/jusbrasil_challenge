import uuid
from typing import List

from django.db import models
from django.contrib.auth.models import User

from .constants import LINE_STATUS
from .types import GeneratorCnjs


class BatchGenerator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    refresh_lawsuit = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="solicitation"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def generate(self, cnjs: List[GeneratorCnjs], public_consultation: bool):
        for gen_cnj in cnjs:
            BatchLine.objects.create(
                cnj=gen_cnj["cnj"], uf=gen_cnj["uf"], generator=self
            )

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
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)

    def get_line_status(self) -> LINE_STATUS:
        return LINE_STATUS(self.status).name


class BatchConsultation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generator = models.OneToOneField(
        BatchGenerator, on_delete=models.CASCADE, related_name="consultation"
    )
    public = models.BooleanField(default=False)
