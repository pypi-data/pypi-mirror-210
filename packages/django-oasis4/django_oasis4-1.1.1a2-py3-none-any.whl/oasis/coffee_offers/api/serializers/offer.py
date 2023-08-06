# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         6/03/23 13:54
# Project:      CFHL Transactional Backend
# Module Name:  offers_serializer
# Description:
# ****************************************************************
from oasis.models import Offer
from zibanu.django.rest_framework import serializers


class OfferListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d")
    warehouse = serializers.CharField(source="warehouse.location_name")
    status_desc = serializers.SerializerMethodField()
    product = serializers.CharField(source="product.name")

    def get_status_desc(self, instance):
        return instance.get_status_display()

    class Meta:
        model = Offer
        fields = ("id", "contract", "created_at", "delivery_date", "kg_offered", "kg_received", "price",
                  "warehouse", "status", "status_desc", "product")

