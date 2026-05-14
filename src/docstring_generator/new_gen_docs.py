import pathlib

import click
import docstring_generator_ext


@click.command()
@click.argument("path")
@click.option(
    "--style", default="numpy", help="Docstring style [numpy, rest, google].", show_default=True
)
def main(path: str, style: str) -> None:
    path_ = pathlib.Path(path)

    docstring_style = docstring_generator_ext.DocstringFormatStyle.NUMPY
    if style == "rest":
        docstring_style = docstring_generator_ext.DocstringFormatStyle.reST
    if style == "google":
        docstring_style = docstring_generator_ext.DocstringFormatStyle.GOOGLE

    if not path_.exists():
        return

    if path_.is_dir():
        for file in path_.glob("**/*.py"):
            docstring_generator_ext.parse_file(file.absolute().as_posix(), docstring_style)

    if path_.is_file() and path_.name.endswith(".py"):
        docstring_generator_ext.parse_file(path_.absolute().as_posix(), docstring_style)


if __name__ == "__main__":
    main()
