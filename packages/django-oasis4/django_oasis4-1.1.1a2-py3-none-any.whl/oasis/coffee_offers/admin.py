# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         6/03/23 14:36
# Project:      CFHL Transactional Backend
# Module Name:  admin
# Description:
# ****************************************************************
from django.contrib import admin
from oasis.coffee_offers.admin_views import StateMachineAdmin
from oasis.models import StateMachine

admin.site.register(StateMachine, StateMachineAdmin)
