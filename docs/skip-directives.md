# Skip Directives

CLI flags like `--ignore-private` or `--exclude-file` apply uniformly to a whole run. Sometimes you need something more surgical — skip *this one file*, *this one function*, or *this group of helpers* — without changing how the rest of the codebase is processed.

For that, `docstring_generator` understands special `# docstring: ...` comments directly in your source code. Three scopes are supported.

---

## 1. File-level skip

Place `# docstring: skip` within the **first 10 lines** of the file to skip the entire file — nothing in it will be touched:

```python
# docstring: skip

def some_function():
    return None
```

Running `gendocs_new` on this file leaves it byte-for-byte unchanged. This is the right choice for generated files, vendored code, or files you never want auto-documented.

> The directive must appear within the first 10 lines. If it appears later, it is treated as a comment and has no effect at the file level.

---

## 2. Single-target skip

Place the directive as the **first statement inside a function or method body** to skip just that one target:

```python
def helper_three(a: int) -> int:
    # docstring: skip
    return a


def normal_func(a: int) -> int:
    return a
```

Here, only `helper_three` is left untouched — `normal_func` still gets a docstring generated normally. This is the most precise way to opt a single function or method out of documentation, e.g. for trivial one-liners or intentionally undocumented internals.

---

## 3. Block/Range skip

Wrap a group of functions or classes between `# docstring: off` and `# docstring: on` to skip everything in between:

```python
# docstring: off
def helper_one():
    ...


def helper_two():
    ...
# docstring: on
```

!!! warning "Known limitation"
    In the current version of the underlying `docstring-generator-ext` engine, only the function **immediately following** `# docstring: off` is reliably skipped. Additional functions further down in the block (before the matching `# docstring: on`) may still receive generated docstrings. This is tracked as a known issue — until it's fixed upstream, prefer the [single-target skip](#2-single-target-skip) directive on each function you want to exclude if you need a guarantee that *every* function in a range is skipped.

---

## Choosing the right scope

| Scope | Directive | Effect |
|-------|-----------|--------|
| File-level | `# docstring: skip` (first 10 lines) | Skips the entire file |
| Single-target | `# docstring: skip` (first line inside a function/method body) | Skips just that function/method |
| Block/range | `# docstring: off` ... `# docstring: on` | Intended to skip everything in between (see limitation above) |

These directives compose with all CLI flags — e.g. you can run `gendocs_new --ignore-magic mydir/` while still using `# docstring: skip` to opt individual functions out of documentation.
