# FAQ

## What happens if I re-run docstring generation?

Nothing is lost. If the function signature hasn't changed, the existing docstring stays untouched. If you add or rename parameters, only the structural part is updated — your custom descriptions are preserved.

## Is it safe to use on an existing codebase?

Yes. The tool is non-destructive by design. It never deletes content; it only adds or updates parameter sections based on type hints.

## Does it work with class methods?

Yes — both standalone functions and class methods are fully supported.

## Does it handle `async` functions?

Yes. `async def` functions are treated identically to regular `def` functions — no extra configuration needed.

## Will `self` and `cls` appear in the generated docstring?

No. `self` and `cls` are automatically excluded from generated parameter sections, matching every major docstring standard.

## What if my project uses a different venv location?

For the JetBrains File Watcher, adjust the `program` path in `gendocs_file_watchers.xml` to point to your actual `gendocs_new` executable. For VS Code, ensure `gendocs_new` is on your system `PATH` or configure the full path in the extension settings.
