# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         7/02/23 3:56
# Project:      CFHL Transactional Backend
# Module Name:  oasis_cycle
# Description:
# ****************************************************************
from oasis.models import Cycle
from zibanu.django.rest_framework import serializers


class CycleSerializer(serializers.ModelSerializer):
    """
    Cycle serializer for obtain availables cycles by type
    """

    class Meta:
        model = Cycle
        fields = ("year", "cycle")