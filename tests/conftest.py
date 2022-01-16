#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 16.01.22
@author: felix
"""
import ast
import uuid

from pytest import fixture
import pathlib

from docstring_generator.gen_docs import Config
from docstring_generator.gen_docs import find_imports
from docstring_generator.gen_docs import read_file

TEMP_DIR = pathlib.Path(__file__).parent / pathlib.Path('tmp')
FILE_NAME = str(uuid.uuid4()).replace('-', '')[:10] + '_example.py'
if not TEMP_DIR.exists():
    TEMP_DIR.mkdir(exist_ok=True)


@fixture
def testfile() -> pathlib.Path:
    tempfile = TEMP_DIR / pathlib.Path(FILE_NAME)
    tempfile.write_text(pathlib.Path("file_a.py").read_text())
    yield tempfile
    tempfile.unlink()


def extract_data_from_file(file: pathlib.Path):
    file_data = {}
    imports = {}

    parsed_file = ast.parse(file.read_text(), str(file))

    exec("\n".join(find_imports(parsed_file.body)), globals(), imports)
    exec(ast.unparse(parsed_file), {**globals(), **imports}, file_data)
    return file_data


def parse_file(file: pathlib.Path, ignore_classes: bool, ignore_functions: bool, style: str):
    config = Config(ignore_classes, ignore_functions, style)
    read_file(file, config)
