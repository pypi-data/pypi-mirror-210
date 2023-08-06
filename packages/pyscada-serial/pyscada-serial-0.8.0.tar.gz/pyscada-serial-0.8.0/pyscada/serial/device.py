# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.device import GenericDevice
from .devices import GenericDevice as GenericHandlerDevice

from time import time, sleep

import sys

import logging
logger = logging.getLogger(__name__)

try:
    import serial
    driver_ok = True
except ImportError:
    logger.error('Cannot import serial')
    driver_ok = False


class Device(GenericDevice):
    """
    Serial device
    """

    def __init__(self, device):
        self.driver_ok = driver_ok
        self.handler_class = GenericHandlerDevice
        super().__init__(device)

        for var in self.device.variable_set.filter(active=1):
            if not hasattr(var, 'serialvariable'):
                continue
            self.variables[var.pk] = var

    def write_data(self, variable_id, value, task):
        """
        write value to a Serial Device
        """

        output = []
        if not self.driver_ok:
            logger.error("Cannot import serial")
            return output

        self._h.connect()

        if self._h.inst is None:
            return output

        output = super().write_data(variable_id, value, task)

        self._h.disconnect()

        return output
