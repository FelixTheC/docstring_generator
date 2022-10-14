#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect
from inspect import _empty

import pytest
from strongtyping.docs_from_typing import numpy_docs_from_typing

from docstring_generator.function_cache import FunctionCache


def example_function(param_a: str):
    """Some example docstring"""
    pass


@pytest.fixture(scope="module")
def example_function_signature():
    sig = inspect.signature(example_function)
    yield dict(sig.parameters)


def test_cache_object_to_dict(example_function_signature):
    cache_obj = FunctionCache(
        "test_caching.py", "example_function", example_function_signature, example_function.__doc__
    )

    assert cache_obj.to_dict() == {
        "filename": "test_caching",
        "object_name": "example_function",
        "annotations": {
            "param_a": {
                "annotation": "str",
                "default": "_empty",
                "kind": 1,
                "name": "param_a",
            }
        },
        "origin_docstring": "Some example docstring",
        "current_docstring": None,
    }


def test_cache_object_to_json(example_function_signature):
    cache_obj = FunctionCache(
        "test_caching.py", "example_function", example_function_signature, example_function.__doc__
    )

    assert cache_obj.to_json()


def test_restore_from_json_obj(example_function_signature):
    cache_obj = FunctionCache(
        "test_caching.py", "example_function", example_function_signature, example_function.__doc__
    )

    assert FunctionCache.from_json(cache_obj.to_json()) == cache_obj


def test_create_docstring_from_origin(example_function_signature):
    cache_obj = FunctionCache(
        "test_caching.py", "example_function", example_function_signature, example_function.__doc__
    )
    docstring = cache_obj.generate_from_inital_docstring(numpy_docs_from_typing)
    assert docstring == [
        "Some example docstring",
        "",
        "Parameters",
        "----------",
        "param_a : argument of type str",
    ]


def test_create_docstring_from_origin_alternative_arguments(example_function_signature):
    cache_obj = FunctionCache(
        "test_caching.py", "example_function", example_function_signature, example_function.__doc__
    )
    docstring = cache_obj.generate_from_inital_docstring(
        numpy_docs_from_typing,
        {
            "param_a": {
                "name": "param_a",
                "kind": 1,
                "annotation": "int",
                "default": _empty.__name__,
            }
        },
    )
    assert docstring == [
        "Some example docstring",
        "",
        "Parameters",
        "----------",
        "param_a : argument of type int",
    ]
