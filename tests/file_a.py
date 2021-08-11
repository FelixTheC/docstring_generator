#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 01.08.21
@author: felix
"""
from typing import Dict
from typing import Literal
from typing import Union


def foo(
    val_a: Literal["foo", "bar"],
    val_b: Dict[str, Union[int, float]],
    val_c: str = "Hello World",
) -> Dict[str, Union[int, float]]:
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam
    """


def bar(val_a: int, val_b: int) -> int:
    pass


class Vehicle:
    """
    The Vehicle object contains lots of vehicles
    """

    def __init__(self, arg: str, *args, **kwargs):
        """
        $2 at least one value of type string is needed
        """
        self.arg = arg

    def cars(self, distance: float, destination: str):
        pass

    def fuel(self, fuel):
        """
        Some text
        """
        pass
