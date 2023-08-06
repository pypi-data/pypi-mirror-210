# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable
from pyscada.serial.models import SerialDevice, SerialVariable, ExtendedSerialVariable, \
    ExtendedSerialDevice

from django.dispatch import receiver
from django.db.models.signals import post_save

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SerialDevice)
@receiver(post_save, sender=SerialVariable)
@receiver(post_save, sender=ExtendedSerialVariable)
@receiver(post_save, sender=ExtendedSerialDevice)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is SerialDevice:
        post_save.send_robust(sender=Device, instance=instance.serial_device)
    elif type(instance) is SerialVariable:
        post_save.send_robust(sender=Variable, instance=instance.serial_variable)
    elif type(instance) is ExtendedSerialVariable:
        post_save.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedSerialDevice:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))
