# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         6/03/23 16:34
# Project:      CFHL Transactional Backend
# Module Name:  sync_coffe_offers
# Description:
# ****************************************************************
from core import celery_app
from django.conf import settings
from oasis.coffee_offers.lib.utils import OfferStateMachine
from oasis.models import Offer
from oasis.models import Operation
from typing import Any


@celery_app.task(bind=True)
def sync_coffee_offers(app: Any):
    document_id = settings.COFFEE_OFFERS_DOCUMENT

    offer_qs = Offer.objects.get_all_active_offers()
    for offer in offer_qs:
        operation = Operation.objects.get_by_operation_pk(document_id=document_id,
                                                          location_id=offer.warehouse.location_id,
                                                          number_id=offer.contract).first()
        if operation is not None:
            state_machine = OfferStateMachine(offer, operation)
            state_machine.run()
            state_machine.validate_timeout()
