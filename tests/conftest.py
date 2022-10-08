import ast
import pathlib
import uuid

from pytest import fixture
from strongtyping.type_namedtuple import typed_namedtuple

from docstring_generator.gen_docs import Config, find_imports, read_file

TEMP_DIR = pathlib.Path(__file__).parent / pathlib.Path("tmp")
FILE_NAME = str(uuid.uuid4()).replace("-", "")[:10] + "_example.py"
if not TEMP_DIR.exists():
    TEMP_DIR.mkdir(exist_ok=True)


Config = typed_namedtuple("Config", ["ignore_classes:bool", "ignore_function:bool", "style:str"])


@fixture(scope="package")
def function_only_file():
    file = pathlib.Path(__file__).parent / pathlib.Path("files") / pathlib.Path("functions_only.py")
    with file.open("r") as fp:
        origin_txt = fp.readlines()

    yield file

    with file.open("w") as fp:
        fp.writelines(origin_txt)


@fixture(scope="package")
def class_only_file():
    yield pathlib.Path(__file__).parent / pathlib.Path("files") / pathlib.Path("class_only.py")


@fixture(scope="package")
def config():
    yield Config(True, False, "numpy")


@fixture
def testfile() -> pathlib.Path:
    tempfile = TEMP_DIR / pathlib.Path(FILE_NAME)
    tempfile.write_text(pathlib.Path("tmp/file_a.py").read_text())
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
