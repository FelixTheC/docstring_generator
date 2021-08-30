#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 01.08.21
@author: felix
"""
import ast
import inspect
import json
from pathlib import Path
from pprint import pprint
from typing import Any
from typing import List

import click
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
    # TODO :fix: writing overwrites one line
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


def create_docstring_function(file: Path, data: Any, line_no: int, tab: TAB = TAB) -> DocstringLines:
    try:
        docs = inspect.getdoc(data).split("\n")
    except AttributeError:
        docs = []
    origin_doc_lines = len(docs) + 2 if docs else 0
    the_docs = numpy_docs_from_typing()(data).__doc__.split("\n")
    if the_docs[0] == "":
        the_docs = the_docs[1:]
    tmp_docs = [f"{tab}{data}" for data in ['"""'] + the_docs + ['"""\n']]
    the_docs = "\n".join(tmp_docs)
    return DocstringLines(file, the_docs, line_no, line_no + origin_doc_lines)


def create_docstring_classes(file: Path, data: Any, line_no: int) -> List[DocstringLines]:
    docs = inspect.getdoc(data).split("\n")
    origin_doc_lines = len(docs) + 2 if docs else 0

    class_docs = []
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


def json_exists(file: Path):
    return (CACHE_FOLDER / Path(f'{file.name}.json')).exists()


def save_as_json(file: Path, file_watcher):
    with (CACHE_FOLDER / Path(f'{file.name}.json')).open('w') as file:
        json.dump(file_watcher.to_json(), file)


def load_json(file: Path) -> dict:
    with (CACHE_FOLDER / Path(f'{file.name}.json')).open('r') as file:
        return json.loads(file.read())


def find_lineno(ast_body: list, func_name: str):
    start_lineno = end_lineno = 0
    for expr in ast_body:
        if isinstance(expr, ast.FunctionDef) and expr.name == func_name:
            start_lineno, end_lineno = expr.body[0].lineno, expr.end_lineno
            break
        if isinstance(expr, ast.ClassDef) and expr.name == func_name:
            start_lineno, end_lineno = expr.lineno, expr.end_lineno
            break
    return start_lineno, end_lineno


def find_imports(ast_body: list):
    return [ast.unparse(expr) for expr in ast_body
            if isinstance(expr, (ast.Import, ast.ImportFrom))]


def read_file(file: Path):
    import ast
    updated_lines = []
    file_data = {}
    imports = {}

    parsed_file = ast.parse(file.read_text(), str(file))

    exec('\n'.join(find_imports(parsed_file.body)), globals(), imports)
    exec(ast.unparse(parsed_file), {**globals(), **imports}, file_data)

    file_data = {key: val
                 for key, val in file_data.items()
                 if inspect.isfunction(val) or inspect.isclass(val)}

    for key, data in file_data.items():
        if inspect.isfunction(data):
            if str(file_data[data.__name__].__module__) == '__main__':
                line_no, _ = find_lineno(parsed_file.body, data.__name__)
                updated_lines.append(create_docstring_function(file, data, line_no))
        if inspect.isclass(data):
            pass
            # updated_lines.extend(create_docstring_classes(file, data))
    # updated_lines.sort(key=lambda x: x.start_line, reverse=True)
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
    if path == '.':
        for file in Path.cwd().glob("*/*.py"):
            if file.name != "gen_docs.py":
                read_file(file)
    path_ = Path(path)
    if not path_.exists():
        return
    if path_.name.endswith(".py"):
        read_file(path_)
    # for file in path_.glob("*/*.py"):
    #     if file.name != "gen_docs.py":
    #         read_file(file)


if __name__ == "__main__":
    main()
