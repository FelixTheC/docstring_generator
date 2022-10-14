import inspect
import json
from typing import Callable, Mapping, Optional

from strongtyping.strong_typing import match_typing
from strongtyping.strong_typing_utils import get_origins
from strongtyping_pyoverload import overload

from docstring_generator.config import CACHE_FOLDER

single_json_result = {
    "filename": "",
    "function_name": "",
    "annotations": "",
    "origin_docstring": "",  # the docstring before the first touch
    "current_docstring": "",
}


def arguments_to_dict(arguments: Mapping[str, inspect.Parameter]) -> dict:
    res = {}
    for key, argument in arguments.items():
        annotation_obj = get_origins(argument.annotation)[0]
        if not annotation_obj:
            annotation_str = argument.annotation.__name__
        else:
            annotation_str = annotation_obj

        res[key] = {
            "name": argument.name,
            "kind": argument.kind.value,
            "annotation": annotation_str,
            "default": argument.default.__name__,
        }
    return res


class FunctionCache:
    __slots__ = ("file_name", "object_name", "annotations", "origin_docstring", "current_docstring")

    file_name: str
    function_name: str
    annotations: dict
    origin_docstring: str
    current_docstring: Optional[str]

    @overload
    def __init__(self, json_obj: dict):
        self.file_name = json_obj["filename"]
        self.object_name = json_obj["object_name"]
        self.annotations = json_obj["annotations"]
        self.origin_docstring = json_obj["origin_docstring"]
        self.current_docstring = json_obj["current_docstring"]

    @overload
    def __init__(self, filename: str, object_name: str, annotations: dict, origin_docstring: str):
        self.file_name = filename.replace(".py", "")
        self.object_name = object_name
        self.annotations = arguments_to_dict(annotations)
        self.origin_docstring = origin_docstring
        self.current_docstring = None

    @overload
    def __init__(
        self,
        filename: str,
        object_name: str,
        annotations: dict,
        origin_docstring: str,
        current_docstring: str,
    ):
        self.file_name = filename.replace(".py", "")
        self.object_name = object_name
        self.annotations = arguments_to_dict(annotations)
        self.origin_docstring = origin_docstring
        self.current_docstring = current_docstring

    @staticmethod
    @match_typing
    def dict_to_annotations_str(annotations: dict) -> str:
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

    def generate_from_inital_docstring(self, generator_func: Callable, annotations: dict = None):
        func_str = (
            f"def func_a({self.dict_to_annotations_str(annotations or self.annotations)}):"
            "    pass"
            ""
        )
        new_func = {}
        exec(func_str, globals(), new_func)
        new_func["func_a"].__name__ = self.object_name
        new_func["func_a"].__doc__ = self.origin_docstring
        return generator_func()(new_func["func_a"]).__doc__.split("\n")

    def to_dict(self) -> dict:
        return {
            "filename": self.file_name,
            "object_name": self.object_name,
            "annotations": self.annotations,
            "origin_docstring": self.origin_docstring,  # the docstring before the first touch
            "current_docstring": self.current_docstring,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def write_json(self):
        filename = self.file_name.replace("/", "_")[1:].lower()
        cache_file = CACHE_FOLDER / f"{filename}_{self.object_name}.json"
        with cache_file.open("w") as file:
            json.dump(self.to_dict(), file)

    @classmethod
    def from_json(cls, /, json_: str) -> "FunctionCache":
        return FunctionCache(json.loads(json_))

    @classmethod
    def from_json_file(cls, file_name, object_name) -> Optional["FunctionCache"]:
        filename = file_name.replace("/", "_")[1:].lower().replace(".py", "")
        cache_file = CACHE_FOLDER / f"{filename}_{object_name}.json"

        if not cache_file.exists():
            return

        with cache_file.open("r") as file:
            return FunctionCache(json.load(file))

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()
