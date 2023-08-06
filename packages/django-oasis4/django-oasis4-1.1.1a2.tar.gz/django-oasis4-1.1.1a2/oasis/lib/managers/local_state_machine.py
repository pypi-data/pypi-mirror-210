# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         8/03/23 9:01
# Project:      CFHL Transactional Backend
# Module Name:  local_state_machine
# Description:
# ****************************************************************
from typing import Any
from zibanu.django.db import models


class StateMachine(models.Manager):
    def get_next_state(self, from_state: int, oasis_state: str, oasis_status: str) -> models.Model:
        """
        Method to get next state value based on current states.
        :param from_state: from what state start search
        :param oasis_state: oasis current state
        :param oasis_status: oasis current status
        :return: state record
        """
        state = self.filter(from_state__exact=from_state, oasis_state__exact=oasis_state,
                            oasis_status__exact=oasis_status, update_oasis__exact=False).first()
        return state

    def get_next_oasis_status(self, from_state: int, new_state: int) -> models.Model:
        """
        Get next oasis status for set a new offer status
        :param from_state: from start state search
        :param new_state: new state to set
        :return: state record
        """
        state = self.filter(from_state__exact=from_state, state__exact=new_state, update_oasis__exact=True).first()
        return state

    def get_current_state(self, current_state: int, oasis_state: str, oasis_status: str) -> models.Model:
        """
        Get current state record
        :param current_state: current offer state
        :param oasis_state: current oasis operation state
        :param oasis_status: current oasis operation status
        :return: state record
        """
        state = self.filter(state__exact=current_state, oasis_state__exact=oasis_state,
                            oasis_status__exact=oasis_status).first()
        return state
