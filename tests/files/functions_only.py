#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Callable


def function_without_custom_docstring(param_a: str, param_b: dict):
    pass


def function_with_custom_docstring(param_a: int, param_b: Callable):
    """
    Lorem ipsum dolor samit even more text
    """
    pass
