# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         26/02/23 15:26
# Project:      CFHL Transactional Backend
# Module Name:  coffee_offers_states
# Description:
# ****************************************************************
from django.utils.translation import gettext_lazy as _
from zibanu.django.db import models


class CoffeeOffersStates(models.IntegerChoices):
    NEW = 0, _("New")
    CHANGED = 1, _("Changed")
    SIGNED = 2, _("Signed")
    PARTIAL = 3, _("Partial")
    FINISHED = 4, _("Finished")
    REJECTED = 9, _("Rejected")

    @classmethod
    def active_list(cls) -> list:
        return [cls.SIGNED, cls.PARTIAL]

    @classmethod
    def ended_list(cls) -> list:
        return [cls.FINISHED, cls.REJECTED]

    @classmethod
    def not_ended_list(cls) -> list:
        return [cls.NEW, cls.CHANGED, cls.SIGNED, cls.PARTIAL]
