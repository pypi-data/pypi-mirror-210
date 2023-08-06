# -*- coding: utf-8 -*-

#   Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#   Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE: PyCharm
# Developed by: JhonyAlexanderGonzal
# Date: 23/05/2023 11:24 a. m.
# Project: cfhl-backend
# Module Name: cursor
# ****************************************************************

from django.core.exceptions import ValidationError
from django.db import connections
from django.utils.translation import gettext_lazy as _
from oasis.models import Stat


class Cursor:
    connection_name = "default"

    @classmethod
    def __execute_query(cls, query: str, *args):
        new_args = tuple()
        if isinstance(query, str):
            if "%s" in query:
                if len(args) <= 0:
                    raise ValueError(_("The arguments required for the query were not received."))
                else:
                    count = query.count("%s")
                    new_args = tuple()
                    for i in range(0, count):
                        new_args = new_args + (args[i],)

            cursor = connections[cls.connection_name].cursor()
            cursor.execute(query, new_args)
            columns = [col[0].lower() for col in cursor.description]
            raw_data = [
                dict(zip(columns, row)) for row in cursor.fetchall()
            ]
        else:
            raise ValueError(_("The query text must be string type."))
        return raw_data

    @classmethod
    def generate_stat(cls, sql: str, *args) -> list:
        try:
            dataset = cls.__execute_query(sql, *args)
        except Stat.DoesNotExist:
            raise ValidationError(_("Stat key does not exist."))
        except Exception as exc:
            raise
        else:
            return dataset
