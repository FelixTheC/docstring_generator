# Roadmap

Planned features and areas of investment.

## Medium-term

- [x] File Watcher configuration for JetBrains IDEs (PyCharm) — import `gendocs_file_watchers.xml` to auto-generate docstrings on every file save
- [x] VS Code extension — available on the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=felixthec.docstring-generator-vscode)
- [ ] GitHub Action — publish a ready-to-use Action to the Marketplace so teams can enforce docstring coverage in CI without any local installation
- [ ] Coverage badge generation (`--badge`) — produce an SVG badge from `--check` results to embed in README, similar to a test-coverage badge
- [ ] JUnit/SARIF output for `--check` — emit machine-readable results for GitHub, GitLab, and Azure DevOps CI panels; enables PR annotations that highlight undocumented functions inline

## Longer-term

- [ ] Watch mode (`--watch`) — monitor the project for file saves and regenerate docstrings automatically in the background
- [ ] Sphinx / mkdocs bridge (`--export-rst`) — generate `.rst` or `.md` stubs ready for Sphinx/mkdocs autodoc pipelines
- [ ] Custom docstring templates — let teams define their own format via `pyproject.toml` for internal style guides that extend NumPy or Google
- [ ] LLM-assisted description generation (opt-in enrichment mode) — use a local or remote LLM to fill in meaningful parameter descriptions beyond the type hint
- [ ] CI/CD pipeline gate (fail build below coverage threshold)

Community feedback shapes priorities — open an [issue](https://github.com/FelixTheC/docstring_generator/issues) to vote on features or suggest new ones.
