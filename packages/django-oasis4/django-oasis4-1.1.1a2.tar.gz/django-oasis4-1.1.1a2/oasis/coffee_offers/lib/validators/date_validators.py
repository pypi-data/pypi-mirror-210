# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         26/02/23 16:03
# Project:      CFHL Transactional Backend
# Module Name:  date_validators
# Description:
# ****************************************************************
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def eq_greater_than_today(value: datetime) -> None:
    now_datetime = datetime.now()
    now_date = datetime(now_datetime.year, now_datetime.month, now_datetime.day)
    source_date = datetime(value.year, value.month, value.day)

    if source_date < now_date:
        raise ValidationError(_("Received date is less than current date"))


def greater_than_today(value: datetime) -> None:
    now_datetime = datetime.now()
    now_date = datetime(now_datetime.year, now_datetime.month, now_datetime.day)
    source_date = datetime(value.year, value.month, value.day)

    if source_date <= now_date:
        raise ValidationError(_("Received date is less than or equal to current date"))
