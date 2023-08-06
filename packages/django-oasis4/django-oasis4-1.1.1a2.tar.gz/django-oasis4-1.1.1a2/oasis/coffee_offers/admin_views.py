# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         6/03/23 14:29
# Project:      CFHL Transactional Backend
# Module Name:  admin_views
# Description:
# ****************************************************************
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class StateMachineAdmin(admin.ModelAdmin):
    list_display = ("state", "from_state", "is_initial", "is_final", "update_oasis")
    fieldsets = (
        (
            _("Status Section"),
            {
                "fields": (("state", "from_state"), ("oasis_state", "oasis_status"),
                           ("is_initial", "is_final", "is_changed", "update_oasis"),
                           ("timeout", "state_at_timeout"))
            }
        ),
        (
            _("Notifications Section"),
            {
                "fields": (("notify_user", "notify_coffee_area", "notify_legal_area", "send_contract"),)
            }
        )

    )
