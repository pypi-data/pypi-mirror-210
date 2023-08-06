# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         26/02/23 15:43
# Project:      CFHL Transactional Backend
# Module Name:  oasis_statuses
# Description:
# ****************************************************************
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_oasis_statuses(value: str) -> None:
    if value not in settings.COFFEE_OFFERS_STATUSES:
        raise ValidationError(_("Invalid Coffe Order - Oasis Status"))
