# Using Pip

## setup virtual enviroment and package installation using Pip (Legacy)
```bash
# Using Pip

# Create virtual environment
python3 -m venv .venv

# Activate (Mac/Linux)
source .venv/bin/activate

# Install package
pip install sqlalchemy psycopg2-binary

# deactivate venv
deactivate
```

## setup venv and installation using uv

### Prerequist
``` bash
# install uv
pip install uv
```

```bash
# Create virtual environment and activate it
uv venv

# Activate (Mac/Linux)
source .venv/bin/activate

# Install SQLAlchemy
uv pip install sqlalchemy psycopg2-binary


# Extra

# Freeze dependencies
uv pip freeze > requirements.txt

# Install from requirements.txt
uv pip install -r requirements.txt
```

⬆️ reason to use uv