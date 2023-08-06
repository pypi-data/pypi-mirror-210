# Who is concerned by this file

This file is for:

- Project owners - creators and maintainers of the project
- Project contributors - users of the project who want to know items they're welcome to tackle, and
  tact they need in navigating the project/respecting those involved with the project
- Project consumers - users who want to build off the project to create their own project

## Testing

### Installation

```bash
pip install -e .[ALL]
pre-commit install
```

Run pre-commit hooks on all files:

```bash
pre-commit run --all-files
```

This will run the following hooks:

- `black`
- `flake8`
- `isort`
- `mypy`

### Running tests

```bash
pytest
```

# Pypi share

```bash
pip install -r build-requirements.txt
pip install --upgrade twine
python -m build
python -m twine upload --repository pypi dist/*
```

