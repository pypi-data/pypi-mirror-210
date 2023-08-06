# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)
_debug = 1

try:
    import RPi.GPIO as GPIO
    _DRIVER_RPI_OK = True
except (ImportError, RuntimeError):
    logger.warning("Trying to import RPi.GPIO : not on a RPi or library not installed")
    GPIO = None
    _DRIVER_RPI_OK = False

from time import time


class Device:
    """
    GPIO device
    """

    def __init__(self, device):
        self.variables = []
        self.device = device
        if _DRIVER_RPI_OK:
            GPIO.setmode(GPIO.BOARD)
            # todo add cleanup

            for var in device.variable_set.filter(active=1):
                if not hasattr(var, 'gpiovariable'):
                    continue
                self.variables.append(var)
                if var.gpiovariable.gpio_mode == 'input_pull_up':
                    GPIO.setup(int(var.gpiovariable.gpio_pin), GPIO.IN, pull_up_down=GPIO.PUD_UP)
                elif var.gpiovariable.gpio_mode == 'input_pull_down':
                    GPIO.setup(int(var.gpiovariable.gpio_pin), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                elif var.gpiovariable.gpio_mode == 'input':
                    GPIO.setup(int(var.gpiovariable.gpio_pin), GPIO.IN)
                elif var.gpiovariable.gpio_mode == 'output':
                    GPIO.setup(int(var.gpiovariable.gpio_pin), GPIO.OUT)

    def request_data(self):
        if not _DRIVER_RPI_OK:
            return None
        output = []
        for item in self.variables:
            if item.gpiovariable.gpio_mode == 'output':
                continue

            timestamp = time()
            # value = None

            value = GPIO.input(int(item.gpiovariable.gpio_pin))
            if value is not None and item.update_value(value, timestamp):
                output.append(item.create_recorded_data_element())

        return output

    def write_data(self, variable_id, value, task):
        """
        write value to single gpio pin
        """
        if not _DRIVER_RPI_OK:
            return None

        output = []

        for item in self.variables:
            if item.id == variable_id:
                if not item.gpiovariable.gpio_mode == 'output' or not item.writeable:
                    return False
                GPIO.output(int(item.gpiovariable.gpio_pin), int(value))
                if value is not None and item.update_value(value, time()):
                    output.append(item.create_recorded_data_element())
        return output
