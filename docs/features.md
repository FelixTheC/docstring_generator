# Features

## Preserve Custom Descriptions with `$<num>` Placeholders

Write your domain-specific notes once — `docstring_generator` will place them in the right parameter slot automatically.

Use `$1`, `$2`, … in your docstring body to map descriptions to positional parameters:

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

After running `gendocs_new` (NumPy style):

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

---

## Preserve Return Description with `>>` Marker

Use `>>` on its own line inside an existing docstring to provide a description for the return value. On the next `gendocs_new` run the marker is consumed and wired into the `Returns` section automatically.

```python
def square(x: int) -> int:
    """Square a number.

    >> The squared value of x.
    """
    return x * x
```

After running `gendocs_new` (Google style):

```python
def square(x: int) -> int:
    """Square a number.

    Args:
        x (int):
    Returns:
        int: The squared value of x.
    """
    return x * x
```

Combine `$N` for parameter descriptions and `>>` for the return description to fully annotate a function before running the generator — no manual editing of the structured sections needed.

---

## Automatic `Raises` Extraction

`docstring_generator` statically analyzes your function body for `raise` statements and adds a `Raises` section describing each exception — including the condition that triggers it. This works seamlessly with frameworks like **Pydantic**, **FastAPI**, or any custom validation logic.

### Before

```python
class PluginConfig(BaseModel):
    name: str = Field(default="default")
    api_config: dict = Field(default_factory=dict)

    @field_validator("api_config", mode='before')
    @classmethod
    def validate_api_config(cls, values: dict) -> dict:
        required_key_obj = values.get("required_keys", None)
        if not required_key_obj:
            raise ValueError("The first key must be 'required_keys'")
        if not isinstance(required_key_obj, dict):
            raise ValueError("The 'required_keys' must be a dict")
        return values
```

### After running `gendocs_new`

```python
class PluginConfig(BaseModel):
    name: str = Field(default="default")
    api_config: dict = Field(default_factory=dict)

    @field_validator("api_config", mode='before')
    @classmethod
    def validate_api_config(cls, values: dict) -> dict:
        """
        Parameters
        ----------
        values : dict [Argument]

        Returns
        -------
        dict

        Raises
        -------
        ValueError
            If not isinstance(required_key_obj, dict)
        ValueError
            If not required_key_obj
        """
        required_key_obj = values.get("required_keys", None)
        if not required_key_obj:
            raise ValueError("The first key must be 'required_keys'")
        if not isinstance(required_key_obj, dict):
            raise ValueError("The 'required_keys' must be a dict")
        return values
```

Every `raise` — even multiple ones in the same function — is captured, so complex validators document all their failure modes at once.
