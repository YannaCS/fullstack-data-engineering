## Installing dependency

run in project directory with venv activated:

```bash
# install packages
uv pip install pytest requests pytest-cov

# frezze dependencies
uv pip freeze > requirements.txt
```

```bash
# run test at root directory
pytest

# run with coverage
pytest --cov=app  --cov-report=term-missing
```