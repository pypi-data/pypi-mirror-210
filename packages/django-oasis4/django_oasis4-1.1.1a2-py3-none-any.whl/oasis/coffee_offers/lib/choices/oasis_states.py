# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         26/02/23 15:31
# Project:      CFHL Transactional Backend
# Module Name:  oasis_states
# Description:
# ****************************************************************
from django.utils.translation import gettext_lazy as _
from zibanu.django.db import models


class OasisStates(models.TextChoices):
    ACTIVE = "A", _("Active")
    PROCESSED = "P", _("Processed")
    CANCELED = "X", _("Canceled")
