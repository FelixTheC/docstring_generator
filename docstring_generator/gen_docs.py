import ast
import inspect
import pathlib
from pathlib import Path
from typing import Any, List, Optional

import click
from strongtyping.docs_from_typing import (
    class_docs_from_typing,
    numpy_docs_from_typing,
    rest_docs_from_typing,
)
from strongtyping.type_namedtuple import typed_namedtuple

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


def write_the_docs(file: Path, start_line: int, doc_string: str, end_line: int) -> None:
    with file.open("r") as f:
        lines = f.readlines()

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
        lines.insert(start_line - 1, doc_string + "\n" + new_end)

    with file.open("w+") as fp:
        fp.writelines(lines)


def get_tab_size(docs: list[str]) -> int:
    if len(docs) > 1:
        return len(docs[-1]) // 4
    return 1


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
    func_cache.write_json()

    try:
        docs = data.__doc__.split("\n")
    except AttributeError:
        docs = ""

    tab_size = get_tab_size(docs)
    docs = prepare_docs(docs)

    origin_doc_lines = len(docs) + 1 if docs else 0
    the_docs = config_styles.get(config.style, rest_docs_from_typing)()(data).__doc__.split("\n")
    origin, new = the_docs[:origin_doc_lines], the_docs[origin_doc_lines:]

    if 0 <= len(origin) < 3:  # means we have only a single line with no line break
        # we add a single line for a line break to follow PEP-8
        origin = [f'{tab * tab_size}"""'] + [f"{tab * tab_size}{data}" for data in origin if data]
    origin += [f"{tab * tab_size}{data}" for data in new]
    origin.append(f'{tab * tab_size}"""')

    return DocstringLines(
        file, "\n".join(origin), line_no, line_no + origin_doc_lines + len(origin)
    )


def create_docstring_classes(
    config: Config, file: Path, data: Any, line_no: int
) -> List[DocstringLines]:
    if data_docs := inspect.getdoc(data):
        docs = inspect.getdoc(data_docs).split("\n")
    else:
        docs = ""

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
    new_docs = DocstringLines(
        file, the_docs, line_no + 1, line_no + origin_doc_lines + len(the_docs)
    )
    class_docs.append(new_docs)
    for name, method in inspect.getmembers(data):
        if inspect.isfunction(method):
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
                        DocstringLines(
                            file,
                            "\n".join(method_docs),
                            method_line_no,
                            method_line_no + len(method_docs),
                        )
                    )
                else:
                    method_line_no += 1
                    method_docs = [
                        f"{METHOD_TAB}{doc_line}"
                        for doc_line in ['"""'] + method.__doc__.split("\n") + ['"""\n']
                    ]
                    class_docs.append(
                        DocstringLines(
                            file,
                            "\n".join(method_docs),
                            method_line_no,
                            method_line_no + len(method_docs),
                        )
                    )
    return class_docs


def read_file(file: Path, config: Config) -> None:
    if file.name == "gen_docs.py":
        return
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

    updated_lines = [obj for obj in updated_lines if obj]
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
