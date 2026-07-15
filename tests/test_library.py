import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

BASE_EXAMPLE_FILE = Path(__file__).parent / "files" / "example.py"

EXPECTED_FILES = {
    "numpy": Path(__file__).parent / "files" / "expected" / "numpy_example.py",
    "google": Path(__file__).parent / "files" / "expected" / "google_example.py",
    "rest": Path(__file__).parent / "files" / "expected" / "reST_example.py",
}


@pytest.mark.parametrize("style", ("numpy", "rest", "google"))
def test_docstring_creation(style):
    with NamedTemporaryFile(suffix=".py", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(BASE_EXAMPLE_FILE.read_bytes())

    try:
        gendocs_new = Path(sys.executable).parent / "gendocs_new"
        result = subprocess.run(
            [str(gendocs_new), "--style", style, str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"gendocs_new failed:\n{result.stderr}"

        expected = EXPECTED_FILES[style].read_text(encoding="utf-8")
        actual = tmp_path.read_text(encoding="utf-8")

        assert actual == expected, (
            f"Style '{style}': generated output does not match expected.\n"
            f"--- expected ---\n{expected}\n--- actual ---\n{actual}"
        )
    finally:
        tmp_path.unlink(missing_ok=True)


def test_check_coverage_no_coverage():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"
    result = subprocess.run(
        [str(gendocs_new), "--check", str(BASE_EXAMPLE_FILE)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1

    with Path(Path.cwd(), "gendocs_check_output.json").open('r') as output_file:
        import json
        check_result = json.load(output_file)

    assert not check_result["passing"]


@pytest.mark.parametrize("test_file", EXPECTED_FILES.values())
def test_check_coverage_full_coverage(test_file):
    gendocs_new = Path(sys.executable).parent / "gendocs_new"
    result = subprocess.run(
        [str(gendocs_new), "--check", "--threshold", "95", str(test_file)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    with Path(Path.cwd(), "gendocs_check_output.json").open('r') as output_file:
        import json
        check_result = json.load(output_file)

    assert (check_result["passing"])


@pytest.mark.parametrize("test_file", EXPECTED_FILES.values())
@pytest.mark.xfail
def test_check_coverage_full_coverage_with_strict(test_file):
    gendocs_new = Path(sys.executable).parent / "gendocs_new"
    result = subprocess.run(
        [str(gendocs_new), "--check", "--threshold", "95", "--strict", str(test_file)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    with Path(Path.cwd(), "gendocs_check_output.json").open('r') as output_file:
        import json
        check_result = json.load(output_file)

    assert check_result["passing"]

def test_overwrite_existing_style():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"

    file = EXPECTED_FILES['google']

    with NamedTemporaryFile(suffix=".py", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(file.read_bytes())

    # default style is numpy as it is the most common
    result = subprocess.run(
        [str(gendocs_new), "--overwrite-style", str(tmp_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    expected = EXPECTED_FILES["numpy"].read_text(encoding="utf-8")
    actual = tmp_path.read_text(encoding="utf-8")

    assert expected == actual
