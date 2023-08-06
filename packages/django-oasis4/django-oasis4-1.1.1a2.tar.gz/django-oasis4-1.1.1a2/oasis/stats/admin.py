# -*- coding: utf-8 -*-

# ****************************************************************
# IDE: PyCharm
# Developed by: JhonyAlexanderGonzal
# Date: 18/05/2023 4:21 p. m.
# Project: cfhl-backend
# Module Name: admin
# ****************************************************************

from django.contrib import admin
from oasis.models import Stat


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    pass
