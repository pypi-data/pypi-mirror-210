# -*- coding: utf-8 -*-
# Copyright (c) CDU

"""Model Docstrings

"""

from __future__ import absolute_import
from __future__ import annotations
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from typing import Callable
from typing import TypeVar

__all__ = ['lambda_function', 'lambda_value', 'raise_exception']

T = TypeVar("T")


def lambda_function(call: Callable, *args, **kwargs) -> Callable:
    """
    shortcut create a lambda function

    :param call: lambda ...: call(...)
    :param args: return function args
    :param kwargs: return function kwargs
    :return: lambda function
    """
    return lambda *_args, **_kwargs: call(*args, *_args, **kwargs, **_kwargs)


def lambda_value(value: T) -> Callable[[...], T]:
    return lambda *_, **__: value


def raise_exception(e: Exception):
    raise e
