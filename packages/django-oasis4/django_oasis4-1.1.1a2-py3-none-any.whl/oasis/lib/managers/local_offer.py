# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         1/03/23 12:04
# Project:      CFHL Transactional Backend
# Module Name:  offer
# Description:
# ****************************************************************
from oasis.coffee_offers.lib.choices import CoffeeOffersStates
from zibanu.django.db import models
from typing import Any


class Offer(models.Manager):
    """
    Manager class for Offer entity
    """
    def get_balance(self, user: Any) -> float:
        """
        Method to return a balance from active offers in entity
        :param user: Offers owner
        :return: balance
        """
        qs = self.get_active_offers(user)
        balance = 0
        if qs is not None:
            for offer in qs:
                balance = balance + (offer.kg_offered - offer.kg_received)
        return balance

    def get_active_offers(self, user: Any) -> models.QuerySet:
        """
        Method to return a queryset with only active offers
        :param user: Offers owner
        :return: filtered queryset
        """
        states = CoffeeOffersStates.not_ended_list()

        qs = self.filter(user__exact=user, status__in=states)

        return qs

    def get_all_active_offers(self):
        return self.filter(status__in=CoffeeOffersStates.not_ended_list())
