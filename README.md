# docstring_generator
Auto generate docstring from type-hints

## How to use it
```shell
gendocs file.py
```

```shell
gendocs mydir/
```

## Options

### style
- `--style`
- Docstring style [numpy, rest].  [default: numpy]

### ignore-classes
- `--ignore-classes`
- when used then no class will be modified

### ignore-functions
- `--ignore-functions`
- when used then no function will be modified this
- __!important__ class methods are no functions in this context


### Add additional information before running `gendocs` 
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

## Examples
- An example can be found under examples

### Installing

- pip install docstring-generator

#### Versioning
- For the versions available, see the tags on this repository.

### Authors
- Felix Eisenmenger

### License
- This project is licensed under the MIT License - see the LICENSE.md file for details
