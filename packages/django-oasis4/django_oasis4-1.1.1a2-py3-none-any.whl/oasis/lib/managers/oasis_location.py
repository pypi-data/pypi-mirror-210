# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         23/02/23 9:16
# Project:      CFHL Transactional Backend
# Module Name:  oasis_location
# Description:
# ****************************************************************
from zibanu.django.db import models


class OasisLocation(models.Manager):
    """
    Manager class of Location class entity
    """
    def get_coffe_ware_houses(self):
        qs = self.get_queryset().filter(businessid__exact=1, level__exact=2, pointofsales__exact=1)
        return qs


