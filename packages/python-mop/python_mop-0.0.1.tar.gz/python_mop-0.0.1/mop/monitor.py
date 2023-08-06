# -*- coding: utf-8 -*-
# Copyright (c) CDU

"""Model Docstrings

"""

from __future__ import absolute_import
from __future__ import annotations
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools
from typing import Any
from typing import Callable
from typing import Dict
from typing import Final
from typing import Type
from typing import Union

from mop.logger import unusual_backtracking
from mop.utils import lambda_value

# alias
REFEREE = Union[Callable[[Any], bool], object]
"""referee"""

CALLBACK = Callable[[Any], Any]
"""callback"""
ErrorHandlers = Dict[Type[BaseException], Callable[[BaseException, Any], Any]]
"""handle exception"""

INVALID_RETURN_VALUE: Final = object()
"""when raise Exception in function or method the value will return."""

BASE_TYPE: Final = (int, float, str, bytes, tuple, list, dict, set)
"""base type in python"""

FUNCTION_HASH: Final = (hash(type(lambda: ...)), hash(type(hash)))


def referee(ref: REFEREE) -> Callable[[Any], bool]:
    def _referee(return_value):
        if return_value is INVALID_RETURN_VALUE:
            return False
        elif ref is Any:
            return True
        elif ref in BASE_TYPE:
            return type(ref) == type(return_value)
        elif hash(type(ref)) in FUNCTION_HASH:
            return ref(return_value)
        else:
            return True

    return _referee


def monitor(ref: REFEREE, /, callback: CALLBACK = None, default_value=None):
    """
    core function: monitoring return value

    This is the core function of monitor-oriented programming.
    it can make a function get an expect value whatever happened.

    WARNING: if default_value is `Reference type`, for example, list, dict and other.
    the value could be changed in other code

    :param ref: Determines whether the return value is expected
    :param callback: Used to handle cases where the return value does not match the expected value
    :param default_value: default value, it is valid when callback is None
    :param debug: debug mode
    :return: function wrap
    """
    ref = referee(ref)
    callback = callback or lambda_value(default_value)

    def _monitoring_function_wrap(func):

        @functools.wraps(func)
        def _function(*args, **kwargs):
            _return_value = INVALID_RETURN_VALUE

            try:
                _return_value = func(*args, **kwargs)
            except BaseException as e:
                unusual_backtracking(e)

            if not ref(_return_value):
                return callback(_return_value)

            return _return_value

        return _function

    return _monitoring_function_wrap


class MonitoringReturnValue:
    def __eq__(self, other):
        return lambda v1, v2=other: v1 == v2

    def __ne__(self, other):
        return lambda v1, v2=other: v1 != v2

    @classmethod
    def isinstance(cls, other: Any):
        return lambda v1, v2=other: isinstance(v1, v2)

    @classmethod
    def issubclass(cls, other: Any):
        return lambda v1, v2=other: issubclass(v1, v2)
