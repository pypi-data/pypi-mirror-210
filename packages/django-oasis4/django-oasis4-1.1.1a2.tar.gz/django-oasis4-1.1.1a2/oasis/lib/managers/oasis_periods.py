# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         4/02/23 18:35
# Project:      CFHL Transactional Backend
# Module Name:  oasis_periods
# Description:
# ****************************************************************
from zibanu.django.db import models


class Periods(models.Manager):
    def is_open(self, year: int, period: int = 12) -> bool:
        b_return = False
        period = 12 if period == 0 else period
        if 1 <= period <= 12:
            qs = self.filter(year__exact=year, period__exact=period)
            if qs.count() > 0:
                periods = qs.first()
                b_return = periods.open
        return b_return
