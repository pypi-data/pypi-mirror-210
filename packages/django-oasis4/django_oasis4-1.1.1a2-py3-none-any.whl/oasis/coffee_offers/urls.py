# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         23/02/23 10:12
# Project:      CFHL Transactional Backend
# Module Name:  urls
# Description:
# ****************************************************************
from oasis.coffee_offers.api import services
from django.urls import path
from rest_framework.routers import DefaultRouter

routers = DefaultRouter()

urlpatterns = [
    path(r"pre-load/", services.CoffeeOffers.as_view({"post": "pre_load"})),
    path(r"load/", services.CoffeeOffers.as_view({"post": "load_offer"})),
    path(r"change-status/", services.CoffeeOffers.as_view({"post": "change_status"})),
    path(r"sign/", services.CoffeeOffers.as_view({"post": "sign_offer"}))
]
