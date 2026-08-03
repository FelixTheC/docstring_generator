import difflib
import pathlib
import shutil
import subprocess
import tempfile

import click
import docstring_generator_ext
import tomllib  # type: ignore

from docstring_generator.output import print_results

STYLE_MAP = {
    "rest": docstring_generator_ext.DocstringFormatStyle.reST,
    "google": docstring_generator_ext.DocstringFormatStyle.GOOGLE,
    "numpy": docstring_generator_ext.DocstringFormatStyle.NUMPY,
}


def find_pyproject_toml(start_paths: tuple[str, ...]) -> pathlib.Path | None:
    """
    Walks up parent directories from the target files/directories
    to discover the project root's pyproject.toml.
    
    Parameters
    ----------
    start_paths : tuple[str, Ellipsis] [Argument]

    Returns
    -------
    Union[pathlib.Path, None]
    """
    # Fallback to current working directory if no paths passed
    base_path = (
        pathlib.Path(start_paths[0]).absolute() if start_paths else pathlib.Path.cwd().absolute()
    )

    # If the base path is a file, start searching from its parent folder
    search_dir = base_path.parent if base_path.is_file() else base_path

    for parent in [search_dir] + list(search_dir.parents):
        potential_toml = parent / "pyproject.toml"
        if potential_toml.exists():
            return potential_toml

    return None


def load_toml_config(config_path: pathlib.Path | None) -> dict:
    """Finds and parses configuration options from pyproject.toml.
    Parameters
    ----------
    config_path : Union[pathlib.Path, None] [Argument]

    Returns
    -------
    dict
    """
    if not config_path or not config_path.exists():
        return {}

    with config_path.open("rb") as fp:
        toml_data = tomllib.load(fp)
    # Extract options from your custom namespace: [tool.docstring_generator]
    return toml_data.get("tool", {}).get("docstring_generator", {})


@click.command()
@click.argument("paths", nargs=-1, required=True)
@click.option(
    "--style", default="numpy", help="Docstring style [numpy, rest, google].", show_default=True
)
@click.option("--check", is_flag=True, help="Get an overview on the docstrings coverage.")
@click.option(
    "--strict",
    is_flag=True,
    help="Strict mode: Treats partial docstrings as missing/failed documentation.",
)
@click.option(
    "--threshold",
    type=click.IntRange(0, 100),
    default=None,
    help="Minimum required coverage percentage (0-100) to pass the check.",
)
@click.option("--exclude-file", type=str, multiple=True)
@click.option("--exclude-dir", type=str, multiple=True)
@click.option("--overwrite-style", is_flag=True, help="Overwrite existing docstrings.")
@click.option(
    "--ignore-magic", is_flag=True, help="Ignore dunder methods like `__init__`, `__str__`, etc."
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview changes as a unified diff without modifying any file.",
)
@click.option(
    "--changed-only",
    is_flag=True,
    help="Only process files changed or staged in git. Aborts if git is not available.",
)
def main(
    paths: tuple[str, ...],
    style: str,
    check: bool,
    strict: bool,
    threshold: int | None,
    exclude_file: list[str],
    exclude_dir: list[str],
    overwrite_style: bool,
    dry_run: bool,
    ignore_magic: bool,
    changed_only: bool,
) -> None:
    """
    Parameters
    ----------
    paths : tuple[str, Ellipsis] [Argument]
    style : str [Argument]
    check : bool [Argument]
    strict : bool [Argument]
    threshold : Union[int, None] [Argument]
    exclude_file : list[str] [Argument]
    exclude_dir : list[str] [Argument]
    overwrite_style : bool [Argument]
    dry_run : bool [Argument]
    ignore_magic : bool [Argument]
    changed_only : bool [Argument]

    Returns
    -------
    None
    """
    docstring_style = STYLE_MAP[style]

    config = load_toml_config(find_pyproject_toml(paths))
    _strict = strict or config.get("strict", False)
    _threshold = threshold or config.get("threshold", 100)
    _exclude_files = config.get("exclude_files", [])
    _exclude_dirs = config.get("exclude_dirs", [])
    _ignore_magic = config.get("ignore_magic", [])

    # CLI args always wins
    if exclude_file:
        _exclude_files = exclude_file
    if exclude_dir:
        _exclude_dirs = exclude_dir
    if ignore_magic:
        _ignore_magic = ignore_magic

    changed_files: set[str] | None = None
    if changed_only:
        if not shutil.which("git"):
            click.echo(
                "Error: --changed-only requires git, but git was not found on PATH. Aborting.",
                err=True,
            )
            import sys

            sys.exit(1)
        try:
            result_unstaged = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            result_staged = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
            )
            raw = result_unstaged.stdout + result_staged.stdout
            changed_files = {
                str(pathlib.Path(line.strip()).absolute())
                for line in raw.splitlines()
                if line.strip().endswith(".py")
            }
        except subprocess.CalledProcessError as e:
            click.echo(f"Error: git command failed: {e.stderr.strip()}", err=True)
            import sys

            sys.exit(1)

    files_ = []

    for path in paths:
        path_ = pathlib.Path(path)

        if not path_.exists():
            continue

        if path_.is_dir():
            files_.extend(path_.glob("**/*.py"))

        if path_.is_file() and path_.name.endswith(".py"):
            files_.append(path_)

    if changed_files is not None:
        files_ = [f for f in files_ if str(f.absolute()) in changed_files]

    if check:
        checked_files = {
            file.absolute().as_posix(): docstring_generator_ext.check_docstring(
                file.absolute().as_posix(), ignore_magic
            )
            for file in files_
        }
        if print_results(checked_files, _strict, _threshold) != 0:
            import sys

            return sys.exit(1)
    else:
        for file in files_:
            if file.name in _exclude_files or any(
                str(exclude_dir) in str(file) for exclude_dir in _exclude_dirs
            ):
                continue
            try:
                if dry_run:
                    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
                        tmp_path = pathlib.Path(tmp.name)
                    shutil.copy2(file, tmp_path)
                    try:
                        docstring_generator_ext.parse_file(
                            tmp_path.as_posix(), docstring_style, overwrite_style
                        )
                        original = file.read_text(encoding="utf-8").splitlines(keepends=True)
                        modified = tmp_path.read_text(encoding="utf-8").splitlines(keepends=True)
                        diff = list(
                            difflib.unified_diff(
                                original,
                                modified,
                                fromfile=f"a/{file}",
                                tofile=f"b/{file}",
                            )
                        )
                        if diff:
                            print("".join(diff))
                        else:
                            print(f"{file}: no changes")
                    finally:
                        tmp_path.unlink(missing_ok=True)
                else:
                    docstring_generator_ext.parse_file(
                        file.absolute().as_posix(), docstring_style, overwrite_style
                    )
            except SyntaxError as e:
                print(f"Error processing file {file}: {e}")
            except Exception as e:
                print(f"Error processing file {file}: {e}")


if __name__ == "__main__":
    main()
