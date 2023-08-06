# -*- coding: utf-8 -*-

# ****************************************************************
# IDE: PyCharm
# Developed by: JhonyAlexanderGonzal
# Date: 19/05/2023 8:25 a. m.
# Project: cfhl-backend
# Module Name: stats
# ****************************************************************

from oasis.models import Stat
from zibanu.django.rest_framework import serializers


class StatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stat
        fields = ("id", "name", "is_staff")
