# -*- coding: utf-8 -*-

# ****************************************************************
# IDE: PyCharm
# Developed by: JhonyAlexanderGonzal
# Date: 19/05/2023 8:46 a. m.
# Project: cfhl-backend
# Module Name: urls
# ****************************************************************

from oasis.stats.api import services
from django.urls import path
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()

urlpatterns = [
    path(r"list/", services.StatsServices.as_view({"post": "list"})),
    path(r"get/", services.StatsServices.as_view({"post": "get"})),
]
