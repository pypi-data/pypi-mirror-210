# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         23/02/23 9:14
# Project:      CFHL Transactional Backend
# Module Name:  sync_coffee_ware_house
# Description:
# ****************************************************************
from core import celery_app
from oasis import models
from typing import Any


@celery_app.task(bind=True)
def sync_coffee_ware_house(app: Any):
    """
    Background task to sync coffe warehouse
    :param app: Any
    :return: None
    """
    location_qs = models.Location.objects.get_coffe_ware_houses()
    warehouse_model = models.CoffeeWareHouse
    for location in location_qs:
        warehouse = warehouse_model.objects.get_by_location_id(location.locationid).first()
        if warehouse is None:
            warehouse = warehouse_model()
            warehouse.location_id = location.locationid
        warehouse.location_name = location.locationname
        warehouse.save()



