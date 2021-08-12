#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 01.08.21
@author: felix
"""
import pickle
from typing import Any
from typing import List

import click
from pathlib import Path
import inspect
from strongtyping.docs_from_typing import (
    rest_docs_from_typing,
    numpy_docs_from_typing,
    class_docs_from_typing,
)
from strongtyping.type_namedtuple import typed_namedtuple

TAB = " " * 4
METHOD_TAB = TAB * 2
CACHE_FOLDER = Path(__file__).parent.parent / Path('.docstring_generator')

# file, line_no, the_docs, line_no + origin_doc_lines
DocstringLines = typed_namedtuple(
    "DocstringLines", ["file:PosixPath", "docs:str", "start_line:int", "end_line:int"]
)


def write_the_docs(file: Path, start_line: int, doc_string: str, end_line: int) -> None:
    with file.open("r") as f:
        lines = f.readlines()
    with file.open("w+") as f:
        for idx, line in enumerate(lines):
            if idx == start_line:
                f.writelines(doc_string)
                f.write("\n")
            if start_line - 1 <= idx < end_line:
                continue
            f.write(line)


def create_docstring_function(file: Path, data: Any, tab: TAB = TAB) -> DocstringLines:
    func, line_no = inspect.getsourcelines(data)
    for idx, line in enumerate(func):
        if line.endswith(":\n"):
            line_no += idx + 1
            break
    try:
        docs = inspect.getdoc(data).split("\n")
    except AttributeError:
        docs = []
    origin_doc_lines = len(docs) + 2
    the_docs = numpy_docs_from_typing()(data).__doc__.split("\n")
    if the_docs[0] == "":
        the_docs = the_docs[1:]
    tmp_docs = [f"{tab}{data}" for data in ['"""'] + the_docs + ['"""\n']]
    the_docs = "\n".join(tmp_docs)
    return DocstringLines(file, the_docs, line_no, line_no + origin_doc_lines)


def create_docstring_classes(file: Path, data: Any) -> List[DocstringLines]:
    func, line_no = inspect.getsourcelines(data)
    docs = inspect.getdoc(data).split("\n")
    origin_doc_lines = len(docs) + 2

    class_docs = []
    for idx, line in enumerate(func):
        if line.endswith(":\n"):
            line_no += idx + 1
            break
    the_docs = class_docs_from_typing(doc_type="numpy")(data).__doc__.split("\n")
    if the_docs[0] == "":
        the_docs = the_docs[1:]
    tmp_docs = []
    reached_parameter = False
    for doc_line in ['"""'] + the_docs + ['"""\n']:
        if doc_line == "Parameters":
            reached_parameter = True
        if not reached_parameter and doc_line.startswith(TAB):
            tmp_docs.append(doc_line)
        else:
            tmp_docs.append(f"{TAB}{doc_line}")
    the_docs = "\n".join(tmp_docs)
    class_docs.append(DocstringLines(file, the_docs, line_no, line_no + origin_doc_lines))

    for method in dir(data):
        method_func = getattr(data, method)
        if inspect.isfunction(method_func) and method != "__init__":
            if method_func.__annotations__:
                _, method_line_no = inspect.getsourcelines(method_func)
                method_line_no += 1
                method_docs = [
                    f"{METHOD_TAB}{doc_line}"
                    for doc_line in ['"""'] + method_func.__doc__.split("\n") + ['"""\n']
                ]
                class_docs.append(
                    DocstringLines(file, "\n".join(method_docs), method_line_no, method_line_no + 1)
                )
    return class_docs


def read_file(file: Path):
    from src.docstring_utils import FileWatched
    cached_file = CACHE_FOLDER / Path(f'{file.name}.pkl')
    if cached_file.exists():
        with cached_file.open('rb') as pickle_file:
            file_watched = pickle.load(pickle_file)
    else:
        file_watched = FileWatched(file)
    file_watched.create_docstrings()

    with cached_file.open('wb') as pickle_file:
        pickle.dump(file_watched, pickle_file)

    updated_lines = [DocstringLines(**line)
                     for line in file_watched.updated_lines if line]
    for key, data in file_watched():
        # if inspect.isfunction(data):
        #     result = create_docstring_function(file, data)
        #     updated_lines.append(result)
        if inspect.isclass(data):
            updated_lines.extend(create_docstring_classes(file, data))
    updated_lines.sort(key=lambda x: x.start_line, reverse=True)
    # for new_docstring_lines in updated_lines:
    #     if new_docstring_lines:
    #         write_the_docs(
    #             new_docstring_lines.file,
    #             new_docstring_lines.start_line,
    #             new_docstring_lines.docs,
    #             new_docstring_lines.end_line,
    #         )


def create_cache_folder():
    if not CACHE_FOLDER.exists():
        CACHE_FOLDER.mkdir()


@click.command()
@click.argument("path")
def main(path: str):
    create_cache_folder()
    path_ = Path(path)
    if path_.name.endswith(".py"):
        read_file(path_)
    for file in path_.glob("*.py"):
        if file.name != "gen_docs.py":
            print(file)


if __name__ == "__main__":
    main()
