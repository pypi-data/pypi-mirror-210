# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         23/02/23 9:38
# Project:      CFHL Transactional Backend
# Module Name:  local_coffee_ware_house
# Description:
# ****************************************************************
from zibanu.django.db import models


class CoffeeWareHouse(models.Manager):
    """
    Manager class for CoffeeWarehouse entity
    """
    def get_by_location_id(self, location_id: int):
        return self.get_queryset().filter(location_id__exact=location_id)