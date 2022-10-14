from typing import Callable


def function_without_custom_docstring(param_a: str, param_b: dict):
    pass


def function_with_custom_docstring(param_a: int, param_b: Callable):
    """
    Lorem ipsum dolor samit even more text
    """
    pass


class Dummy:
    """
    Some useful information about this class
    """

    attr_a: str = "Hello"
    attr_b: int

    def __init__(self):
        pass

    def some_other_method(self, param_a: int):
        """
        Lorem ipsum dolor some_method
        """

        return self.attr_b

    @classmethod
    def some_classmethod(cls):
        """
        Lorem ipsum dolor some_classmethod
        """

        return cls.attr_b
