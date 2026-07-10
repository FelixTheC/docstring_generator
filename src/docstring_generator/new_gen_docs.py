import pathlib

import click
import docstring_generator_ext


@click.command()
@click.argument("paths", nargs=-1, required=True)
@click.option(
    "--style", default="numpy", help="Docstring style [numpy, rest, google].", show_default=True
)
def main(paths: tuple[str, ...], style: str) -> None:
    docstring_style = docstring_generator_ext.DocstringFormatStyle.NUMPY
    if style == "rest":
        docstring_style = docstring_generator_ext.DocstringFormatStyle.reST
    if style == "google":
        docstring_style = docstring_generator_ext.DocstringFormatStyle.GOOGLE

    for path in paths:
        path_ = pathlib.Path(path)

        if not path_.exists():
            continue

        if path_.is_dir():
            for file in path_.glob("**/*.py"):
                docstring_generator_ext.parse_file(file.absolute().as_posix(), docstring_style)

        if path_.is_file() and path_.name.endswith(".py"):
            try:
                docstring_generator_ext.parse_file(path_.absolute().as_posix(), docstring_style)
            except SyntaxError as e:
                print(f"Error processing file {path_}: {e}")


if __name__ == "__main__":
    main()
