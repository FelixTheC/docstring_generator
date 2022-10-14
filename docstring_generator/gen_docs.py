import ast
import inspect
import pathlib
from pathlib import Path
from types import FunctionType
from typing import Any, List, Optional

import click
from strongtyping.docs_from_typing import numpy_docs_from_typing, rest_docs_from_typing
from strongtyping.type_namedtuple import typed_namedtuple

from docstring_generator.docstring_utils import class_docs_from_typing
from docstring_generator.function_cache import FunctionCache

TAB = " " * 4
METHOD_TAB = TAB * 2
CACHE_FOLDER = Path(__file__).parent.parent / Path(".docstring_generator")

# file, line_no, the_docs, line_no + origin_doc_lines
DocstringLines = typed_namedtuple(
    "DocstringLines", ["file:PosixPath", "docs:str", "start_line:int", "end_line:int"]
)
Config = typed_namedtuple("Config", ["ignore_classes:bool", "ignore_function:bool", "style:str"])

config_styles = {"numpy": numpy_docs_from_typing, "rest": rest_docs_from_typing}


def parse_ast_elements(ast_element, parsed_elements=[]) -> Optional[list]:
    try:
        body = ast_element.body
    except (OSError, AttributeError):
        return
    else:
        parsed_elements.append(ast_element)
        for element in body:
            parse_ast_elements(element, parsed_elements)
        return parsed_elements


def find_lineno(ast_body: list, func_name: str) -> tuple[int, int]:
    start_lineno = end_lineno = 0
    for expr in ast_body:
        if isinstance(expr, ast.FunctionDef) and expr.name == func_name:
            start_lineno, end_lineno = expr.body[0].lineno, expr.end_lineno
            break
        if isinstance(expr, ast.ClassDef) and expr.name == func_name:
            start_lineno, end_lineno = expr.lineno, expr.end_lineno
            break
    return start_lineno, end_lineno


def find_imports(ast_body: list) -> list:
    return [
        ast.unparse(expr) for expr in ast_body if isinstance(expr, (ast.Import, ast.ImportFrom))
    ]


def write_the_docs(
    lines: list[str], start_line: int, doc_string: str, end_line: int
) -> Optional[list[str]]:
    if start_line == end_line:
        return

    # del lines[start_line - 1]
    del_end_line = None
    if '"""' in lines[start_line - 1]:
        for idx, obj in enumerate(lines[start_line:]):
            if '"""' in obj:
                del_end_line = start_line + idx
                break

    if del_end_line:
        before, after = lines[:start_line], lines[del_end_line + 1 :]
        before.append(doc_string)
        before.append("\n")
        lines = before + after
    else:
        new_end = lines.pop(start_line - 1)
        tabsize = inspect.indentsize(doc_string) // 4
        lines.insert(start_line - 1, f'{"    " * tabsize}"""' + "\n" + doc_string + "\n" + new_end)
    return lines


def get_line_number_from_ast(file: Path, name: str):
    parsed_file = ast.parse(file.read_text(), str(file), type_comments=True)
    method_line_no = find_lineno(parse_ast_elements(parsed_file), name)[0]
    return method_line_no


def get_line_number(method: FunctionType, file: Path, name: str):
    try:
        return inspect.getsourcelines(method)[-1]
    except OSError:
        return get_line_number_from_ast(file, name)


def get_tabs(method: FunctionType, file: Path, name: str):
    try:
        spaces = (
            inspect.indentsize(inspect.getsourcelines(method)[0][0]) + 4
        )  # [0][0] will return `def ...(..):` so that we add 4 for the next line
    except OSError:
        line_number = get_line_number(method, file, name)
        last_line = ""
        with file.open("r") as fp:
            for line in range(line_number - 1):
                last_line = fp.readline()
        spaces = inspect.indentsize(last_line) + 4

    return "    " * (spaces // 4)


def prepare_docs(docs: list[str]) -> list[str]:
    return [doc_str or "\n" for doc_str in docs]


def create_docstring_function(
    config: Config, file: Path, data: Any, line_no: int, tab: TAB = TAB
) -> DocstringLines:

    func_cache = FunctionCache.from_json_file(str(file.absolute()), data.__name__) or FunctionCache(
        str(file.absolute()),
        data.__name__,
        dict(inspect.signature(data).parameters),
        data.__doc__ or "",
    )

    try:
        docs = data.__doc__.split("\n")
    except AttributeError:
        docs = ""

    if not func_cache.current_docstring or func_cache.origin_docstring == data.__doc__:

        tabs = get_tabs(data, file, data.__name__)
        docs = prepare_docs(docs)

        origin_doc_lines = len(docs) + 1 if docs else 0
        the_docs = (
            config_styles.get(config.style, rest_docs_from_typing)()(data)
            .__doc__.strip()
            .split("\n")
        )
        origin = the_docs
        origin += ["", '"""']

        new_docs = "\n".join([f"{tabs}{obj}" for obj in origin])
        func_cache.current_docstring = new_docs
        func_cache.write_json()

        return DocstringLines(file, new_docs, line_no, line_no + origin_doc_lines + len(origin))


def create_docstring_method(cls, file: Path, config: Config) -> Optional[DocstringLines]:
    for name, method in inspect.getmembers(cls):
        if not hasattr(method, "__annotations__"):
            continue

        if not method.__annotations__:
            continue

        if inspect.isfunction(method) and name not in ("__init__",) or inspect.ismethod(method):
            func_cache = FunctionCache.from_json_file(str(file.absolute()), name) or FunctionCache(
                str(file.absolute()),
                name,
                dict(inspect.signature(method).parameters),
                method.__doc__ or "",
            )

            start_line = get_line_number(method, file, name)
            tabs = get_tabs(method, file, name)
            doc_lines = config_styles.get(config.style, rest_docs_from_typing)(
                remove_linebreak=True
            )(method).__doc__.split("\n")[1:] + ["", '"""']
            new_docs = "\n".join([f"{tabs}{obj}" for obj in doc_lines])

            if not func_cache.current_docstring or func_cache.origin_docstring == method.__doc__:
                func_cache.current_docstring = new_docs
                func_cache.write_json()
                yield DocstringLines(file, new_docs, start_line, start_line + len(doc_lines))


def create_docstring_classes(
    config: Config, file: Path, data: Any, line_no: int
) -> List[DocstringLines]:
    class_docs = []

    func_cache = FunctionCache.from_json_file(str(file.absolute()), data.__name__) or FunctionCache(
        str(file.absolute()),
        data.__name__,
        dict(inspect.signature(data).parameters),
        data.__doc__ or "",
    )

    the_docs = class_docs_from_typing(data, doc_type=config.style)[1:]

    if not func_cache.current_docstring or func_cache.origin_docstring == data.__doc__:
        func_cache.current_docstring = the_docs

        func_cache.write_json()
        if data.__doc__ != the_docs:
            class_docs.append(
                DocstringLines(file, the_docs, line_no + 1, line_no + len(the_docs.split("\n")))
            )

    for doc_lines in create_docstring_method(data, file, config):
        if doc_lines:
            class_docs.append(doc_lines)

    return class_docs


def read_file(file: Path, config: Config) -> None:
    if file.name == "gen_docs.py":
        return
    from docstring_generator.docstring_generator import DocstringGenerator

    gen = DocstringGenerator(file, config)

    gen.get_file_objects()
    if not config.ignore_function:
        gen.create_docstrings_functions()
    if not config.ignore_classes:
        gen.create_docstrings_classes()
    gen.write_docstring()


@click.command()
@click.argument("path")
@click.option("--style", default="numpy", help="Docstring style [numpy, rest].", show_default=True)
@click.option("--ignore-classes", is_flag=True)
@click.option("--ignore-functions", is_flag=True)
def main(path: str, ignore_classes: bool, ignore_functions: bool, style: str) -> None:
    config = Config(ignore_classes, ignore_functions, style)
    path_ = pathlib.Path(path)
    if not path_.exists():
        return

    if path_.is_dir():
        for file in path_.glob("**/*.py"):
            read_file(file, config)

    if path_.is_file() and path_.name.endswith(".py"):
        read_file(path_, config)


if __name__ == "__main__":
    main()
