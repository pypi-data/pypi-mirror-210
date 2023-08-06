# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .. import PROTOCOL_ID
from pyscada.models import DeviceProtocol
from pyscada.device import GenericHandlerDevice

try: 
    import serial
    driver_ok = True
except ImportError:
    serial = None
    driver_ok = False

from time import time

import logging

logger = logging.getLogger(__name__)


class GenericDevice(GenericHandlerDevice):
    def __init__(self, pyscada_device, variables):
        super().__init__(pyscada_device, variables)
        self._protocol = PROTOCOL_ID
        self.driver_ok = driver_ok

    def connect(self):
        """
        establish a connection to the Instrument
        """
        super().connect()
        result = True

        try:
            self.inst = serial.Serial(port=self._device.serialdevice.port,
                                      baudrate=self._device.serialdevice.baudrate,
                                      bytesize=self._device.serialdevice.bytesize,
                                      parity=self._device.serialdevice.parity,
                                      stopbits=self._device.serialdevice.stopbits,
                                      timeout=self._device.serialdevice.timeout,
                                      write_timeout=self._device.serialdevice.timeout)
        except serial.serialutil.SerialException as e:
            logger.debug(e)
            result = False

        self.accessibility()
        return result

    def disconnect(self):
        if self.inst is not None:
            self.inst.close()
            self.inst = None
            return True
        return False
