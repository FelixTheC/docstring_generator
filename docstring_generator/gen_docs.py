#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 01.08.21
@author: felix
"""
import ast
import inspect
from pathlib import Path
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
CACHE_FOLDER = Path(__file__).parent.parent / Path(".docstring_generator")

# file, line_no, the_docs, line_no + origin_doc_lines
DocstringLines = typed_namedtuple(
    "DocstringLines", ["file:PosixPath", "docs:str", "start_line:int", "end_line:int"]
)
Config = typed_namedtuple("Config", ["ignore_classes:bool", "ignore_function:bool", "style:str"])


def parse_ast_elements(ast_element, parsed_elements=[]):
    try:
        body = ast_element.body
    except (OSError, AttributeError):
        return
    else:
        parsed_elements.append(ast_element)
        for element in body:
            parse_ast_elements(element, parsed_elements)
        return parsed_elements


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
    return [
        ast.unparse(expr) for expr in ast_body if isinstance(expr, (ast.Import, ast.ImportFrom))
    ]


def write_the_docs(file: Path, start_line: int, doc_string: str, end_line: int) -> None:
    with file.open("r") as f:
        lines = f.readlines()
    with file.open("w+") as f:
        keep_line = None
        for idx, line in enumerate(lines):
            if idx == start_line:
                keep_line = lines[idx - 1]
                f.writelines(doc_string)
            if start_line - 1 <= idx < end_line:
                continue
            else:
                if keep_line:
                    if '"""' not in keep_line:
                        f.write(keep_line)
                    else:
                        f.write("\n")
                    keep_line = None
            f.write(line)


def create_docstring_function(
    config: Config, file: Path, data: Any, line_no: int, tab: TAB = TAB
) -> DocstringLines:
    try:
        docs = inspect.getdoc(data).split("\n")
    except AttributeError:
        docs = []
    origin_doc_lines = len(docs) + 2 if docs else 0
    if config.style == "numpy":
        the_docs = numpy_docs_from_typing()(data).__doc__.split("\n")
    else:
        the_docs = rest_docs_from_typing()(data).__doc__.split("\n")
    if the_docs[0] == "":
        the_docs = the_docs[1:]
    tmp_docs = [f"{tab}{data}" for data in ['"""'] + the_docs + ['"""\n']]
    the_docs = "\n".join(tmp_docs)
    return DocstringLines(file, the_docs, line_no, line_no + origin_doc_lines)


def create_docstring_classes(
    config: Config, file: Path, data: Any, line_no: int
) -> List[DocstringLines]:
    docs = inspect.getdoc(data).split("\n")
    origin_doc_lines = len(docs) + 2 if docs else 0

    class_docs = []
    tmp_docs = []
    reached_parameter = False

    the_docs = class_docs_from_typing(doc_type=config.style)(data).__doc__.split("\n")

    if the_docs[0] == "":
        the_docs = the_docs[1:]
    for doc_line in ['"""'] + the_docs + ['"""']:
        if doc_line == "Parameters":
            reached_parameter = True
        if not reached_parameter and doc_line.startswith(TAB):
            tmp_docs.append(doc_line)
        else:
            tmp_docs.append(f"{TAB}{doc_line}")
    the_docs = "\n".join(tmp_docs)
    new_docs = DocstringLines(file, the_docs, line_no + 1, line_no + origin_doc_lines)
    class_docs.append(new_docs)
    for name, method in inspect.getmembers(data):
        if inspect.isfunction(method) and name != "__init__":
            if method.__annotations__:
                try:
                    _, method_line_no = inspect.getsourcelines(method)
                except OSError:
                    parsed_file = ast.parse(file.read_text(), str(file), type_comments=True)
                    method_line_no = find_lineno(parse_ast_elements(parsed_file), name)[0]
                    method_docs = [
                        f"{METHOD_TAB}{doc_line}"
                        for doc_line in ['"""'] + method.__doc__.split("\n") + ['"""\n']
                    ]
                    class_docs.append(
                        DocstringLines(file, "\n".join(method_docs), method_line_no, method_line_no)
                    )
                else:
                    method_line_no += 1
                    method_docs = [
                        f"{METHOD_TAB}{doc_line}"
                        for doc_line in ['"""'] + method.__doc__.split("\n") + ['"""\n']
                    ]
                    class_docs.append(
                        DocstringLines(
                            file, "\n".join(method_docs), method_line_no, method_line_no + 1
                        )
                    )
    return class_docs


def read_file(file: Path, config: Config):
    import ast

    updated_lines = []
    file_data = {}
    imports = {}

    parsed_file = ast.parse(file.read_text(), str(file))

    exec("\n".join(find_imports(parsed_file.body)), globals(), imports)
    exec(ast.unparse(parsed_file), {**globals(), **imports}, file_data)

    file_data = {
        key: val
        for key, val in file_data.items()
        if inspect.isfunction(val) or inspect.isclass(val)
    }

    for key, data in file_data.items():
        if inspect.isfunction(data) and not config.ignore_function:
            line_no, _ = find_lineno(parsed_file.body, data.__name__)
            updated_lines.append(create_docstring_function(config, file, data, line_no))
        if inspect.isclass(data) and not config.ignore_classes:
            updated_lines.extend(
                create_docstring_classes(
                    config, file, data, find_lineno(parsed_file.body, data.__name__)[0]
                )
            )
    updated_lines.sort(key=lambda x: x.start_line, reverse=True)
    for new_docstring_lines in updated_lines:
        if new_docstring_lines:
            write_the_docs(
                new_docstring_lines.file,
                new_docstring_lines.start_line,
                new_docstring_lines.docs,
                new_docstring_lines.end_line,
            )


@click.command()
@click.argument("path")
@click.option("--style", default="numpy", help="Docstring style [numpy, rest].", show_default=True)
@click.option("--ignore-classes", is_flag=True)
@click.option("--ignore-functions", is_flag=True)
def main(path: str, ignore_classes: bool, ignore_functions: bool, style: str):
    config = Config(ignore_classes, ignore_functions, style)
    if path == ".":
        for file in Path.cwd().glob("*/*.py"):
            if file.name != "gen_docs.py":
                read_file(file, config)
    path_ = Path(path)
    if not path_.exists():
        return
    if path_.name.endswith(".py"):
        read_file(path_, config)
    for file in path_.glob("**/*.py"):
        if file.name not in ("gen_docs.py", "__init__.py", "__main__.py"):
            read_file(file, config)
