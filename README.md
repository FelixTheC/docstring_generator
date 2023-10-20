[![Python 3.10](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/docstring-generator.svg)](https://badge.fury.io/py/docstring-generator)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![](https://img.shields.io/pypi/dm/docstring-generator.svg)](https://pypi.org/project/docstring-generator/)

# docstring_generator
Auto generate docstring from type-hints for python functions and class methods.

## How to use it

```shell
gendocs_new file.py
```

```shell
gendocs_new mydir/
```

## Options

### style

- `--style`
- Docstring style [numpy, google, rest].  [default: numpy]

### Add additional information before running `gendocs_new` 

- when adding `$<num>` into your docstring these will then be replaced with parameter at this index
- Example:
```python
from typing import List


def foo(val_a: int, val_b: List[int]):
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam

    $1 Lorem ipsum dolor sit amet
    $2 nonumy eirmod tempor invidun
    """
```
will become (here with numpy style)
```python
from typing import List


def foo(val_a: int, val_b: List[int]):
    """
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
    sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam
    
    Parameters
    ----------
    val_a : argument of type int
        Lorem ipsum dolor sit amet
    val_b : argument of type List(int)
        nonumy eirmod tempor invidun

    """
```

## FAQ

### what happens if I re-run the docstring creation?

- nothing if all stays the same, changed parameter descriptions will be ignored only changes of the function header will be used

## Examples
- An example can be found under examples

## Installing

- pip install docstring-generator

## Dependency `docstring-generator-ext`

- this extension is the heart of this project and written with pybind11 (c++)

## Versioning

- For the versions available, see the tags on this repository.

## Authors

- Felix Eisenmenger

## License

- MIT License (MIT)