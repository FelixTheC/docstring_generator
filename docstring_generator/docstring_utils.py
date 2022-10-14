import inspect

from strongtyping.docs_from_typing import get_type_info
from strongtyping.strong_typing_utils import get_possible_types

DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
TAB = "    "


def numpy_class_docs(cls, remove_linebreak: bool = True) -> str:
    if cls.__doc__:
        indent_size = inspect.indentsize(cls.__doc__) // 4
        doc_infos = cls.__doc__.split("\n")
    else:
        indent_size = 1
        doc_infos = []

    if hasattr(cls, "__annotations__") and doc_infos:
        cls_name = cls.__name__
        doc_infos += [
            f"{TAB * indent_size}Attributes",
            f"{TAB * indent_size}----------",
        ]

        for key, val in cls.__annotations__.items():
            type_origins = get_possible_types(val)
            info_str = (
                f"{TAB * indent_size}{cls_name}.{key} : of type {get_type_info(val, type_origins)}"
            )
            if hasattr(cls, key):
                if default := getattr(cls, key):
                    info_str = f"{info_str}\n{TAB * (indent_size + 1)}Default is {default!r}"
            doc_infos.append(info_str)
    if doc_infos:
        doc_infos.append(f'\n{TAB * indent_size}"""')
    lb = "" if remove_linebreak else "\n"
    return lb + "\n".join(doc_infos)


def rest_class_docs(cls, remove_linebreak: bool = True) -> str:
    indent_size = inspect.indentsize(cls.__doc__) // 4 if cls.__doc__ else 1
    doc_infos = cls.__doc__.split("\n") if cls.__doc__ else []

    if hasattr(cls, "__annotations__") and doc_infos:
        cls_name = cls.__name__
        for key, val in cls.__annotations__.items():
            type_origins = get_possible_types(val)
            info_str = (
                f"{TAB * indent_size}:param {cls_name}.{key}: {get_type_info(val, type_origins)}"
            )
            if hasattr(cls, key):
                if default := getattr(cls, key):
                    info_str = f"{info_str} (Default value = {default!r})"
            doc_infos.append(info_str)
    if doc_infos:
        doc_infos.append(f'\n{TAB * indent_size}"""')
    lb = "" if remove_linebreak else "\n"
    return lb + "\n".join(doc_infos)


def class_docs_from_typing(cls: object, doc_type: str) -> str:
    if doc_type.lower() == "numpy":
        return numpy_class_docs(cls)
    else:
        return rest_class_docs(cls)
