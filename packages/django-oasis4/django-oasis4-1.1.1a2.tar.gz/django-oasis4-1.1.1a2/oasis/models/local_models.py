# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         10/12/22 3:52 PM
# Project:      CFHL Transactional Backend
# Module Name:  own_models
# Description:
# ****************************************************************
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from oasis.coffee_offers.lib.choices import CoffeeOffersStates
from oasis.coffee_offers.lib.validators import greater_than_today
from oasis.coffee_offers.lib.validators import validate_oasis_statuses
from oasis.lib import managers
from zibanu.django.db import models


class Company(models.Model):
    """
    Model class to represent entity Company.
    """
    company_id = models.IntegerField(blank=False, null=False, verbose_name=_("Company Id"))
    name = models.CharField(max_length=100, blank=False, null=False, verbose_name=_("Company Name"))
    tax_id = models.CharField(max_length=30, blank=False, null=False, verbose_name=_("Tax Id"))
    address = models.CharField(max_length=100, blank=False, null=False, verbose_name=_("Address"))
    phone = models.CharField(max_length=100, blank=False, null=False, verbose_name=_("Phone Number"))
    city = models.CharField(max_length=100, blank=False, null=False, verbose_name=_("City"))
    legal_representative = models.CharField(max_length=150, blank=False, null=False,
                                            verbose_name=_("Legal Representative"))
    enabled = models.BooleanField(default=True, blank=False, null=False, verbose_name=_("Enabled"))
    # Set default Manager
    objects = managers.Company()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["company_id"], name="UNQ_company_company_id")
        ]


class Product(models.Model):
    """
    Model class to represent Product entity.
    """
    product_id = models.IntegerField(blank=False, null=False, verbose_name=_("Product id"))
    name = models.CharField(max_length=250, blank=False, null=False, verbose_name=_("Product name"))
    enabled = models.BooleanField(default=True, blank=False, null=False, verbose_name=_("Is enabled"))
    # Set default manager
    objects = managers.Product()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("product_id",), name="ownproduct_productid_unique", )
        ]


class DocumentType(models.Model):
    """
    Model class to represent DocumentType entity
    """
    type_id = models.CharField(max_length=1, blank=False, null=False, verbose_name=_("Document type oasis id"))
    description = models.CharField(max_length=50, blank=False, null=False, verbose_name=_("Document type description"))
    # Set default manager
    objects = managers.DocumentType()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("type_id",), name="UNQ_document_type_id")
        ]


class CoffeeWareHouse(models.Model):
    """
    Model class to represent CoffeeWareHouse entity
    """
    location_id = models.IntegerField(null=False, blank=False, verbose_name=_("Location ID"))
    location_name = models.CharField(max_length=150, blank=False, null=False, verbose_name=_("Location Name"))
    # Default Manager
    objects = managers.CoffeeWareHouse()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("location_id",), name="UNQ_coffee_ware_house_location_id")
        ]

        indexes = [
            models.Index(fields=("location_name",), name="IDX_coffee_ware_house_location")
        ]


class StateMachine(models.Model):
    state = models.IntegerField(null=False, blank=False, verbose_name=_("State"), choices=CoffeeOffersStates.choices,
                                default=CoffeeOffersStates.NEW)
    from_state = models.IntegerField(null=True, blank=True, verbose_name=_("From State"),
                                     choices=CoffeeOffersStates.choices)
    oasis_state = models.CharField(max_length=1, null=False, blank=False, verbose_name=_("Oasis State"))
    oasis_status = models.CharField(max_length=1, null=False, blank=False, verbose_name=_("Oasis Status"),
                                    validators=[validate_oasis_statuses])
    notify_user = models.BooleanField(default=True, null=False, blank=False, verbose_name=_("Notify User"))
    notify_coffee_area = models.BooleanField(default=False, null=False, blank=False,
                                             verbose_name=_("Notify Coffee Area"))
    notify_legal_area = models.BooleanField(default=False, null=False, blank=False, verbose_name=_("Notify Legal Area"))
    is_initial = models.BooleanField(default=False, null=False, blank=False, verbose_name=_("Is initial state"))
    is_final = models.BooleanField(default=False, null=False, blank=False, verbose_name=_("Is final state"))
    is_changed = models.BooleanField(default=False, null=False, blank=False, verbose_name=_("Validate changes"))
    send_contract = models.BooleanField(default=False, null=False, blank=False, verbose_name=_("Send contract"))
    update_oasis = models.BooleanField(default=False, null=False, blank=False, verbose_name=_("Update Oasis"))
    timeout = models.IntegerField(default=0, blank=False, null=False, verbose_name=_("Timeout (hours)"))
    state_at_timeout = models.IntegerField(null=True, blank=True, verbose_name=_("State at timeout"),
                                           choices=CoffeeOffersStates.choices)

    objects = managers.StateMachine()

    def __str__(self):
        return _("Status ") + self.get_state_display()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("state", "from_state", "oasis_state", "oasis_status"),
                                    name="UNQ_CoffeeOffer_StateMachine")
        ]


class Offer(models.DatedModel):
    # Field List
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name="offers",
                             related_query_name="user")
    contract = models.IntegerField(blank=False, null=False, verbose_name=_("Contract No"))
    warehouse = models.ForeignKey(CoffeeWareHouse, null=False, blank=False, verbose_name=_("Warehouse"),
                                  on_delete=models.PROTECT, related_query_name="warehouse")
    product = models.ForeignKey(Product, null=False, blank=False, verbose_name=_("Product"), on_delete=models.PROTECT)
    kg_offered = models.DecimalField(max_digits=9, decimal_places=2, blank=False, null=False,
                                     verbose_name=_("Kg Offered"))
    kg_received = models.DecimalField(max_digits=9, decimal_places=2, blank=False, null=False, default=0,
                                      verbose_name=_("Kg Received"))
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False, null=False, default=0,
                                verbose_name=_("Price"))
    status = models.IntegerField(choices=CoffeeOffersStates.choices, default=CoffeeOffersStates.NEW, null=False,
                                 blank=False, verbose_name=_("Status"))
    delivery_date = models.DateField(blank=False, null=False, verbose_name=_("Delivery Date"),
                                     validators=[greater_than_today])
    # Set default Manager
    objects = managers.Offer()

    @property
    def is_active(self) -> bool:
        return self.status in [CoffeeOffersStates.NEW, CoffeeOffersStates.SIGNED, CoffeeOffersStates.PARTIAL]

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("contract",), name="UNQ_Offer_Contract")
        ]


class OfferMov(models.DatedModel):
    offer = models.ForeignKey(Offer, on_delete=models.PROTECT, related_name="offer_movements",
                              related_query_name="offer")
    status = models.IntegerField(choices=CoffeeOffersStates.choices, null=False, blank=False)
    delivery_date = models.DateField(blank=True, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    kg_offered = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    kg_received = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    created = models.BooleanField(default=False, blank=False, null=False)


class Stat(models.Model):
    """
    Model class to represent stats entity of the app Stats
    """
    name = models.CharField(null=False, blank=False, max_length=120, verbose_name=_("Stat name"))
    query_text = models.TextField(null=False, blank=False, verbose_name=_("Query Text"),
                                  help_text=_("Text used to execute the query"))
    is_staff = models.BooleanField(default=True, null=False, blank=False, verbose_name=_("Is staff"),
                                   help_text=_("It is required to be staff to see the stat"))
    enabled = models.BooleanField(default=True, null=False, blank=False, verbose_name=_("Enabled"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Stat")
        verbose_name_plural = _("Stats")
