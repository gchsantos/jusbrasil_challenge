import json
from typing import List, Dict

from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from dacite import from_dict
from dacite.exceptions import MissingValueError

from .serializers import BatchLinesSerializer
from .messages import (
    BatchInsertDataMessage,
    BatchInsertDataReturnMessage,
    BatchConsultationReturnMessage,
)
from .models import BatchGenerator, BatchLine, BatchConsultation
from .exceptions import (
    UnsupportedCNJException,
    MissingValueException,
    BaseException,
    BatchConsultationException,
)
from .utils.cnj_utils import get_uf_by_cnj


class BatchManager(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        try:
            try:
                insert_message = from_dict(
                    data_class=BatchInsertDataMessage, data=request.data
                )
            except MissingValueError as e:
                return Response(
                    MissingValueException(str(e)).message,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            generator_cnjs: Dict[str, List[BatchLine]] = dict()

            for cnj in insert_message.cnjs:
                try:
                    uf = get_uf_by_cnj(cnj)
                    if not uf:
                        raise UnsupportedCNJException(cnj)

                    generator_cnjs.setdefault(uf, []).append(BatchLine(cnj=cnj, uf=uf))
                except (UnsupportedCNJException, ValueError) as e:
                    message = (
                        e.message
                        if hasattr(e, "message")
                        else UnsupportedCNJException(cnj).message
                    )
                    return Response(
                        message,
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            with transaction.atomic():
                generator = BatchGenerator.objects.create(
                    refresh_lawsuit=insert_message.refresh_lawsuit,
                    user=request.user,
                )
                generator.generate(generator_cnjs, insert_message.public_consultation)

            return_message = json.loads(
                BatchInsertDataReturnMessage(generator.consultation.id).to_json()
            )
            return Response(return_message, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                BaseException(str(e)).message,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ConsultationManager(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        consultation_id = kwargs.get("consultation_id")

        try:
            if not consultation_id:
                raise BatchConsultationException(
                    "Parameter 'consultation_id' is required"
                )

            try:
                consultation = BatchConsultation.objects.get(id=consultation_id)
            except ValidationError:
                raise BatchConsultationException(
                    f"'{consultation_id}' is not a valid UUID"
                )
            except BatchConsultation.DoesNotExist:
                return_message = json.loads(
                    BatchConsultationReturnMessage(consultation_id).to_json()
                )
                return Response(return_message, status=status.HTTP_404_NOT_FOUND)

            if consultation.public or consultation.generator.user == request.user:
                lines = BatchLinesSerializer(
                    consultation.generator.lines.all(), many=True
                )
            else:
                ...

        except BatchConsultationException as e:
            return Response(
                e.message,
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                BatchConsultationException(str(e)).message,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        messageObj = BatchConsultationReturnMessage(consultation_id, lines.data)
        message = json.loads(messageObj.to_json())
        message["batchConsultations"] = lines.data

        return Response(message, status=status.HTTP_200_OK)
