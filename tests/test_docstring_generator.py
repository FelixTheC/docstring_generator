from docstring_generator.config import BASE_ROOT, CACHE_FOLDER
from docstring_generator.docstring_generator import DocstringGenerator


def test_load_functions_only_file(function_only_file, config):
    gen = DocstringGenerator(function_only_file, config)
    gen.get_file_objects()

    assert len(gen.file_functions) == 2
    assert len(gen.file_classes) == 0


def test_load_class_only_file(class_only_file, config):
    gen = DocstringGenerator(class_only_file, config)
    gen.get_file_objects()

    assert len(gen.file_classes) == 1
    assert len(gen.file_functions) == 0


def test_changed_lines_functions_only_file(function_only_file, config):
    gen = DocstringGenerator(function_only_file, config)
    gen.get_file_objects()
    gen.create_docstrings_functions()

    assert gen.updated_lines[0].start_line == 7
    assert gen.updated_lines[0].end_line == 15
    assert gen.updated_lines[1].start_line == 11
    assert gen.updated_lines[1].end_line == 19


def test_changed_lines_class_only_file(class_only_file, config):
    gen = DocstringGenerator(class_only_file, config)
    gen.get_file_objects()
    gen.create_docstrings_classes()

    assert gen.updated_lines[0].start_line == 6

    assert gen.updated_lines[1].start_line == 10
    assert gen.updated_lines[1].end_line == 17


def test_cache_file_created_function_file_only(function_only_file, config):
    gen = DocstringGenerator(function_only_file, config)

    gen.get_file_objects()
    gen.create_docstrings_functions()
    prefix = str(BASE_ROOT).replace("/", "_")[1:].lower()

    expected_cache_files = [
        (
            CACHE_FOLDER
            / f"{prefix}_tests_files_functions_only_function_without_custom_docstring.json"
        ),
        (CACHE_FOLDER / f"{prefix}_tests_files_functions_only_function_with_custom_docstring.json"),
    ]
    for file in expected_cache_files:
        assert file.exists()


def test_write_updated_lines(function_only_file, config):
    with function_only_file.open("r") as fp:
        origin_txt = fp.readlines()

    gen = DocstringGenerator(function_only_file, config)

    gen.get_file_objects()
    gen.create_docstrings_functions()
    gen.write_docstring()

    with function_only_file.open("r") as fp:
        updated_txt = fp.readlines()

    assert len(origin_txt) < len(updated_txt)
    assert origin_txt != updated_txt


def test_cache_file_created_class_file_only(class_only_file, config):
    gen = DocstringGenerator(class_only_file, config)

    gen.get_file_objects()
    gen.create_docstrings_classes()
    prefix = str(BASE_ROOT).replace("/", "_")[1:].lower()

    expected_cache_files = [
        (CACHE_FOLDER / f"{prefix}_tests_files_class_only_Dummy.json"),
    ]
    for file in expected_cache_files:
        assert file.exists()


def test_mixed_file(mixed_file, config):
    gen = DocstringGenerator(mixed_file, config)

    gen.get_file_objects()
    gen.create_docstrings_functions()
    gen.create_docstrings_classes()
    gen.write_docstring()

    prefix = str(BASE_ROOT).replace("/", "_")[1:].lower()

    expected_cache_files = [
        (CACHE_FOLDER / f"{prefix}_tests_files_mixed_Dummy.json"),
    ]
    for file in expected_cache_files:
        assert file.exists()
