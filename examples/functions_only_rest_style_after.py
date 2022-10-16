from typing import Any, Callable, Optional


def function_without_custom_docstring(param_a: str, param_b: dict):
    """
    Function function_without_custom_docstring


    :param param_a: argument
    :param param_b: argument
    :type param_a: str
    :type param_b: dict

    """
    pass


def function_with_custom_docstring(param_a: int, param_b: Callable):
    """
    Lorem ipsum dolor samit even more text


    :param param_a: argument
    :param param_b: argument
    :type param_a: int
    :type param_b: typing.Callable

    """
    pass


def function_with_return(param_a: int, param_b: Callable) -> Callable:
    """
    Lorem ipsum dolor samit even more text


    :param param_a: argument
    :param param_b: argument
    :type param_a: int
    :type param_b: typing.Callable
    :returns: typing.Callable

    """
    pass


def function_with_optional(param_b: Callable, param_a: Optional[int] = None) -> Callable:
    """
    Lorem ipsum dolor samit even more text


    :param param_b: argument
    :param param_a: argument  (Default value = None)
    :type param_b: typing.Callable
    :type param_a: int or NoneType
    :returns: typing.Callable

    """
    pass


def function_with_default(param_b: Callable, param_a: int = 0) -> str:
    """
    Lorem ipsum dolor samit even more text


    :param param_b: argument
    :param param_a: argument  (Default value = 0)
    :type param_b: typing.Callable
    :type param_a: int
    :returns: str

    """
    pass


def function_with_args(*args):
    """
    Lorem ipsum dolor samit even more text


    :param args: variadic arguments
    :type args: tuple

    """
    pass


def function_with_kwargs(**kwargs):
    """
    Lorem ipsum dolor samit even more text


    :param kwargs: variadic keyword arguments
    :type kwargs: dict

    """
    pass


def function_with_args_kwargs(param: Callable, *args, **kwargs) -> Any:
    """
    Lorem ipsum dolor samit even more text


    :param param: argument
    :param args: variadic arguments
    :param kwargs: variadic keyword arguments
    :type param: typing.Callable
    :type args: tuple
    :type kwargs: dict
    :returns: typing.Any

    """
    pass
