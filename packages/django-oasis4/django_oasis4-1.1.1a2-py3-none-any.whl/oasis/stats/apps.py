# -*- coding: utf-8 -*-

# ****************************************************************
# IDE: PyCharm
# Developed by: JhonyAlexanderGonzal
# Date: 18/05/2023 2:14 p. m.
# Project: cfhl-backend
# Module Name: apps
# ****************************************************************

from django.apps import AppConfig


class StatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oasis.stats'
    label = "stats"
