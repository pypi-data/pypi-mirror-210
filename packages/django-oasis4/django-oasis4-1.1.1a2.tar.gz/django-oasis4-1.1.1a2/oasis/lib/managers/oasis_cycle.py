# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         6/02/23 21:05
# Project:      CFHL Transactional Backend
# Module Name:  oasis_cycle
# Description:
# ****************************************************************
from django.utils.translation import gettext_lazy as _
from zibanu.django.db import models


class Cycle(models.Manager):
    def get_by_type(self, cycle_type: str) -> models.QuerySet:
        qs = self.filter(type__exact=cycle_type).order_by("year", "cycle").values("year", "cycle").distinct()
        return qs

    def get_period(self, year: int, cycle: int, cycle_type: str) -> int:
        try:
            qs = self.filter(year__exact=year, cycle__exact=cycle, type__exact=cycle_type).aggregate(period=models.Max("period"))
            period = qs.get("period")
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist(_("A record for year, cycle and cycle type does not found."))
        except Exception as exc:
            raise Exception(_("Not controlled exception at 'get_period' on Cycle manager class."))
        else:
            return period

