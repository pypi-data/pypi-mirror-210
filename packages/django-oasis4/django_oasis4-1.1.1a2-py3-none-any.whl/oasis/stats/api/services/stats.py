# -*- coding: utf-8 -*-

# ****************************************************************
# IDE: PyCharm
# Developed by: JhonyAlexanderGonzal
# Date: 18/05/2023 5:23 p. m.
# Project: cfhl-backend
# Module Name: stats
# ****************************************************************

from oasis.models import Stat
from oasis.stats.api.serializers import StatSerializer
from rest_framework import status
from rest_framework.response import Response
from zibanu.django.rest_framework.exceptions import APIException
from zibanu.django.rest_framework.viewsets import ViewSet
from zibanu.django.utils import ErrorMessages
from zibanu.django.rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from oasis.stats.lib.cursors import Cursor
from django.core.exceptions import ValidationError as CoreValidationError


class StatsServices(ViewSet):

    def list(self, request) -> Response:
        """
        REST Service to get a list of stats.
        :param request: request object from HTTP Post.
        :return: response object with status and data.
        """
        try:
            qs = Stat.objects.filter(enabled=True)
            serializer = StatSerializer(instance=qs, many=True)
            data_return = serializer.data
            status_return = status.HTTP_200_OK if len(data_return) > 0 else status.HTTP_204_NO_CONTENT
        except Exception as exc:
            raise APIException(ErrorMessages.NOT_CONTROLLED, str(exc),
                               http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status_return, data=data_return)

    def get(self, request) -> Response:
        """
        REST Service to get a stat for id.
        :param request: request object from HTTP Post.
        :return: response object with status and data.
        """
        try:
            # Get user
            user = self._get_user(request)
            request.user = user

            if not hasattr(user, "profile"):
                raise ValidationError(_("The user is not registered."), code=status.HTTP_401_UNAUTHORIZED)

            # Set id, start_at and end_at
            if {"id", "start_at", "end_at"} <= request.data.keys():
                stat_id = request.data.get("id")
                start_at = request.data.get("start_at")
                end_at = request.data.get("end_at")

                stat = Stat.objects.get(pk=stat_id)

                if stat.is_staff:
                    if not user.is_staff:
                        raise ValidationError(_("User does not have permissions."), code=status.HTTP_401_UNAUTHORIZED)

                stat_data = Cursor.generate_stat(stat.query_text, start_at, end_at)
                if len(stat_data) > 0:
                    data_return = stat_data
                else:
                    raise ValidationError(_("No data to display."))
            else:
                raise ValidationError(_("Some json field required not found"))
        except Stat.DoesNotExist:
            raise APIException(msg=ErrorMessages.NOT_FOUND, error=_("Stat key does not exist."),
                               http_status=status.HTTP_404_NOT_FOUND)
        except CoreValidationError as exc:
            raise APIException(msg=ErrorMessages.DATA_REQUIRED, error=exc.message) from exc
        except ValidationError as exc:
            raise APIException(msg=ErrorMessages.NOT_FOUND, error=exc.detail[0]) from exc
        except Exception as exc:
            raise APIException(msg=ErrorMessages.NOT_CONTROLLED, error=str(exc)) from exc
        else:
            return Response(status=status.HTTP_200_OK, data=data_return)
