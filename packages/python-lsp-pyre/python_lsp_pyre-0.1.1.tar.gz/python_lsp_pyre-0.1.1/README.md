# python-lsp-pyre

Implements support for calling Meta's [Pyre type checker](https://github.com/facebook/pyre-check) via a subprocess.

This is a plugin for the [Python LSP Server](https://github.com/python-lsp/python-lsp-server).

It was written to scratch an itch, so may not be quite what you're looking for.

## Installation

To use this plugin, you need to install this plugin in the same virtualenv as `python-lsp-server` itself.

```bash
pip install python-lsp-pyre
```

or to make it a development requirement in Poetry

```bash
poetry add -G dev python-lsp-pyre
```

Then run `python-lsp-server` as usual, the plugin will be auto-discovered by
`python-lsp-server` if you've installed it to the right environment. Refer to
`python-lsp-server` and your IDE/text editor documentation on how to setup
`python-lsp-server`. An example is provided for KDE's [Kate editor](/docs/kate.md).

## Configuration

Meta's Pyre uses `.pyre_configuration` files in your project to set up lint controls. It does not read `pyproject.toml`.

On first run of this plugin, it will detect a missing `.pyre_configuration`, and write out one for you. It relies on the workspace root passed to the language server for this write. This file is not immutable, and the [reference documentation](https://pyre-check.org/docs/configuration/) may be useful.

You can also use `pyre init` instead to set up the configuration.

The configuration written by this plugin is:

```json
{
    "site_package_search_strategy": "all",
    "source_directories": [
        "."
    ],
    "exclude": [
        "/setup.py",
        ".*/build/.*"
    ]
}
```

The noteable difference from `pyre init` is the change to the search strategy (pep561 to all).

## Features

This plugin adds the following features to `pylsp`:

- Type linting via Meta's Pyre (pyre-check)

## Developing

Install development dependencies with (you might want to create a virtualenv first):

```bash
git clone https://github.com/cricalix/python-lsp-pyre python-lsp-pyre
cd python-lsp-pyre
pip install -e '.[dev]'
```

Alterately, if you use Poetry,
```
poetry install
```

will set up a virtualenv if necessary, install all dependencies, and then install this project in editable/development mode.
