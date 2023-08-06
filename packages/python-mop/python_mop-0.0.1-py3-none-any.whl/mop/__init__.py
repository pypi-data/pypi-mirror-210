# -*- coding: utf-8 -*-
# Copyright (c) CDU

"""python toolkit for monitor-oriented programming

"""

from __future__ import absolute_import
from __future__ import annotations
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from typing import Final

from mop.monitor import MonitoringReturnValue
from mop.utils import lambda_function
from mop.utils import lambda_value
from mop.monitor import monitor

__all__ = [
    'LF', 'lf', 'lambda_function',
    'LV', 'lv', 'lambda_value',
    'MRV', 'mrv', 'MonitoringReturnValue',
    'monitor', 'monitoring'
]

LF: Final = lambda_function
LV: Final = lambda_value

lf: Final = lambda_function
lv: Final = lambda_value

mrv: Final = MonitoringReturnValue
MRV: Final = MonitoringReturnValue

monitoring: Final = monitor
