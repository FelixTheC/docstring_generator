from typing import Callable


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
        more precise information about the required callable

    """
    pass


class Dummy:
    """
    Some useful information about this class

    Attributes
    ----------
    Dummy.attr_a : of type str
        Default is 'Hello'
    Dummy.attr_b : of type int

    """

    attr_a: str = "Hello"
    attr_b: int

    def __init__(self):
        pass

    def some_other_method(self, param_a: int):
        """
        Lorem ipsum dolor some_method

        Parameters
        ----------
        param_a : argument of type int

        """

        return self.attr_b

    @classmethod
    def some_classmethod(cls):
        """
        Lorem ipsum dolor some_classmethod
        """

        return cls.attr_b
