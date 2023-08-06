# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         6/03/23 16:24
# Project:      CFHL Transactional Backend
# Module Name:  offer_state_machine
# Description:
# ****************************************************************
from datetime import timedelta
from django.utils import timezone
from django.db import DatabaseError
from django.utils.translation import gettext_lazy as _
from oasis.models import Operation
from oasis.models import StateMachine


class OfferStateMachine:
    def __init__(self, offer, operation):
        self.__offer = offer
        self.__operation = operation
        self.__from_status = offer.status

    def run(self) -> None:
        """
        Run a machine state to get and assign next state value.
        :return:
        """
        oasis_state = self.__operation.state
        oasis_status = self.__operation.status
        state = StateMachine.objects.get_next_state(from_state=self.__from_status, oasis_state=oasis_state,
                                                    oasis_status=oasis_status)
        if state is not None:
            self.__offer.status = state.state
            # Change kg received
            if self.__offer.kg_received != self.__operation.quantity:
                self.__offer.kg_received = self.__operation.quantity

            if state.is_changed:
                # Change kg offered
                if self.__offer.kg_offered != self.__operation.otherif:
                    self.__offer.kg_offered = self.__operation.otherif
                # Change delivery date
                if self.__offer.delivery_date != self.__operation.finaldate:
                    self.__offer.delivery_date = self.__operation.finaldate

            self.__offer.save()

    def set(self, new_state: int) -> None:
        """
        Set a new state and assign state and status in oasis operation entity
        :param new_state: new state value
        :return:
        """
        state = StateMachine.objects.get_next_oasis_status(from_state=self.__offer.status, new_state=new_state)

        if state is not None:
            if Operation.objects.update_status(location_id=self.__operation.locationid,
                                               document_id=self.__operation.documentid,
                                               number_id=self.__operation.numberid, state=state.oasis_state,
                                               status=state.oasis_status):
                self.__offer.status = new_state
                self.__offer.save()
            else:
                raise DatabaseError(_("Error updating operation record"))

    def validate_timeout(self) -> None:
        """
        Validate a state timeout and set a new state.
        :return:
        """
        now = timezone.now()
        state = StateMachine.objects.get_current_state(current_state=self.__offer.status, oasis_state=self.__operation.state, oasis_status=self.__operation.status)
        if state is not None and state.timeout > 0:
            if (now - self.__offer.modified_at) > timedelta(hours=state.timeout):
                self.set(state.state_at_timeout)

