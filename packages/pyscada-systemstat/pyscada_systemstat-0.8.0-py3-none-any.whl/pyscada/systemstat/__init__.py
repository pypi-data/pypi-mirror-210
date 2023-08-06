# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada import core

__version__ = "0.8.0"
__author__ = "Martin Schröder, Camille Lavayssiere"
__email__ = "team@pyscada.org"
__description__ = "Systemstat extension for PyScada a Python and Django based Open Source SCADA System"
__app_name__ = "SystemStat"

PROTOCOL_ID = 2

parent_process_list = [{'pk': PROTOCOL_ID,
                        'label': 'pyscada.systemstat',
                        'process_class': 'pyscada.systemstat.worker.Process',
                        'process_class_kwargs': '{"dt_set":30}',
                        'enabled': True}]
