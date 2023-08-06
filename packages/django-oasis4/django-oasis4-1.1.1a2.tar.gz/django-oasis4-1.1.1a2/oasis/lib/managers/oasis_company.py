# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         24/01/23 6:34 PM
# Project:      CFHL Transactional Backend
# Module Name:  oasis_company
# Description:
# ****************************************************************
from oasis import models as oasis_models
from zibanu.django.db import models
from zibanu.django.db.models import Subquery, OuterRef


class OasisCompany(models.Manager):
    def get_for_sync(self):
        qs = self.model.objects.annotate(
            representative=Subquery(
                oasis_models.Client.objects.filter(clientid__exact=OuterRef("clientid")).values("representative")[:1]
            )
        ).values("companyid", "companyname", "companycode", "address", "phone", "city", "representative").all()
        return qs

