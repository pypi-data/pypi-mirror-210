# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         24/01/23 5:55 PM
# Project:      CFHL Transactional Backend
# Module Name:  sync_company
# Description:
# ****************************************************************
from core import celery_app
from oasis import models
from typing import Any


@celery_app.task(bind=True)
def sync_company(app: Any):
    oasis_qs = models.OasisCompany.objects.get_for_sync()
    if oasis_qs.count() > 0:
        # Get dataDict
        oasis_company = oasis_qs.first()
        # Validate if company exists
        company_qs = models.Company.objects.filter(company_id__exact=oasis_company.get("companyid"))
        if company_qs.count() == 0:
            company = models.Company(company_id=oasis_company.get("companyid"))
        else:
            company = company_qs.first()

        company.name = oasis_company.get("companyname")
        company.legal_representative = oasis_company.get("representative")
        company.tax_id = oasis_company.get("companycode")
        company.address = oasis_company.get("address")
        company.phone = oasis_company.get("phone")
        company.city = oasis_company.get("city")
        company.save()



