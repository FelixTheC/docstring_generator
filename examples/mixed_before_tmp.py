from datetime import datetime
from typing import Callable, Dict, Optional, Union


def function_name():
    pass


def function_name_args(arg1, arg2, arg3: Optional[bool]):
    """
    Parameters
    ----------
    arg1 : [Argument]
    arg2 : [Argument]
    arg3 : Optional[bool] [Argument]

    """
    if not dict:
        return ""
    res = {}
    for key, val in annotations.items():
        print(f"{val['default'] = }")
        if default_val := val["default"] != "_empty":
            res[key] = f"{val['annotation']} = {default_val}"
        else:
            res[key] = val["annotation"]
    return ", ".join([f"{key}: {val}" for key, val in res.items()])


def function_name_defaults(
    arg1,
    arg2: str = "hello",
    arg3: Callable = datetime.now,
) -> int:
    """
    Lorem ipsum dolor samit even more text
    
    Parameters
    ----------
    arg1 : [Argument]
    arg2 : str, optional, default: 'hello' [Argument]
        more precise information about the required callable
    arg3 : Callable, optional, default: datetime.now [Argument]

    Returns
    -------
    int
    """

    return 2 * 2


def function_name_star_args(*args):
    """
    Parameters
    ----------
    args : [Variadic arguments]

    """
    ...


def function_name_kwargs(**kwargs):
    """
    Parameters
    ----------
    kwargs : [Keyword arguments]

    """
    pass


def function_name_args_kwargs(*args: tuple, **kwargs: dict):
    """
    Parameters
    ----------
    args : tuple [Variadic arguments]
    kwargs : dict [Keyword arguments]

    """
    pass


def function_name_pos_only(pos1, /, pos2, pos3):
    """
    Parameters
    ----------
    pos1 : [Positional only argument]
    pos2 : [Argument]
    pos3 : [Argument]

    """
    pass


def function_name_kwargs_only(arg1, arg2: int | str = 2, *, kwarg1, kwarg2):
    """
    Parameters
    ----------
    arg1 : [Argument]
    arg2 : Union[int, str], optional, default: 2 [Argument]
    kwarg1 : [Keyword only argument]
    kwarg2 : [Keyword only argument]

    """
    pass


def function_name_pos_only_kwargs_only(pos1, pos2: int = 3, /, *, kwarg1, kwarg2="2"):
    """
    Parameters
    ----------
    pos1 : [Positional only argument]
    pos2 : int, optional, default: 3 [Positional only argument]
    kwarg1 : [Keyword only argument]
    kwarg2 :default: '2' [Keyword only argument]

    """
    pass


def function_without_custom_docstring(param_a: str, param_b: dict):
    """
    Parameters
    ----------
    param_a : str [Argument]
    param_b : dict [Argument]

    """
    pass


def function_with_custom_docstring(param_a: int, param_b: Callable) -> str:
    """
    Lorem ipsum dolor samit even more text
    
    Parameters
    ----------
    param_a : int [Argument]
    param_b : Callable [Argument]
        more precise information about the required callable

    Returns
    -------
    str
    """
    pass


def function_without_complex_type(param_a: list[str], param_b: Dict[Union[int, str], str | bool]):
    """
    Some useful information about this function
    
    Parameters
    ----------
    param_a : list[str] [Argument]
    param_b : Dict[Union[int, str], Union[str, bool]] [Argument]

    """
    pass


class Dummy:
    """
    Some useful information about this class
    """

    attr_a: str = "Hello"
    attr_b: int

    def __init__(self):
        """
        Parameters
        ----------
        self : [Argument]

        """
        pass

    def some_other_method(self, param_a: int):
        """
        Lorem ipsum dolor some_method
        
        Parameters
        ----------
        self : [Argument]
            more precise information about the required callable
        param_a : int [Argument]

        """

        return self.attr_b

    @classmethod
    def some_classmethod(cls):
        """
        Lorem ipsum dolor some_classmethod
        
        Parameters
        ----------
        cls : [Argument]

        """

        return cls.attr_b
