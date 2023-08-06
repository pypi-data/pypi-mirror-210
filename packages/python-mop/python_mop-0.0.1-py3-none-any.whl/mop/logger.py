# -*- coding: utf-8 -*-
# Copyright (c) CDU

"""logger module

"""

from __future__ import absolute_import
from __future__ import annotations
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__all__ = ['unusual_backtracking']

import logging
import traceback

logger = logging.getLogger('mop')
logger.setLevel(logging.WARNING)
logger.propagate = False
logger.addHandler(logging.StreamHandler())


def unusual_backtracking(e):
    logger.warning(e)
    logger.debug("".join(traceback.TracebackException.from_exception(e).format(chain=True)))