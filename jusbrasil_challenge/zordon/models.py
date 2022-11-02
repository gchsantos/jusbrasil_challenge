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

    def generate(cls, cnjs: List[GeneratorCnjs]):
        for gen_cnj in cnjs:
            BatchLine.objects.create(
                cnj=gen_cnj["cnj"], uf=gen_cnj["uf"], generator=cls
            )


class BatchLine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cnj = models.CharField(max_length=25)
    uf = models.CharField(max_length=3)
    generator = models.ForeignKey(
        BatchGenerator, on_delete=models.CASCADE, related_name="batch_lines"
    )
    status = models.SmallIntegerField(
        choices=LINE_STATUS.get_status(), default=LINE_STATUS.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)
