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


@pytest.mark.parametrize("style", ("numpy", "rest", "google"))
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
    """
    Parameters
    ----------
    test_file : [Argument]
    """
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


@pytest.mark.parametrize("test_file", EXPECTED_FILES.values())
def test_check_coverage_full_coverage_with_ignore_magic(test_file):
    """
    Parameters
    ----------
    test_file : [Argument]
    """
    from src.docstring_generator.new_gen_docs import main
    main(["--check", "--ignore-magic", "--threshold", "95", str(test_file)], standalone_mode=False)

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
