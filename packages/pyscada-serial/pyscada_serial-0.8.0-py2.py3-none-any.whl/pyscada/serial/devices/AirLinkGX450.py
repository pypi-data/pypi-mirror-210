# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.serial.devices import GenericDevice
from serial.serialutil import SerialException

import logging

logger = logging.getLogger(__name__)


class Handler(GenericDevice):
    """
    AirLink GX450 and other Devices with the same command set
    """

    def read_data(self, variable_instance):
        """
        read values from the device
        """
        if self.inst is None:
            return
        if variable_instance.serialvariable.device_property.upper() == 'SMSM2M':
            return None
        else:
            self.inst.write(str("AT" + variable_instance.serialvariable.device_property.upper() + "\r\n").encode())
            try:
                value = self.parse_value(str(self.inst.readall().decode()))
            except SerialException as e:
                logger.info("Serial Exception reading %s from %s : %s"
                            % (variable_instance.serialvariable.device_property.upper(),
                               variable_instance.device,
                               str(e)))
                value = None
            return value

    def write_data(self, variable_id, value, task):
        """
        write values to the device
        """
        variable = self._variables[variable_id]
        if variable.serialvariable.device_property.upper() == 'SMSM2M':
            return self.parse_value(str(self.inst.readall().decode()))
        try:
            value = self.parse_value(str(self.inst.readall().decode()))
        except SerialException as e:
            logger.info("Serial Exception reading %s from %s : %s"
                        % (variable.serialvariable.device_property.upper(),
                           variable.device,
                           str(e)))
            value = None
        return value

    def parse_value(self, value):
        """
        takes a string in the AirLink GX450 format and returns a float value or None if not parseable
        """
        try:
            return float(value.split()[1])
        except:
            return None
