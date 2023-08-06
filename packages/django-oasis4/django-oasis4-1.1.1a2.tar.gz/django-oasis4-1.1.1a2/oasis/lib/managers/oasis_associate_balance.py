# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         1/03/23 11:45
# Project:      CFHL Transactional Backend
# Module Name:  oasis_associate_balance
# Description:
# ****************************************************************
from datetime import timedelta
from django.utils import timezone
from zibanu.django.db import models


class AssociateBalance(models.Manager):
    def get_quota(self, customer_id: int, year: int = None, month: int = None) -> float:
        now = timezone.now() + timedelta(days=-30)
        # Set year and month
        if year is None:
            year = now.year
        if month is None:
            month = now.month

        # Get QUOTA
        record = self.filter(clientid__exact=customer_id, year__exact=year, period__exact=month).first()
        if record is not None:
            quota = record.areacoffeeproductive
        else:
            quota = 0

        return quota
