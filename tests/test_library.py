import os
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

BASE_EXAMPLE_FILE = Path(__file__).parent / "files" / "example.py"

EXPECTED_FILES = {
    "numpy": Path(__file__).parent / "files" / "expected" / "numpy_example.py",
    "google": Path(__file__).parent / "files" / "expected" / "google_example.py",
    "rest": Path(__file__).parent / "files" / "expected" / "reST_example.py",
}


@pytest.mark.parametrize("style", ("numpy", "google"))
def test_docstring_creation(style):
    """
    Parameters
    ----------
    style : [Argument]
    """
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
    """
    Parameters
    ----------
    test_file : [Argument]
    """
    gendocs_new = Path(sys.executable).parent / "gendocs_new"
    result = subprocess.run(
        [str(gendocs_new), "--check", "--threshold", "94", str(test_file)],
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
    """
    Parameters
    ----------
    test_file : [Argument]
    """
    gendocs_new = Path(sys.executable).parent / "gendocs_new"
    result = subprocess.run(
        [str(gendocs_new), "--check", "--threshold", "94", "--strict", str(test_file)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    with Path(Path.cwd(), "gendocs_check_output.json").open('r') as output_file:
        import json
        check_result = json.load(output_file)

    assert check_result["passing"]


@pytest.mark.parametrize("test_file", EXPECTED_FILES.values())
def test_check_coverage_full_coverage_with_ignore_magic(test_file):
    """
    Parameters
    ----------
    test_file : [Argument]
    """
    from docstring_generator.new_gen_docs import main
    main(["--check", "--ignore-magic", "--threshold", "94", str(test_file)], standalone_mode=False)

    with Path(Path.cwd(), "gendocs_check_output.json").open('r') as output_file:
        import json
        check_result = json.load(output_file)

    assert check_result["passing"]


# ---------------------------------------------------------------------------
# --dry-run tests
# ---------------------------------------------------------------------------

def test_dry_run_shows_diff_and_does_not_modify_file():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"

    with NamedTemporaryFile(suffix=".py", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(BASE_EXAMPLE_FILE.read_bytes())

    try:
        original_content = tmp_path.read_text(encoding="utf-8")

        result = subprocess.run(
            [str(gendocs_new), "--dry-run", str(tmp_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"gendocs_new --dry-run failed:\n{result.stderr}"

        # File must be untouched
        assert tmp_path.read_text(encoding="utf-8") == original_content, (
            "--dry-run must not modify the original file"
        )

        # stdout must contain a unified diff (example.py has no docstrings yet)
        assert "+++" in result.stdout or "---" in result.stdout, (
            "--dry-run should output a unified diff when there are changes"
        )
    finally:
        tmp_path.unlink(missing_ok=True)


@pytest.mark.xfail(reason="Something is weired with the dry-run")
def test_dry_run_reports_no_changes_for_fully_documented_file():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"
    # Use a hand-crafted, minimal fixture that is genuinely idempotent (no raises → no edge cases)
    idempotent_file = Path(__file__).parent / "files" / "idempotent_example.py"

    result = subprocess.run(
        [str(gendocs_new), "--dry-run", str(idempotent_file)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"gendocs_new --dry-run failed:\n{result.stderr}"
    assert "no changes" in result.stdout, (
        "--dry-run should print '<file>: no changes' when the file is already fully documented"
    )


# ---------------------------------------------------------------------------
# --changed-only tests
# ---------------------------------------------------------------------------

def test_changed_only_aborts_when_git_not_found():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"

    with NamedTemporaryFile(suffix=".py", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(BASE_EXAMPLE_FILE.read_bytes())

    try:
        # Build an env where git is absent from PATH
        env = os.environ.copy()
        env["PATH"] = str(Path(sys.executable).parent)  # only the venv bin dir

        result = subprocess.run(
            [str(gendocs_new), "--changed-only", str(tmp_path)],
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode != 0, (
            "--changed-only should abort with non-zero exit when git is not available"
        )
        assert "git" in result.stderr.lower(), (
            "error message should mention 'git'"
        )
    finally:
        tmp_path.unlink(missing_ok=True)


def test_changed_only_processes_only_changed_files():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"

    with TemporaryDirectory() as tmp_dir:
        tmp_dir_path = Path(tmp_dir)

        # Initialise a throwaway git repo
        subprocess.run(["git", "init"], cwd=tmp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_dir, check=True, capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_dir, check=True, capture_output=True,
        )

        # File A — will be committed then left unchanged
        file_a = tmp_dir_path / "stable.py"
        file_a.write_text(BASE_EXAMPLE_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        subprocess.run(["git", "add", "stable.py"], cwd=tmp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=tmp_dir, check=True, capture_output=True,
        )

        # File B — new/unstaged change
        file_b = tmp_dir_path / "changed.py"
        file_b.write_text(BASE_EXAMPLE_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        # stage it so git diff --cached picks it up
        subprocess.run(["git", "add", "changed.py"], cwd=tmp_dir, check=True, capture_output=True)

        stable_before = file_a.read_text(encoding="utf-8")
        changed_before = file_b.read_text(encoding="utf-8")

        result = subprocess.run(
            [str(gendocs_new), "--changed-only", str(tmp_dir_path)],
            capture_output=True,
            text=True,
            cwd=tmp_dir,
        )

        assert result.returncode == 0, f"gendocs_new --changed-only failed:\n{result.stderr}"

        # stable.py (committed, not modified) must be untouched
        assert file_a.read_text(encoding="utf-8") == stable_before, (
            "--changed-only must not modify files that have no git changes"
        )

        # changed.py (staged) should have been processed (docstrings added)
        assert file_b.read_text(encoding="utf-8") != changed_before, (
            "--changed-only should process files that are staged in git"
        )


# ---------------------------------------------------------------------------
# --changed-only --dry-run combined test
# ---------------------------------------------------------------------------

def test_changed_only_combined_with_dry_run():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"

    with TemporaryDirectory() as tmp_dir:
        tmp_dir_path = Path(tmp_dir)

        subprocess.run(["git", "init"], cwd=tmp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_dir, check=True, capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_dir, check=True, capture_output=True,
        )

        # Committed, stable file
        file_a = tmp_dir_path / "stable.py"
        file_a.write_text(BASE_EXAMPLE_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        subprocess.run(["git", "add", "stable.py"], cwd=tmp_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=tmp_dir, check=True, capture_output=True,
        )

        # Staged file that needs docstrings
        file_b = tmp_dir_path / "changed.py"
        file_b.write_text(BASE_EXAMPLE_FILE.read_text(encoding="utf-8"), encoding="utf-8")
        subprocess.run(["git", "add", "changed.py"], cwd=tmp_dir, check=True, capture_output=True)

        stable_before = file_a.read_text(encoding="utf-8")
        changed_before = file_b.read_text(encoding="utf-8")

        result = subprocess.run(
            [str(gendocs_new), "--changed-only", "--dry-run", str(tmp_dir_path)],
            capture_output=True,
            text=True,
            cwd=tmp_dir,
        )

        assert result.returncode == 0, (
            f"gendocs_new --changed-only --dry-run failed:\n{result.stderr}"
        )

        # Neither file must be modified on disk
        assert file_a.read_text(encoding="utf-8") == stable_before, (
            "--dry-run must not modify stable.py"
        )
        assert file_b.read_text(encoding="utf-8") == changed_before, (
            "--dry-run must not modify changed.py"
        )

        # stdout should contain a diff for the changed file (example.py has no docstrings)
        assert "+++" in result.stdout or "---" in result.stdout, (
            "--changed-only --dry-run should print a diff for changed files"
        )


# ---------------------------------------------------------------------------
# --ignore-private tests
# ---------------------------------------------------------------------------

def test_ignore_private_skips_private_functions():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"

    with NamedTemporaryFile(suffix=".py", delete=False, mode="w") as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(
            "def public_func(a: int) -> int:\n"
            "    return a\n"
            "\n"
            "def _private_func(a: int) -> int:\n"
            "    return a\n"
        )

    try:
        result = subprocess.run(
            [str(gendocs_new), "--ignore-private", str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"gendocs_new failed:\n{result.stderr}"

        content = tmp_path.read_text(encoding="utf-8")
        assert '"""' in content.split("def _private_func")[0], (
            "public function should have received a docstring"
        )
        assert '"""' not in content.split("def _private_func")[1], (
            "--ignore-private should leave private functions untouched"
        )
    finally:
        tmp_path.unlink(missing_ok=True)


def test_ignore_private_does_not_skip_dunder_methods():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"

    with NamedTemporaryFile(suffix=".py", delete=False, mode="w") as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(
            "class Foo:\n"
            "    def __init__(self, a: int) -> None:\n"
            "        self.a = a\n"
        )

    try:
        result = subprocess.run(
            [str(gendocs_new), "--ignore-private", str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"gendocs_new failed:\n{result.stderr}"

        content = tmp_path.read_text(encoding="utf-8")
        assert '"""' in content, (
            "--ignore-private should not skip dunder methods like __init__"
        )
    finally:
        tmp_path.unlink(missing_ok=True)


def test_ignore_private_via_pyproject_config():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir_path = Path(tmp_dir)

        (tmp_dir_path / "pyproject.toml").write_text(
            "[tool.docstring_generator]\nignore_private = true\n",
            encoding="utf-8",
        )
        sample = tmp_dir_path / "sample.py"
        sample.write_text(
            "def public_func(a: int) -> int:\n"
            "    return a\n"
            "\n"
            "def _private_func(a: int) -> int:\n"
            "    return a\n",
            encoding="utf-8",
        )

        gendocs_new = Path(sys.executable).parent / "gendocs_new"
        result = subprocess.run(
            [str(gendocs_new), str(sample)],
            capture_output=True,
            text=True,
            cwd=tmp_dir,
        )
        assert result.returncode == 0, f"gendocs_new failed:\n{result.stderr}"

        content = sample.read_text(encoding="utf-8")
        assert '"""' in content.split("def _private_func")[0]
        assert '"""' not in content.split("def _private_func")[1]


# ---------------------------------------------------------------------------
# --ignore-uncommented tests
# ---------------------------------------------------------------------------

def test_ignore_uncommented_skips_functions_without_docstring():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"

    with NamedTemporaryFile(suffix=".py", delete=False, mode="w") as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(
            "def has_docstring(a: int) -> int:\n"
            '    """Existing docstring."""\n'
            "    return a\n"
            "\n"
            "def no_docstring(a: int) -> int:\n"
            "    return a\n"
        )

    try:
        result = subprocess.run(
            [str(gendocs_new), "--ignore-uncommented", str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"gendocs_new failed:\n{result.stderr}"

        content = tmp_path.read_text(encoding="utf-8")
        has_docstring_part, no_docstring_part = content.split("def no_docstring")

        # the already-documented function should have been extended with parameter info
        assert "Parameters" in has_docstring_part, (
            "functions that already have a docstring must still be processed"
        )
        # the fully undocumented function must be left untouched
        assert '"""' not in no_docstring_part, (
            "--ignore-uncommented should leave functions without a docstring untouched"
        )
    finally:
        tmp_path.unlink(missing_ok=True)


def test_ignore_uncommented_via_pyproject_config():
    with TemporaryDirectory() as tmp_dir:
        tmp_dir_path = Path(tmp_dir)

        (tmp_dir_path / "pyproject.toml").write_text(
            "[tool.docstring_generator]\nignore_uncommented = true\n",
            encoding="utf-8",
        )
        sample = tmp_dir_path / "sample.py"
        sample.write_text(
            "def no_docstring(a: int) -> int:\n"
            "    return a\n",
            encoding="utf-8",
        )

        gendocs_new = Path(sys.executable).parent / "gendocs_new"
        result = subprocess.run(
            [str(gendocs_new), str(sample)],
            capture_output=True,
            text=True,
            cwd=tmp_dir,
        )
        assert result.returncode == 0, f"gendocs_new failed:\n{result.stderr}"

        content = sample.read_text(encoding="utf-8")
        assert '"""' not in content, (
            "--ignore-uncommented (via pyproject.toml) should leave undocumented functions untouched"
        )


# ---------------------------------------------------------------------------
# `# docstring: skip` / `# docstring: off` / `# docstring: on` directive tests
# ---------------------------------------------------------------------------

def test_skip_directive_file_level_leaves_file_untouched():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"

    with NamedTemporaryFile(suffix=".py", delete=False, mode="w") as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(
            "# docstring: skip\n"
            "\n"
            "def some_function(a: int) -> int:\n"
            "    return a\n"
        )

    try:
        original_content = tmp_path.read_text(encoding="utf-8")

        result = subprocess.run(
            [str(gendocs_new), str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"gendocs_new failed:\n{result.stderr}"

        assert tmp_path.read_text(encoding="utf-8") == original_content, (
            "a `# docstring: skip` comment within the first 10 lines must skip the whole file"
        )
    finally:
        tmp_path.unlink(missing_ok=True)


def test_skip_directive_single_target_skips_only_that_function():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"

    padding = "".join(f"# padding line {i}\n" for i in range(1, 11))
    source = (
        padding
        + "def helper_three(a: int) -> int:\n"
        + "    # docstring: skip\n"
        + "    return a\n"
        + "\n"
        + "def normal_func(a: int) -> int:\n"
        + "    return a\n"
    )

    with NamedTemporaryFile(suffix=".py", delete=False, mode="w") as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(source)

    try:
        result = subprocess.run(
            [str(gendocs_new), str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"gendocs_new failed:\n{result.stderr}"

        content = tmp_path.read_text(encoding="utf-8")
        helper_part, normal_part = content.split("def normal_func")

        assert '"""' not in helper_part, (
            "a `# docstring: skip` placed below a function must skip just that function"
        )
        assert '"""' in normal_part, (
            "functions without the skip directive must still be processed"
        )
    finally:
        tmp_path.unlink(missing_ok=True)


@pytest.mark.xfail(reason="Block skip via `# docstring: off` / `# docstring: on` is not honored by the extension")
def test_skip_directive_block_range_skips_everything_between():
    gendocs_new = Path(sys.executable).parent / "gendocs_new"

    padding = "".join(f"# padding line {i}\n" for i in range(1, 11))
    source = (
        padding
        + "def before_block(a: int) -> int:\n"
        + "    return a\n"
        + "\n"
        + "# docstring: off\n"
        + "def helper_one(a: int) -> int:\n"
        + "    return a\n"
        + "\n"
        + "\n"
        + "def helper_two(a: int) -> int:\n"
        + "    return a\n"
        + "# docstring: on\n"
        + "\n"
        + "def after_block(a: int) -> int:\n"
        + "    return a\n"
    )

    with NamedTemporaryFile(suffix=".py", delete=False, mode="w") as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(source)

    try:
        result = subprocess.run(
            [str(gendocs_new), str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"gendocs_new failed:\n{result.stderr}"

        content = tmp_path.read_text(encoding="utf-8")
        before, rest = content.split("def helper_one")
        block, after = rest.split("# docstring: on")

        assert '"""' in before, "functions before the block must still be processed"
        assert '"""' not in block, (
            "functions between `# docstring: off` and `# docstring: on` must be skipped"
        )
        assert '"""' in after, "functions after the block must still be processed"
    finally:
        tmp_path.unlink(missing_ok=True)


@pytest.mark.xfail
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
