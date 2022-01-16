#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect
from datetime import datetime
from pathlib import Path
from typing import Callable


DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


def tmp(file: Path, import_str='*') -> dict:
    file_objects = {}
    import_name = str(file).replace("/", ".").removesuffix(".py")
    exec(f"from {import_name} import {import_str}", globals(), file_objects)
    return file_objects


class DocstringHistory:

    def __init__(self, origin_docstring: str, func_params: dict):
        self.func_params = {key: str(val) for key, val in func_params.items()}
        self.origin_docstring = origin_docstring
        self.docstring_over_time = {datetime.utcnow(): self.origin_docstring}
        self.params_over_time = {datetime.utcnow(): self.func_params}

    def __add__(self, other: tuple):
        if other[0] == 'doc':
            self.docstring_over_time[datetime.utcnow()] = other[1]
        elif other[0] == 'params':
            self.params_over_time[datetime.utcnow()] = {key: str(val)
                                                        for key, val in other[1].items()}

    def add(self, other: tuple):
        self + other

    @property
    def last(self) -> str:
        return self.docstring_over_time[sorted(self.docstring_over_time.keys(), reverse=True)[0]]

    @property
    def length(self) -> int:
        return len(self.docstring_over_time)

    @property
    def function_params(self) -> dict:
        """
        Get last known function params
        """
        return self.params_over_time[sorted(self.params_over_time.keys(), reverse=True)[0]]

    def to_json(self):
        return {
            "origin_docstring": self.origin_docstring,
            "docstring_over_time": {str(key): val for key, val in self.docstring_over_time.items()},
            "params_over_time": {str(key): val for key, val in self.params_over_time.items()},
            "func_params": self.func_params,
        }

    @classmethod
    def load_json(cls, json_data: dict) -> "DocstringHistory":
        new_cls = cls(json_data["origin_docstring"], json_data["func_params"])
        new_cls.docstring_over_time = {datetime.strptime(key, DATE_FORMAT): val
                                       for key, val in json_data["docstring_over_time"]}


class DocstringCreator:

    def __init__(self, file: Path, function: Callable, is_def: bool = True):
        self.file = file
        self.callable_ = function
        self.is_def = is_def
        self.history = None
        self.__docstring_lines = None

        self.extract_origin_docstring()
        self.generate_docstring()

    def extract_origin_docstring(self):
        self.history = DocstringHistory(self.callable_.__doc__,
                                        inspect.signature(self.callable_).parameters)

    def set_docstring_lines(self, doc_lines):
        self.__docstring_lines = {
            'file': doc_lines.file,
            'docs': doc_lines.docs,
            'start_line': doc_lines.start_line,
            'end_line': doc_lines.end_line,
        }

    @property
    def docstring_lines(self):
        return self.__docstring_lines

    def generate_docstring(self):
        from docstring_generator import create_docstring_function, DocstringLines

        function_params = inspect.signature(self.callable_).parameters
        if self.is_def:
            result: DocstringLines = create_docstring_function(self.file, self.callable_)
            if self.history.length == 1:
                self.history.add(('doc', result.docs))
                self.set_docstring_lines(result)
            elif self.history.length == 1 and self.history.last != result.docs:
                self.history.add(('doc', result.docs))
                self.set_docstring_lines(result)
            elif self.history.length > 2:
                if (self.history.last != result.docs
                        and len(self.history.function_params) != len(function_params)):
                    self.history.add(('doc', result.docs))
                    self.set_docstring_lines(result)
                else:
                    self.history.add(('doc', None))
                    self.__docstring_lines = None

    def to_json(self):
        return {str(self.callable_): self.history.to_json()}

    @classmethod
    def load_json(cls, file: Path, json_data: dict) -> "DocstringCreator":
        key = list(json_data.keys())[0]
        import_name = key.split(' ')[1]
        new_cls = cls(file, tmp(file, import_name)[import_name])
        new_cls.history = DocstringHistory.load_json(json_data[key])
        return new_cls


class FileWatched:

    def __init__(self, file: Path):
        self.file = file
        self.file_objects = {}
        self.updated_lines = []
        self.func_doc = {}
        self.read_in_callable_objects()

    def read_in_callable_objects(self):
        import_name = str(self.file).replace("/", ".").removesuffix(".py")
        if import_name.startswith('.'):
            import_name = import_name[1:]
        exec(f"from {import_name} import *", globals(), self.file_objects)

    def create_docstrings(self):
        for key, data in self.file_objects.items():
            if inspect.isfunction(data):
                try:
                    creator = self.func_doc[str(data)]
                except KeyError:
                    self.func_doc[str(data)] = DocstringCreator(self.file, data)
                    creator = self.func_doc[str(data)]
                creator.generate_docstring()
                self.updated_lines.append(creator.docstring_lines)

    def __call__(self, *args, **kwargs):
        return self.file_objects.items()

    def to_json(self):
        return {self.file.name: [val.to_json() for val in self.func_doc.values()]}

    def load_json(self, json_data: dict):
        if self.file.name not in json_data:
            return
        for dc in json_data[self.file.name]:
            for key, val in dc.items():
                self.func_doc[key] = DocstringCreator.load_json(self.file, dc)
