# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, DeviceHandler
from pyscada.models import Variable
from . import PROTOCOL_ID

import serial

from django.db import models
import logging

logger = logging.getLogger(__name__)


class SerialDevice(models.Model):
    serial_device = models.OneToOneField(Device, null=True, blank=True, on_delete=models.CASCADE)
    protocol_choices = ((0, 'serial AT'),)
    protocol = models.PositiveSmallIntegerField(default=0, choices=protocol_choices)
    port = models.CharField(default='/dev/ttyAMA0',
                            max_length=400,
                            help_text="enter serial port (/dev/pts/13))")
    timeout = models.PositiveSmallIntegerField(default=0, help_text="0 use default, else value in seconds")
    stopbits_choices = ((1, 'one stopbit'),
                        (1.5, 'one point five stopbit'),
                        (2, '2 stopbits'),)
    stopbits = models.FloatField(default=serial.STOPBITS_ONE, choices=stopbits_choices)
    bytesize_choices = ((5, 'FIVEBITS'), (6, 'SIXBITS'), (7, 'SEVENBITS'), (8, 'EIGHTBITS'),)
    bytesize = models.PositiveSmallIntegerField(default=serial.EIGHTBITS, choices=bytesize_choices)
    parity_choices = ((serial.PARITY_NONE, 'NONE'), (serial.PARITY_EVEN, 'EVEN'), (serial.PARITY_ODD, 'ODD'),
                      (serial.PARITY_MARK, 'MARK'), (serial.PARITY_SPACE, 'SPACE'),)
    parity = models.CharField(default=serial.PARITY_NONE, max_length=254, choices=parity_choices)
    baudrate = models.PositiveIntegerField(default=9600, help_text="0 use default")

    protocol_id = PROTOCOL_ID

    def parent_device(self):
        try:
            return self.serial_device
        except:
            return None

    def __str__(self):
        return self.serial_device.short_name


class SerialVariable(models.Model):
    serial_variable = models.OneToOneField(Variable, null=True, blank=True, on_delete=models.CASCADE)
    device_property = models.CharField(default='present_value', max_length=255,
                                       help_text='name of the Property the variable be assigned to')

    protocol_id = PROTOCOL_ID

    def __str__(self):
        return self.id.__str__() + "-" + self.serial_variable.name


class ExtendedSerialDevice(Device):
    class Meta:
        proxy = True
        verbose_name = 'Serial Device'
        verbose_name_plural = 'Serial Devices'


class ExtendedSerialVariable(Variable):
    class Meta:
        proxy = True
        verbose_name = 'Serial Variable'
        verbose_name_plural = 'Serial Variables'
