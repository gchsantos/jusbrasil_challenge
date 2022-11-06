from rest_framework import serializers

from .models import BatchLine


class BatchLinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchLine
        fields = ["cnj", "uf"]
