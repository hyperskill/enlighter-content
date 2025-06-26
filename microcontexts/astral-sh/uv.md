# uv - Python Package Manager

## Installation

### macOS and Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Via pip
```bash
pip install uv
```

### Via pipx
```bash
pipx install uv
```

## Verifying Installation
```shell
$ uv
An extremely fast Python package manager.

Usage: uv [OPTIONS]
```

## Virtual Environments

### Creating a Virtual Environment
```console
$ uv venv
Using Python 3.12.3
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate
```

### Creating with Specific Python Version
```shell
uv venv --python 3.11.6
```

### Activating Virtual Environment (macOS/Linux)
```console
$ source .venv/bin/activate
```

## Project Management

### Managing Python Projects
```bash
$ uv init example
Initialized project `example` at `/home/user/example`

$ cd example

$ uv add ruff
Creating virtual environment at: .venv
Resolved 2 packages in 170ms
   Built example @ file:///home/user/example
Prepared 2 packages in 627ms
Installed 2 packages in 1ms
 + example==0.1.0 (from file:///home/user/example)
 + ruff==0.5.0

$ uv run ruff check
All checks passed!

$ uv lock
Resolved 2 packages in 0.33ms

$ uv sync
Resolved 2 packages in 0.70ms
Audited 1 package in 0.02ms
```

### Adding Dependencies
```console
$ uv add httpx
```

## Dependency Management

### Installing from pyproject.toml
```console
$ uv pip install -r pyproject.toml
```

### Installing Locked Requirements
```console
$ uv pip sync docs/requirements.txt
Resolved 43 packages in 11ms
Installed 43 packages in 208ms
 + babel==2.15.0
 + black==24.4.2
 + certifi==2024.7.4
 ...
```

### Installing External Project as Editable
```console
$ uv pip install -e "ruff @ ./project/ruff"
```

### Freezing Environment
```shell
$ uv pip freeze
```

### Executing Script with Dependency
```console
$ uv run --with rich example.py
For example: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:01
```

## Package Building and Publishing

### Building Python Package
```console
$ uv build
```

### Publishing Python Package
```console
$ uv publish
```

## Docker Integration

### Multi-stage Docker Build
```Dockerfile
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-editable

# Copy the project into the intermediate image
ADD . /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

FROM python:3.12-slim

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Run the application
CMD ["/app/.venv/bin/hello"]
```

### Installing Project in Docker
```Dockerfile
COPY pyproject.toml .
RUN uv pip install -r pyproject.toml
COPY . .
RUN uv pip install -e .
```

## Configuration Examples

### Project Dependencies in pyproject.toml
```toml
[project]
name = "albatross"
version = "0.1.0"
dependencies = [
  # Any version in this range
  "tqdm >=4.66.2,<5",
  # Exactly this version of torch
  "torch ==2.2.2",
  # Install transformers with the torch extra
  "transformers[torch] >=4.39.3,<5",
  # Only install this package on older python versions
  # See "Environment Markers" for more information
  "importlib_metadata >=7.1.0,<8; python_version < '3.10'",
  "mollymawk ==0.1.0"
]
```

### AWS Lambda Example
```toml
[project]
name = "uv-aws-lambda-example"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    # FastAPI is a modern web framework for building APIs with Python.
    "fastapi",
    # Mangum is a library that adapts ASGI applications to AWS Lambda and API Gateway.
    "mangum",
]

[dependency-groups]
dev = [
    # In development mode, include the FastAPI development server.
    "fastapi[standard]>=0.115",
]
```

### Running FastAPI Application Locally
```console
$ uv run fastapi dev
```
