import typing
from typing import Any, Callable, Optional


def function_without_custom_docstring(param_a: str, param_b: dict):
    pass


def function_with_custom_docstring(param_a: int, param_b: Callable):
    """
    Lorem ipsum dolor samit even more text
    """
    pass


def function_with_return(param_a: int, param_b: Callable) -> Callable:
    """
    Lorem ipsum dolor samit even more text
    """
    pass


def function_with_optional(param_b: Callable, param_a: Optional[int] = None) -> Callable:
    """
    Lorem ipsum dolor samit even more text
    """
    pass


def function_with_default(param_b: Callable, param_a: int = 0) -> str:
    """
    Lorem ipsum dolor samit even more text
    """
    pass


def function_with_args(*args):
    """
    Lorem ipsum dolor samit even more text
    """
    pass


def function_with_kwargs(**kwargs):
    """
    Lorem ipsum dolor samit even more text
    """
    pass


def function_with_args_kwargs(param: Callable, *args, **kwargs) -> Any:
    """
    Lorem ipsum dolor samit even more text
    """
    pass
