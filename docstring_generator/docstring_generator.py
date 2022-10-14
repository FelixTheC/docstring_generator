import ast
import inspect
from pathlib import Path

from docstring_generator.gen_docs import (
    Config,
    create_docstring_classes,
    create_docstring_function,
    find_imports,
    find_lineno,
    write_the_docs,
)


class DocstringGenerator:
    def __init__(self, file: Path, config: Config):
        self.file = file
        self.config = config
        self.file_functions = {}
        self.file_classes = {}
        self.updated_lines = []
        self.file_caches = []

    @property
    def get_parsed_file(self):
        return ast.parse(self.file.read_text(), str(self.file))

    def get_file_objects(self):
        file_data = {}
        imports = {}

        parsed_file = self.get_parsed_file

        exec("\n".join(find_imports(parsed_file.body)), globals(), imports)
        exec(ast.unparse(parsed_file), {**globals(), **imports}, file_data)

        file_objects = {
            key: val
            for key, val in file_data.items()
            if inspect.isfunction(val) or inspect.isclass(val)
        }

        self.file_functions = {
            key: val for key, val in file_objects.items() if inspect.isfunction(val)
        }
        self.file_classes = {key: val for key, val in file_objects.items() if inspect.isclass(val)}

    def create_docstrings_functions(self):
        for key, val in self.file_functions.items():
            line_no, _ = find_lineno(self.get_parsed_file.body, val.__name__)
            if updated_line := create_docstring_function(self.config, self.file, val, line_no):
                self.updated_lines.append(updated_line)

    def create_docstrings_classes(self):
        for key, val in self.file_classes.items():
            line_no, _ = find_lineno(self.get_parsed_file.body, val.__name__)
            self.updated_lines.extend(
                create_docstring_classes(self.config, self.file, val, line_no)
            )

    def sort_updated_lines(self):
        self.updated_lines.sort(key=lambda x: x.start_line, reverse=True)

    def write_docstring(self):
        self.sort_updated_lines()
        with self.file.open("r") as f:
            updated_lines = f.readlines()

        for new_docstring_lines in self.updated_lines:
            if new_docstring_lines:
                updated_lines = write_the_docs(
                    updated_lines,
                    new_docstring_lines.start_line,
                    new_docstring_lines.docs,
                    new_docstring_lines.end_line,
                )

        with self.file.open("w+") as fp:
            fp.writelines(updated_lines)
