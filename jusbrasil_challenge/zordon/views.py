import json

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from dacite import from_dict
from dacite.exceptions import MissingValueError

from .messages import BatchInsertDataMessage, BatchInsertReturnDataMessage
from .models import BatchGenerator
from .exceptions import UnsupportedCNJException, MissingValueException, BaseException
from .utils.cnj_utils import get_uf_by_cnj


class BatchManager(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            insert_message = from_dict(
                data_class=BatchInsertDataMessage, data=request.data
            )

            try:
                uf = get_uf_by_cnj(insert_message.cnj)
                if not uf:
                    raise UnsupportedCNJException(insert_message.cnj)
            except (UnsupportedCNJException, ValueError) as e:
                message = (
                    e.message
                    if hasattr(e, "message")
                    else UnsupportedCNJException(insert_message.cnj).message
                )
                return Response(
                    message,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            batch_gen = BatchGenerator(
                cnj=insert_message.cnj,
                refresh_lawsuit=insert_message.refresh_lawsuit,
                user=request.user,
            )
            batch_gen.save()

            return_message = json.loads(BatchInsertReturnDataMessage(1).to_json())

            return Response(return_message, status=status.HTTP_200_OK)

        except MissingValueError as e:
            return Response(
                MissingValueException(str(e)).message,
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                BaseException(str(e)).message,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
