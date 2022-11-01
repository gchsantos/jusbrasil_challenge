import json
from typing import List

from django.db import transaction
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
from .types import GeneratorCnjs


class BatchManager(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            insert_message = from_dict(
                data_class=BatchInsertDataMessage, data=request.data
            )
            generator_cnjs: List[GeneratorCnjs] = list()

            try:
                for cnj in insert_message.cnjs:
                    uf = get_uf_by_cnj(cnj)
                    if not uf:
                        raise UnsupportedCNJException(insert_message.cnjs)
                    generator_cnjs.append({"cnj": cnj, "uf": uf})

            except (UnsupportedCNJException, ValueError) as e:
                message = (
                    e.message
                    if hasattr(e, "message")
                    else UnsupportedCNJException(insert_message.cnjs).message
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
                generator.generate(generator_cnjs)

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
