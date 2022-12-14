# Generated by Django 4.1.2 on 2022-11-06 10:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid
import zordon.constants


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BatchGenerator",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("refresh_lawsuit", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solicitation",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BatchLine",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("cnj", models.CharField(max_length=25)),
                ("uf", models.CharField(max_length=3)),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[
                            (1, "PENDING"),
                            (2, "SUCCESS"),
                            (3, "ERROR"),
                            (4, "NOT_FOUND"),
                        ],
                        default=zordon.constants.LINE_STATUS["PENDING"],
                    ),
                ),
                ("details", models.TextField(null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(null=True)),
                (
                    "generator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lines",
                        to="zordon.batchgenerator",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LawsuitGenerator",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("instance", models.SmallIntegerField()),
                ("value", models.TextField(null=True)),
                ("lawsuit_class", models.TextField(null=True)),
                ("subject", models.TextField(null=True)),
                ("distribution", models.TextField(null=True)),
                ("area", models.TextField(null=True)),
                ("judge", models.TextField(null=True)),
                (
                    "batch_line",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lawsuits",
                        to="zordon.batchline",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LawsuitPart",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("participation", models.TextField(null=True)),
                ("person", models.TextField(null=True)),
                (
                    "lawsuit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="parts",
                        to="zordon.lawsuitgenerator",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LawsuitRelatedPart",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("participation", models.TextField(null=True)),
                ("person", models.TextField(null=True)),
                (
                    "related_part",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="relateds",
                        to="zordon.lawsuitpart",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LawsuitProgress",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("date", models.TextField(null=True)),
                ("description", models.TextField(null=True)),
                (
                    "lawsuit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="movements",
                        to="zordon.lawsuitgenerator",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BatchConsultation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("public", models.BooleanField(default=False)),
                (
                    "generator",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consultation",
                        to="zordon.batchgenerator",
                    ),
                ),
            ],
        ),
    ]
