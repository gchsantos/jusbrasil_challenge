import uuid
from typing import List, Dict
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User

from .constants import LINE_STATUS
from robots.core.constants import ROBOTS_HANDLER_MAP
from robots.core.dataclasses import LawsuitProgress, LawsuitConcernedParts


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
    updated_at = models.DateTimeField(null=True)

    def get_line_status(self) -> LINE_STATUS:
        return LINE_STATUS(self.status).name

    def update_status(self, status: LINE_STATUS, details=None):
        self.status = status
        self.updated_at = timezone.now()
        if details:
            self.details = details
        self.save()


class BatchConsultation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    generator = models.OneToOneField(
        BatchGenerator, on_delete=models.CASCADE, related_name="consultation"
    )
    public = models.BooleanField(default=False)

    def has_lines(self) -> bool:
        return bool(self.generator.lines.first())


class LawsuitGenerator(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_line = models.ForeignKey(
        BatchLine, on_delete=models.CASCADE, related_name="lawsuits"
    )
    instance = models.SmallIntegerField()
    value = models.TextField(null=True)
    lawsuit_class = models.TextField(null=True)
    subject = models.TextField(null=True)
    distribution = models.TextField(null=True)
    area = models.TextField(null=True)
    judge = models.TextField(null=True)

    def generate(
        self,
        lawsuit_progress: List[LawsuitProgress],
        lawsuit_concerned_parts: List[LawsuitConcernedParts],
    ):
        bulk_progress = []
        for progress in lawsuit_progress:
            bulk_progress.append(
                LawsuitProgress(
                    date=progress.date,
                    description=progress.description,
                    lawsuit=self,
                )
            )
        LawsuitProgress.objects.bulk_create(bulk_progress)

        for parts in lawsuit_concerned_parts:
            part = LawsuitPart.objects.create(
                lawsuit=self,
                participation=parts.participation,
                person=parts.person,
            )

            bulk_relateds = []
            for participation, person in parts.relateds:
                bulk_relateds.append(
                    LawsuitRelatedPart(
                        related_part=part, person=person, participation=participation
                    )
                )
            LawsuitRelatedPart.objects.bulk_create(bulk_relateds)


class LawsuitProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lawsuit = models.ForeignKey(
        LawsuitGenerator, on_delete=models.CASCADE, related_name="movements"
    )
    date = models.TextField(null=True)
    description = models.TextField(null=True)


class LawsuitPart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lawsuit = models.ForeignKey(
        LawsuitGenerator, on_delete=models.CASCADE, related_name="parts"
    )
    participation = models.TextField(null=True)
    person = models.TextField(null=True)


class LawsuitRelatedPart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    related_part = models.ForeignKey(
        LawsuitPart, on_delete=models.CASCADE, related_name="relateds"
    )
    participation = models.TextField(null=True)
    person = models.TextField(null=True)
