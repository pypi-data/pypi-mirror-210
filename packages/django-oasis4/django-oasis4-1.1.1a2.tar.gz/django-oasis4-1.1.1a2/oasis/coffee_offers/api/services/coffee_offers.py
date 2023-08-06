# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         1/03/23 10:10
# Project:      CFHL Transactional Backend
# Module Name:  coffee_offers
# Description:
# ****************************************************************
from coffee_price.models import Price
from coffee_price.api.serializers import PriceListSerializer
from datetime import datetime
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError as CoreValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from oasis.coffee_offers.api.serializers import CoffeeWareHouseListSerializer
from oasis.coffee_offers.api.serializers import OfferListSerializer
from oasis.lib.choices import CustomerType
from oasis.lib.utils import OasisActions
from oasis.models import AssociateBalance
from oasis.models import CoffeeWareHouse
from oasis.models import Offer
from oasis_auth.lib.utils import SendCode
from rest_framework import status
from rest_framework.response import Response
from zibanu.django.rest_framework.exceptions import APIException
from zibanu.django.rest_framework.exceptions import ValidationError
from zibanu.django.rest_framework import viewsets
from zibanu.django.utils import CodeGenerator
from zibanu.django.utils import ErrorMessages


class CoffeeOffers(viewsets.ViewSet):
    """
    View set for rest service of CoffeOffers module
    """
    __cache_timeout = settings.OASIS_AUTH_CODE_TIMEOUT
    __cache_timeout_seconds = __cache_timeout * 60

    def _get_quota(self, user) -> float:
        """
        Method to get a quota from user profile
        :param user: user object from request
        :return: calculated quota
        """
        # Calculate QUOTA in Kg.
        if user.profile.segment == settings.COFFEE_OFFERS_TRADER_SEGMENT:
            quota = settings.COFFEE_OFFERS_TRADER_QUOTA
        else:
            if user.profile.type == CustomerType.PARTNER:
                quota = AssociateBalance.objects.get_quota(user.profile.document_id)
            else:
                quota = settings.COFFEE_OFFERS_DEFAULT_QUOTA

        if settings.COFFEE_OFFERS_CALCULATE_QUOTA:
            quota = quota - Offer.objects.get_balance(user)

        # Round quota
        quota = int(round(quota / settings.COFFEE_OFFERS_ROUND_FACTOR)) * settings.COFFEE_OFFERS_ROUND_FACTOR
        return quota

    def _get_active_offers_count(self, user) -> int:
        """
        REturn active offers counter
        :param user: owner of offers
        :return: counter
        """
        qs = Offer.objects.get_active_offers(user=user)
        return qs.count()

    def pre_load(self, request) -> Response:
        """
        Rest service for preload all data required for frontend operation.
        :param request: request object from HTTP
        :return: Response object
        """
        try:
            now = timezone.now()
            to_date = now + timedelta(days=settings.COFFEE_OFFERS_DAYS_DELTA)
            product_list =[int(x) for x in settings.COFFEE_OFFERS_PRODUCT_LIST.split(",")]
            user = self._get_user(request)
            # Validate EXCLUDED
            if settings.COFFEE_OFFERS_LOCKED_SEGMENT != 0 and user.profile.segment == settings.COFFEE_OFFERS_LOCKED_SEGMENT:
                raise ValidationError(_("The partner/client is locked for coffee offers."))
            # Load Price List
            price_qs = Price.objects.get_products_price_by_date(date_to_search=now, product_list=product_list)
            price_serializer = PriceListSerializer(instance=price_qs, many=True,
                                                   context={"kg": True, "factor": settings.COFFEE_OFFERS_FACTOR})
            # Load Warehouse List
            warehouse_qs = CoffeeWareHouse.objects.order_by("location_name").all()
            warehouse_serializer = CoffeeWareHouseListSerializer(instance=warehouse_qs, many=True)
            # Load Offer List
            offer_qs = Offer.objects.get_active_offers(user=user)
            offer_serializer = OfferListSerializer(instance=offer_qs, many=True)

            # Calculate QUOTA in Kg.

            data_return = {
                "quota": self._get_quota(user),
                "percent": settings.COFFEE_OFFERS_PRICE_DELTA,
                "to_date": to_date,
                "offers": offer_serializer.data,
                "prices": price_serializer.data,
                "warehouses": warehouse_serializer.data
            }
            status_return = status.HTTP_200_OK
        except ValidationError as exc:
            raise APIException(error=exc.detail[0], http_status=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except Exception as exc:
            raise APIException(error=str(exc), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(status=status_return, data=data_return)

    def load_offer(self, request) -> Response:
        """
        REST service to load offer and set it pending to sign.
        :param request: request object from HTTP
        :return: Response object
        """
        try:
            if {"product", "price", "amount", "location", "to_date"} <= request.data.keys():
                today = datetime.now()
                user = self._get_user(request)
                to_date = datetime.strptime(request.data.get("to_date"), "%Y-%m-%d")

                # Validate user segment and user quota.
                if request.data.get("amount") >= self._get_quota(user):
                    raise ValidationError(_("The amount exceeds the quota available."))
                if user.profile.segment == settings.COFFEE_OFFERS_LOCKED_SEGMENT:
                    raise ValidationError(_("The partner/client is locked for coffee offers."))
                if (to_date - today) > timedelta(days=settings.COFFEE_OFFERS_DAYS_DELTA):
                    raise ValidationError(
                        _("Delivery date is greater than %s days" % settings.COFFEE_OFFERS_DAYS_DELTA))
                if self._get_active_offers_count(user=user) >= settings.COFFEE_OFFERS_MAX_ACTIVE:
                    raise ValidationError(_("You have reached max active offers quota."))

                code_generator = CodeGenerator("save_offer")
                data_cache = code_generator.generate_dict()
                cache_key = data_cache.pop("uuid").hex
                data_cache["user"] = user
                data_cache["data"] = {
                    "product": request.data.get("product"),
                    "price": request.data.get("price"),
                    "amount": request.data.get("amount"),
                    "location": request.data.get("location"),
                    "to_date": request.data.get("to_date")
                }
                email_context = {
                    "customer_name": user.get_full_name(),
                    "customer_code": data_cache.get("code"),
                }
                data_return = {
                    "token": cache_key
                }
                send_code = SendCode(to=user.email, action=data_cache.get("action"), context=email_context)
                if send_code.load_templates():
                    send_code.send()
                cache.set(cache_key, data_cache, self.__cache_timeout_seconds)
                status_return = status.HTTP_200_OK
            else:
                raise ValidationError(ErrorMessages.DATA_REQUEST_NOT_FOUND)
        except (ValidationError, CoreValidationError) as exc:
            raise APIException(error=exc.detail[0], http_status=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except Exception as exc:
            raise APIException(error=str(exc), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(status=status_return, data=data_return)

    def change_status(self, request) -> Response:
        try:
            if {"offer_id", "status"} <= request.data.keys():
                user = self._get_user(request)
                code_generator = CodeGenerator("change_status")
                data_cache = code_generator.generate_dict()
                cache_key = data_cache.pop("uuid").hex
                data_cache["user"] = user
                data_cache["data"] = {
                    "offer_id": request.data.get("offer_id"),
                    "status": request.data.get("status")
                }
                data_return = {
                    "token": cache_key
                }
                email_context = {
                    "customer_name": user.get_full_name(),
                    "customer_code": data_cache.get("code")
                }
                send_code = SendCode(to=user.email, action=data_cache.get("action"), context=email_context)
                if send_code.load_templates():
                    send_code.send()
                cache.set(cache_key, data_cache, self.__cache_timeout_seconds)
                status_return = status.HTTP_200_OK
            else:
                raise ValidationError(ErrorMessages.DATA_REQUEST_NOT_FOUND)
        except Exception as exc:
            raise APIException(error=str(exc), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(status=status_return, data=data_return)

    def sign_offer(self, request) -> Response:
        """
        Sign an offer with electronic code and run specific action
        :param request: request object from HTTP
        :return: response object
        """
        try:
            if {"token", "code"} <= request.data.keys():
                user = self._get_user(request)
                data_cache = cache.get(request.data.get("token"))
                if data_cache:
                    if request.data.get("code") == data_cache.get("code") and user == data_cache.get("user"):
                        oasis_actions = OasisActions(data_cache=data_cache)
                        result = oasis_actions.do_action()
                    else:
                        raise ValidationError(_("Code or user does not match."))
                else:
                    raise ValidationError(_("The code has expired. You have to create the offer again."))
                status_return = status.HTTP_200_OK
            else:
                raise ValidationError(ErrorMessages.DATA_REQUEST_NOT_FOUND)
        except CoreValidationError as exc:
            raise APIException(error=exc.message, http_status=status.HTTP_406_NOT_ACCEPTABLE)
        except ValidationError as exc:
            raise APIException(error=exc.detail[0], http_status=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except Exception as exc:
            raise APIException(error=str(exc), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(status=status_return)
