from typing import Any, Callable, Optional


def function_without_custom_docstring(param_a: str, param_b: dict):
    """
    Function function_without_custom_docstring


    Parameters
    ----------
    param_a : argument of type str
    param_b : argument of type dict

    """
    pass


def function_with_custom_docstring(param_a: int, param_b: Callable):
    """
    Lorem ipsum dolor samit even more text


    Parameters
    ----------
    param_a : argument of type int
    param_b : argument of type typing.Callable

    """
    pass


def function_with_return(param_a: int, param_b: Callable) -> Callable:
    """
    Lorem ipsum dolor samit even more text


    Parameters
    ----------
    param_a : argument of type int
    param_b : argument of type typing.Callable

    Returns
    -------
    typing.Callable

    """
    pass


def function_with_optional(param_b: Callable, param_a: Optional[int] = None) -> Callable:
    """
    Lorem ipsum dolor samit even more text


    Parameters
    ----------
    param_b : argument of type typing.Callable
    param_a : argument of type int or NoneType
        Default is None

    Returns
    -------
    typing.Callable

    """
    pass


def function_with_default(param_b: Callable, param_a: int = 0) -> str:
    """
    Lorem ipsum dolor samit even more text


    Parameters
    ----------
    param_b : argument of type typing.Callable
    param_a : argument of type int
        Default is 0

    Returns
    -------
    str

    """
    pass


def function_with_args(*args):
    """
    Lorem ipsum dolor samit even more text


    Parameters
    ----------
    args : variadic arguments of type tuple

    """
    pass


def function_with_kwargs(**kwargs):
    """
    Lorem ipsum dolor samit even more text


    Parameters
    ----------
    kwargs : variadic keyword arguments of type dict

    """
    pass


def function_with_args_kwargs(param: Callable, *args, **kwargs) -> Any:
    """
    Lorem ipsum dolor samit even more text


    Parameters
    ----------
    param : argument of type typing.Callable
    args : variadic arguments of type tuple
    kwargs : variadic keyword arguments of type dict

    Returns
    -------
    typing.Any

    """
    pass
