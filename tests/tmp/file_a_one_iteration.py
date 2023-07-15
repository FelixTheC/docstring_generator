#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 01.08.21
@author: felix
"""
from typing import Dict, Literal, Union


def foo(
    val_a: Literal["foo", "bar"],
    val_b: Dict[str, Union[int, float]],
    val_c: str = "Hello World",
) -> Dict[str, Union[int, float]]:
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam
    
    
    Parameters
    ----------
    val_a : argument of type `str` allowed values are `foo` or `bar`
    val_b : argument of type Dict(str, int or float)
    val_c : argument of type str
    	Default is Hello World
    
    Returns
    -------
    Dict(str, int or float)
    """


def bar(val_a: int, val_b: int) -> int:
    pass


class Vehicle:
    """
    The Vehicle object contains lots of vehicles
    
    
    Parameters
    ----------
    arg : argument of type str
    args : variadic arguments of type tuple
    kwargs : variadic keyword arguments of type dict
    """