# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         16/03/23 16:18
# Project:      CFHL Transactional Backend
# Module Name:  on_post_save_offer
# Description:
# ****************************************************************
from django.db.models.signals import post_save
from django.dispatch import receiver
from oasis.models import Offer
from oasis.models import OfferMov


@receiver(post_save, sender=Offer)
def on_post_save_offer(sender, **kwargs):
    """
    Event for signal post_save on Offer model.
    """
    instance = kwargs.get("instance", None)
    created = kwargs.get("created", False)
    offer_mov = OfferMov(offer=instance, status=instance.status, delivery_date=instance.delivery_date, price=instance.price, kg_offered=instance.kg_offered, kg_received=instance.kg_received, created=created)
    offer_mov.save()
