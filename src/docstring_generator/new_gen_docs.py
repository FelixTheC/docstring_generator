import pathlib

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
    """Finds and parses configuration options from pyproject.toml."""
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
# @click.option("--overwrite-style", type=bool, default=False)
def main(
    paths: tuple[str, ...],
    style: str,
    check: bool,
    strict: bool,
    threshold: int | None,
    exclude_file: list[str],
    exclude_dir: list[str],
    # overwrite_style: bool,
) -> None:
    docstring_style = STYLE_MAP[style]

    config = load_toml_config(find_pyproject_toml(paths))
    _strict = strict or config.get("strict", False)
    _threshold = threshold or config.get("threshold", 100)
    _exclude_files = config.get("exclude_files", [])
    _exclude_dirs = config.get("exclude_dirs", [])

    # CLI args always wins
    if exclude_file:
        _exclude_files = exclude_file
    if exclude_dir:
        _exclude_dirs = exclude_dir

    files_ = []

    for path in paths:
        path_ = pathlib.Path(path)

        if not path_.exists():
            continue

        if path_.is_dir():
            files_.extend(path_.glob("**/*.py"))

        if path_.is_file() and path_.name.endswith(".py"):
            files_.append(path_)

    if check:
        checked_files = {
            file.absolute().as_posix(): docstring_generator_ext.check_docstring(
                file.absolute().as_posix()
            )
            for file in files_
        }
        print_results(checked_files, _strict, _threshold)
    else:
        for file in files_:
            if file.name in _exclude_files or any(str(exclude_dir) in str(file) for exclude_dir in _exclude_dirs):
                continue
            try:
                docstring_generator_ext.parse_file(file.absolute().as_posix(), docstring_style)
            except SyntaxError as e:
                print(f"Error processing file {file}: {e}")


if __name__ == "__main__":
    main()
