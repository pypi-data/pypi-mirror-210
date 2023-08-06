# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable
from pyscada.gpio.models import GPIODevice, GPIOVariable, ExtendedGPIOVariable, ExtendedGPIODevice

from django.dispatch import receiver
from django.db.models.signals import post_save

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=GPIODevice)
@receiver(post_save, sender=GPIOVariable)
@receiver(post_save, sender=ExtendedGPIOVariable)
@receiver(post_save, sender=ExtendedGPIODevice)
def _reinit_daq_daemons(sender, instance, **kwargs):
    """
    update the daq daemon configuration when changes be applied in the models
    """
    if type(instance) is GPIODevice:
        post_save.send_robust(sender=Device, instance=instance.gpio_device)
    elif type(instance) is GPIOVariable:
        post_save.send_robust(sender=Variable, instance=instance.gpio_variable)
    elif type(instance) is ExtendedGPIOVariable:
        post_save.send_robust(sender=Variable, instance=Variable.objects.get(pk=instance.pk))
    elif type(instance) is ExtendedGPIODevice:
        post_save.send_robust(sender=Device, instance=Device.objects.get(pk=instance.pk))
