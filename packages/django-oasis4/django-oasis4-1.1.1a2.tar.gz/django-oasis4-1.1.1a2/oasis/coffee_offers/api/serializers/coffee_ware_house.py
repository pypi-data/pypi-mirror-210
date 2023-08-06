# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         23/02/23 10:18
# Project:      CFHL Transactional Backend
# Module Name:  coffee_ware_house
# Description:
# ****************************************************************
from oasis.models import CoffeeWareHouse
from zibanu.django.rest_framework import serializers


class CoffeeWareHouseListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CoffeeWareHouse
        fields = ("location_id", "location_name")