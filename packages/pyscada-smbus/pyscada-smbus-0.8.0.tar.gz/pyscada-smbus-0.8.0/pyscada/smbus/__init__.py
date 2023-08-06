# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada import core

__version__ = "0.8.0"
__author__ = "Martin Schröder, Camille Lavayssiere"
__email__ = "team@pyscada.org"
__description__ = "SMBus extension for PyScada a Python and Django based Open Source SCADA System"
__app_name__ = "SMBus"

PROTOCOL_ID = 8

parent_process_list = [{'pk': PROTOCOL_ID,
                        'label': 'pyscada.smbus',
                        'process_class': 'pyscada.smbus.worker.Process',
                        'process_class_kwargs': '{"dt_set":30}',
                        'enabled': True}]
