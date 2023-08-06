# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         22/02/23 9:18
# Project:      CFHL Transactional Backend
# Module Name:  apps
# Description:
# ****************************************************************
from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class OasisCoffeeOffer(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "oasis.coffee_offers"
    label = "coffee_offer"
    verbose_name = _("Oasis4 Coffee Offer ")

    def ready(self):
        """
        Method loaded on ready event pre_load application
        :return: None
        """
        # Import events for signals
        import oasis.coffee_offers.lib.events
        # Document ID to save Coffee Offer
        settings.COFFEE_OFFERS_DOCUMENT = getattr(settings, "COFFEE_OFFERS_DOCUMENT", "OA")
        # Concept ID to save Coffee Offer
        settings.COFFEE_OFFERS_CONCEPT = getattr(settings, "COFFEE_OFFERS_CONCEPT", "CF")
        # Discount ID to save Coffee Offer
        settings.COFFEE_OFFERS_DISCOUNT = getattr(settings, "COFFEE_OFFERS_DISCOUNT", 26)
        # Motive ID to save Coffee Offer
        settings.COFFEE_OFFERS_MOTIVE = getattr(settings, "COFFEE_OFFERS_MOTIVE", 9)
        # Max Active Offers
        settings.COFFEE_OFFERS_MAX_ACTIVE = getattr(settings, "COFFEE_OFFERS_MAX_ACTIVE", 3)
        # Set of status values for validators
        settings.COFFEE_OFFERS_STATUSES = getattr(settings, "COFFEE_OFFERS_STATUSES", "DPRTX")
        # Delta days for validate delivery dato of coffee offer
        settings.COFFEE_OFFERS_DAYS_DELTA = getattr(settings, "COFFEE_OFFERS_DAYS_DELTA", 15)
        # Segment excluded of coffee offers
        settings.COFFEE_OFFERS_LOCKED_SEGMENT = getattr(settings, "COFFEE_OFFERS_LOCKED_SEGMENT", 0)
        # Merchant segment for coffee offers
        settings.COFFEE_OFFERS_TRADER_SEGMENT = getattr(settings, "COFFEE_OFFERS_TRADER_SEGMENT", 77)
        # Merchants quota in KG
        settings.COFFEE_OFFERS_TRADER_QUOTA = getattr(settings, "COFFEE_OFFERS_TRADER_QUOTA", 30000)
        # Default quota in KG
        settings.COFFEE_OFFERS_DEFAULT_QUOTA = getattr(settings, "COFFEE_OFFERS_DEFAULT_QUOTA", 3000)
        # Calculate quota discounting active offers
        settings.COFFEE_OFFERS_CALCULATE_QUOTA = getattr(settings, "COFFEE_OFFERS_CALCULATE_QUOTA", False)
        # Delta price for minor or major value
        settings.COFFEE_OFFERS_PRICE_DELTA = getattr(settings, "COFFEE_OFFERS_PRICE_DELTA", 10)
        # Show all offers or only active
        settings.COFFEE_OFFERS_LOAD_ALL = getattr(settings, "COFFEE_OFFERS_LOAD_ALL", False)
        # Round factor
        settings.COFFEE_OFFERS_ROUND_FACTOR = getattr(settings, "COFFEE_OFFERS_ROUND_FACTOR", 10)
        # Contract Template
        settings.COFFEE_OFFERS_CONTRACT_TEMPLATE = getattr(settings, "COFFEE_OFFERS_CONTRACT_TEMPLATE",
                                                           "contract_template.html")
        # Terms and conditions template
        settings.COFFEE_OFFERS_TERMS_TEMPLATE = getattr(settings, "COFFEE_OFFERS_TERMS_TEMPLATE",
                                                        "terms_conditions.html")
        # Promissory note
        settings.COFFEE_OFFERS_PROMISE_TEMPLATE = getattr(settings, "COFFEE_OFFERS_PROMISE_TEMPLATE",
                                                          "promisory_note.html")
        # Coffee factor for offers
        settings.COFFEE_OFFERS_FACTOR = getattr(settings, "COFFEE_OFFERS_FACTOR", 94)
        # Coffee Offers product list
        settings.COFFEE_OFFERS_PRODUCT_LIST = getattr(settings, "COFFEE_OFFERS_PRODUCT_LIST",
                                                      "2101,2102,2104,2106,2107,2109,2112,2113,2114,2126,2120,2134")
