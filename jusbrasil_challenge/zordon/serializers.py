from rest_framework import serializers

from .models import (
    BatchLine,
    LawsuitGenerator,
    LawsuitProgress,
    LawsuitPart,
    LawsuitRelatedPart,
)
from .constants import LINE_STATUS


class LawsuitProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawsuitProgress
        fields = ["date", "description"]


class LawsuitRelatedPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawsuitRelatedPart
        fields = ["person", "participation"]


class LawsuitPartSerializer(serializers.ModelSerializer):
    relateds = LawsuitRelatedPartSerializer(many=True, read_only=True)

    class Meta:
        model = LawsuitPart
        fields = ["participation", "person", "relateds"]


class LawsuitSerializer(serializers.ModelSerializer):
    lawsuitClass = serializers.CharField(source="lawsuit_class")
    parts = LawsuitPartSerializer(many=True, read_only=True)
    movements = LawsuitProgressSerializer(many=True, read_only=True)

    class Meta:
        model = LawsuitGenerator
        fields = [
            "instance",
            "value",
            "lawsuitClass",
            "subject",
            "distribution",
            "area",
            "judge",
            "parts",
            "movements",
        ]


class BatchLinesSerializer(serializers.ModelSerializer):
    lawsuits = LawsuitSerializer(many=True, read_only=True)

    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")
    lineStatus = serializers.SerializerMethodField()

    class Meta:
        model = BatchLine
        fields = [
            "cnj",
            "lineStatus",
            "uf",
            "details",
            "createdAt",
            "updatedAt",
            "lawsuits",
        ]

    def get_lineStatus(self, instance):
        return LINE_STATUS(instance.status).name
