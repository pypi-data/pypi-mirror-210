# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         3/03/23 16:25
# Project:      CFHL Transactional Backend
# Module Name:  oasis_operation
# Description:
# ****************************************************************
import cx_Oracle
from datetime import datetime
from django.conf import settings
from django.db import connections
from django.db import DatabaseError
from django.utils.translation import gettext_lazy as _
from oasis import models as oasis_models

from typing import Any
from zibanu.django.db import models


class Operation(models.Manager):
    connection_name = "oasis"

    def __get_cursor(self):
        return connections[self.connection_name].cursor()

    def __get_connection(self):
        return connections[self.connection_name]

    def get_by_operation_pk(self, document_id: str, location_id: int, number_id: int) -> models.QuerySet:
        """
        Return an operation with oasis pk filter
        :param document_id: Document id
        :param location_id: Location id
        :param number_id: Document number id
        :return: Queryset
        """
        return self.filter(companyid__exact=settings.OASIS_DEFAULT_COMPANY, locationid__exact=location_id,
                           numberid__exact=number_id, documentid__startswith=document_id)

    def operation_insert(self, user: Any, product_id: int, location_id: int, amount: float, price: float, to_date: str):
        """
        Method to insert an operation record in OASIS4
        :param user:
        :param product_id:
        :param location_id:
        :param amount:
        :param price:
        :param to_date:
        :return:
        """
        # Set Queries
        operation_insert = "p_operationinsert"
        operation_insert_detail = "p_operationinsertdetail"
        # Update operation table after insertion
        update_operation = "update oasis4.operation set motiveid = :motive_id, otherif = :amount, " \
                           "initialdate = :initial_date, finaldate = :final_date, status='P' " \
                           "where companyid = :company_id and locationid = :location_id " \
                           "and numberid = :number_id and trim(documentid) = :document_id"
        # Update discount table after insertion
        update_discount = "update oasis4.discount set productid = :product_id, price= :price, " \
                          "dateinitial = :initial_date, datefinal = :final_date " \
                          "where companyid = :company_id and locationid = :location_id " \
                          "and numberid = :number_id and trim(documentid) = :document_id " \
                          "and typediscountid = :type_discount_id"
        try:
            company_id = settings.OASIS_DEFAULT_COMPANY
            contact_id = settings.OASIS_DEFAULT_COMPANY_ID
            date_now = datetime.now()
            to_date = datetime.strptime(to_date, "%Y-%m-%d")
            client_id = user.profile.document_id
            document_id = settings.COFFEE_OFFERS_DOCUMENT
            concept_id = settings.COFFEE_OFFERS_CONCEPT
            motive_id = settings.COFFEE_OFFERS_MOTIVE
            product = oasis_models.Product.objects.get(pk=product_id)

            cursor = self.__get_cursor()
            operation_number = cursor.var(cx_Oracle.NUMBER).var
            # Call operation insert procedure
            cursor.callproc(operation_insert, [
                company_id,
                document_id,
                location_id,
                concept_id,
                0,
                date_now,
                client_id,
                contact_id,
                operation_number
            ])

            if operation_number:
                # Update motive and quantity on operation table.
                number_id = operation_number.getvalue()
                cursor.execute(update_operation, {
                    "motive_id": motive_id,
                    "amount": amount,
                    "company_id": company_id,
                    "location_id": location_id,
                    "number_id": number_id,
                    "document_id": document_id,
                    "initial_date": date_now,
                    "final_date": to_date
                })
                if cursor.rowcount > 0:
                    # Execute operation_insert_detail procedure
                    cursor.callproc(operation_insert_detail, [
                        company_id,
                        document_id,
                        number_id,
                        location_id
                    ])
                    # Update product and price on discount.
                    cursor.execute(update_discount, {
                        "product_id": product.product_id,
                        "price": price,
                        "company_id": company_id,
                        "location_id": location_id,
                        "number_id": number_id,
                        "document_id": document_id,
                        "type_discount_id": settings.COFFEE_OFFERS_DISCOUNT,
                        "initial_date": date_now,
                        "final_date": to_date
                    })

                    if cursor.rowcount > 0:
                        warehouse = oasis_models.CoffeeWareHouse.objects.filter(location_id__exact=location_id).get()
                        offer = oasis_models.Offer(product=product, contract=number_id, kg_offered=amount,
                                                   delivery_date=to_date, user=user, warehouse=warehouse, price=price)
                        offer.save(force_insert=True)
                        b_return = True
                    else:
                        raise DatabaseError(_("Error updating OASIS4 database."))
                else:
                    raise DatabaseError(_("Error updating OASIS4 database."))
            else:
                raise DatabaseError(_("Error inserting OASIS4 database."))
        except Exception:
            raise
        else:
            return b_return

    def update_status(self, location_id: int, number_id: int, document_id: str, state: str, status: str) -> bool:
        company_id = settings.OASIS_DEFAULT_COMPANY
        update_operation = "update oasis4.operation set state = :state, status = :status " \
                           "where companyid = :company_id and locationid = :location_id " \
                           "and numberid = :number_id and documentid = :document_id"

        cursor = self.__get_cursor()
        cursor.execute(update_operation, {
            "state": state,
            "status": status,
            "company_id": company_id,
            "location_id": location_id,
            "number_id": number_id,
            "document_id": document_id
        })

        return cursor.rowcount == 1

