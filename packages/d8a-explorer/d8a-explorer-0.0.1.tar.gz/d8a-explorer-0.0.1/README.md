# Explorer - An Exploratory Data Analysis Framework

[![PyPI](https://img.shields.io/pypi/v/explorer?style=flat-square)](https://pypi.python.org/pypi/explorer/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/explorer?style=flat-square)](https://pypi.python.org/pypi/explorer/)
[![PyPI - License](https://img.shields.io/pypi/l/explorer?style=flat-square)](https://pypi.python.org/pypi/explorer/)

---

**Documentation**: [https://john-james-ai.github.io/explorer](https://john-james-ai.github.io/explorer)

**Source Code**: [https://github.com/john-james-ai/explorer](https://github.com/john-james-ai/explorer)

**PyPI**: [https://pypi.org/project/explorer/](https://pypi.org/project/explorer/)

---

Exploratory Data Analysis Framework

## Installation

```sh
pip install explorer
```

## Development

* Clone this repository
* Requirements:
  * [Poetry](https://python-poetry.org/)
  * Python 3.7+
* Create a virtual environment and install the dependencies

```sh
poetry install
```

* Activate the virtual environment

```sh
poetry shell
```

### Testing

```sh
pytest
```

### Documentation

The documentation is automatically generated from the content of the [docs directory](./docs) and from the docstrings
 of the public signatures of the source code. The documentation is updated and published as a [Github project page
 ](https://pages.github.com/) automatically as part each release.

### Releasing

Trigger the [Draft release workflow](https://github.com/john-james-ai/explorer/actions/workflows/draft_release.yml)
(press _Run workflow_). This will update the changelog & version and create a GitHub release which is in _Draft_ state.

Find the draft release from the
[GitHub releases](https://github.com/john-james-ai/explorer/releases) and publish it. When
 a release is published, it'll trigger [release](https://github.com/john-james-ai/explorer/blob/master/.github/workflows/release.yml) workflow which creates PyPI
 release and deploys updated documentation.

### Pre-commit

Pre-commit hooks run all the auto-formatters (e.g. `black`, `isort`), linters (e.g. `mypy`, `flake8`), and other quality
 checks to make sure the changeset is in good shape before a commit/push happens.

You can install the hooks with (runs for each commit):

```sh
pre-commit install
```

Or if you want them to run only for each push:

```sh
pre-commit install -t pre-push
```

Or if you want e.g. want to run all checks manually for all files:

```sh
pre-commit run --all-files
```

---
