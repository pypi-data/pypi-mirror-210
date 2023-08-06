# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         28/01/23 9:36
# Project:      CFHL Transactional Backend
# Module Name:  local_company
# Description:
# ****************************************************************
from zibanu.django.db import models


class Company(models.Manager):
    def get_by_company_id(self, company_id: int):
        return self.filter(company_id__exact=company_id)