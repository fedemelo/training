This project uses a Python 3.13 virtual environment that should always be activated when working on the codebase.
```shell
source venv/bin/activate
```

The project uses automated quality checks.

Format code:
```shell
isort . && black .
```

Lint code:
```shell
flake8
```

Run tests:
```shell
pytest
```