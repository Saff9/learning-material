---
title: Installation Guide
tags:
  - flask
  - installation
  - venv
  - poetry
  - uv
  - docker
aliases:
  - Flask Setup
  - Flask Install
  - Virtualenv for Flask
related:
  - "[[Flask-Overview]]"
  - "[[Project-Structure]]"
  - "[[Flask-SQLAlchemy]]"
created: 2024-01-15
updated: 2024-01-15
---

# Installation Guide

#flask #installation #venv #poetry #uv #docker

> [!info] From zero to running Flask app
> This note covers every realistic way to install Flask and its extensions: bare `venv`+`pip`, `pipenv`, `poetry`, the new `uv`, and Docker. Pick the one that matches your team; the result is the same.

A Flask install is two things: a **Python environment** (isolated from the system Python so you don't break your OS) and a **set of pinned dependencies** (so the app behaves identically on every machine). This note walks through both.

---

## Prerequisites

| Requirement | Minimum | Recommended |
|---|---|---|
| Python | 3.8 | 3.11 or 3.12 |
| pip | 21.0 | latest |
| Operating system | Linux / macOS / Windows | Linux or macOS for production |
| Git | any recent | latest |
| A database | SQLite (built-in) for dev | PostgreSQL 14+ for production |

> [!warning] Python 3.7 and below
> Flask 3.0 dropped Python 3.7 support. If you're stuck on 3.7, use Flask 2.3.x — but upgrade Python instead. Most extensions covered in this vault assume 3.8+.

### Check your Python

```bash
$ python3 --version
Python 3.12.3

$ python3 -m pip --version
pip 24.0
```

If `python3` isn't installed, install it from [python.org](https://www.python.org/downloads/) or your package manager:

```bash
# Ubuntu / Debian
$ sudo apt update && sudo apt install -y python3 python3-pip python3-venv

# macOS (Homebrew)
$ brew install python

# Windows: download from python.org, ensure "Add to PATH" is checked
```

```mermaid
flowchart TD
    Start[New Flask project] --> Q1{Team / preference?}
    Q1 -->|Classic, no extra tools| Venv[Approach 1: venv + pip<br/>+ pip-tools for pinning]
    Q1 -->|Modern standard, PEP 621| Poetry[Approach 3: poetry<br/>pyproject.toml + poetry.lock]
    Q1 -->|Fastest, Rust-powered| Uv[Approach 4: uv<br/>uv.lock, 10-100× faster]
    Q1 -->|Legacy / existing project| Pipenv[Approach 2: pipenv<br/>Pipfile + Pipfile.lock]
    Venv --> Q2{Production deployment?}
    Poetry --> Q2
    Uv --> Q2
    Pipenv --> Q2
    Q2 -->|Docker / k8s| Docker[Dockerfile + docker-compose<br/>see Docker section]
    Q2 -->|Bare metal / PaaS| Req[requirements/*.txt<br/>or lock file in image]
```

---

## Approach 1: `venv` + `pip` (the classic)

The Python standard library ships `venv`, a virtual environment creator. Combined with `pip` for installing packages, this is the simplest possible setup.

### Step 1 — Create a project directory

```bash
$ mkdir my_flask_app && cd my_flask_app
```

### Step 2 — Create a virtual environment

```bash
$ python3 -m venv venv
```

This creates a `venv/` folder containing a private Python interpreter and site-packages. Anything you `pip install` goes here, not into your system Python.

### Step 3 — Activate the environment

```bash
# Linux / macOS
$ source venv/bin/activate

# Windows (cmd)
C:\> venv\Scripts\activate.bat

# Windows (PowerShell)
PS> venv\Scripts\Activate.ps1
```

Your shell prompt will change to `(venv)`, indicating the environment is active.

> [!tip] VS Code auto-activation
> If you use VS Code, open the Command Palette → "Python: Select Interpreter" → choose `./venv/bin/python`. VS Code will auto-activate it in every terminal.

### Step 4 — Install Flask and extensions

```bash
(venv) $ pip install --upgrade pip
(venv) $ pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Login Flask-WTF
```

### Step 5 — Pin versions

```bash
(venv) $ pip freeze > requirements.txt
```

The resulting `requirements.txt` looks like:

```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
Flask-Login==0.6.3
Flask-WTF==1.2.1
# ... and ~30 transitive dependencies
```

### Step 6 — Reproduce the environment elsewhere

```bash
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

> [!warning] `pip freeze` is noisy
> It captures every transitive dependency, which makes diffs huge and upgrades painful. Use `pip-tools` (below) to keep a hand-curated `requirements.in` and auto-generate the locked `requirements.txt`.

### `pip-tools` — the upgrade

```bash
(venv) $ pip install pip-tools
```

Write a hand-curated `requirements.in`:

```
# requirements.in
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-Login
Flask-WTF
python-dotenv
gunicorn
```

Compile a fully-pinned `requirements.txt`:

```bash
(venv) $ pip-compile requirements.in
```

Sync the environment to exactly those versions:

```bash
(venv) $ pip-sync
```

This is the **most production-ready `pip` workflow**. Use it if you don't want to adopt Poetry/uv.

---

## Approach 2: `pipenv`

`pipenv` was the hip choice around 2018–2020. It combines `pip` + `virtualenv` + a `Pipfile` + a `Pipfile.lock`. It has since been eclipsed by Poetry and uv but is still maintained.

### Install

```bash
$ pip install --user pipenv
```

### Use

```bash
$ cd my_flask_app
$ pipenv install Flask Flask-SQLAlchemy Flask-Migrate
$ pipenv install --dev pytest pytest-flask
```

This creates `Pipfile` (curated) and `Pipfile.lock` (pinned).

### Run commands inside the env

```bash
$ pipenv run flask run
$ pipenv shell  # opens a subshell with the env active
```

> [!note] Why not pipenv?
> Pipenv is slow, has had security advisories, and the maintainers have been less active. New projects should prefer Poetry or uv.

---

## Approach 3: `poetry` (modern standard)

Poetry is the most popular modern Python dependency manager. It uses `pyproject.toml` (the PEP 621 standard) and a `poetry.lock` file.

### Install

```bash
# Linux / macOS
$ curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
PS> (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### Create a project

```bash
$ poetry new my_flask_app
# or, in an existing directory:
$ cd my_flask_app && poetry init
```

`poetry new` creates:

```
my_flask_app/
├── pyproject.toml
├── README.md
├── my_flask_app/
│   └── __init__.py
└── tests/
    └── __init__.py
```

### Add dependencies

```bash
$ poetry add flask flask-sqlalchemy flask-migrate flask-login flask-wtf
$ poetry add --group dev pytest pytest-flask factory-boy
```

Poetry writes these to `pyproject.toml`:

```toml
[tool.poetry]
name = "my-flask-app"
version = "0.1.0"
description = "A Flask app"
authors = ["You <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
flask = "^3.0.3"
flask-sqlalchemy = "^3.1.1"
flask-migrate = "^4.0.7"
flask-login = "^0.6.3"
flask-wtf = "^1.2.1"

[tool.poetry.group.dev.dependencies]
pytest = "^8.2.2"
pytest-flask = "^1.3.0"
factory-boy = "^3.3.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### Use

```bash
$ poetry install          # creates venv, installs everything from lock
$ poetry run flask run    # run a command in the venv
$ poetry shell            # spawn shell with venv active
$ poetry update           # bump versions per constraints, rewrite lock
```

> [!tip] Poetry pros
> - `pyproject.toml` is the PEP 621 standard — future-proof.
> - `poetry.lock` is reproducible across machines.
> - Build & publish to PyPI with `poetry build` and `poetry publish`.
> - Excellent dependency resolver (better than pip's historical resolver).

---

## Approach 4: `uv` (the new fast option)

`uv` is a Rust-based drop-in replacement for `pip`/`pip-tools`/`virtualenv`/`pipenv`/`poetry`, written by Astral (the same people behind Ruff). It is **10–100× faster** than pip and is rapidly becoming the default in 2024.

### Install

```bash
$ curl -LsSf https://astral.sh/uv/install.sh | sh
# or
$ pip install uv
```

### Create a project

```bash
$ uv init my_flask_app
$ cd my_flask_app
```

### Add dependencies

```bash
$ uv add flask flask-sqlalchemy flask-migrate flask-login flask-wtf
$ uv add --dev pytest pytest-flask
```

This creates a `pyproject.toml` and a `uv.lock`. The virtual environment lives in `.venv/`.

### Run

```bash
$ uv run flask run
$ uv sync          # install everything from lock (fast)
$ uv lock --upgrade  # bump versions
```

> [!tip] When to pick uv
> If you're starting fresh in 2024+, use uv. It's faster than everything else, supports the PEP 621 standard, and is actively developed. The only downside: ecosystem tooling (IDE plugins, CI templates) is still catching up.

---

## Installing Specific Versions

### Pin a single package

```bash
(venv) $ pip install "Flask==3.0.3"
(venv) $ pip install "Flask-SQLAlchemy>=3.1,<3.2"
(venv) $ pip install "Flask-Migrate~=4.0"   # compatible release: >=4.0, <5.0
```

### Install from git

```bash
(venv) $ pip install git+https://github.com/pallets/flask.git@3.0.x
```

### Install editable (for development)

```bash
# Clone Flask itself
$ git clone https://github.com/pallets/flask.git
$ cd my_flask_app
(venv) $ pip install -e ../flask
```

### Install from a local wheel

```bash
(venv) $ pip install ./Flask-3.0.3-py3-none-any.whl
```

---

## `requirements.txt` Best Practices

### Split into environments

```
# requirements/
├── base.txt        # everything needed to run the app
├── dev.txt         # base + dev tools
├── test.txt        # base + test deps
└── prod.txt        # base + production-only deps (gunicorn, sentry-sdk)
```

`requirements/base.txt`:

```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
Flask-Login==0.6.3
Flask-WTF==1.2.1
Flask-Mail==0.9.1
Flask-Caching==2.3.0
Flask-Limiter==3.8.0
Flask-Cors==4.0.1
Flask-JWT-Extended==4.6.0
Flask-Admin==2.0.1
Flask-RESTful==0.3.10
Flask-SocketIO==5.3.6
marshmallow==3.21.3
marshmallow-sqlalchemy==1.0.0
celery==5.4.0
redis==5.0.7
psycopg2-binary==2.9.9
python-dotenv==1.0.1
```

`requirements/dev.txt`:

```
-r base.txt
pytest==8.2.2
pytest-cov==5.0.0
pytest-flask==1.3.0
factory-boy==3.3.0
ipython==8.25.0
flask-debugtoolbar==0.15.1
```

`requirements/prod.txt`:

```
-r base.txt
gunicorn==22.0.0
sentry-sdk[flask]==2.6.0
psycopg2==2.9.9           # NOT -binary in prod; compile against system libpq
```

### Install the right file

```bash
# Dev
$ pip install -r requirements/dev.txt

# CI / production
$ pip install -r requirements/prod.txt
```

> [!warning] `psycopg2-binary` vs `psycopg2`
> The `-binary` variant bundles a precompiled libpq and is fine for development. In production, install plain `psycopg2` and compile against your system's libpq — the binary variant has caused subtle issues with connection pooling in some deployments.

---

## Environment Variables

### `.env` file with `python-dotenv`

Flask automatically loads `.env` and `.flaskenv` if `python-dotenv` is installed.

```bash
# .env (gitignored)
SECRET_KEY=abc123def456
DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
FLASK_ENV=development
```

```bash
# .flaskenv (committed)
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
```

```python
# In your code, just use os.environ
import os
secret = os.environ["SECRET_KEY"]
```

> [!danger] Never commit `.env`
> Add `.env` to `.gitignore`. Commit only `.env.example` with empty values. Countless production secrets have leaked because someone committed `.env` to a public repo.

### Loading `.env` manually

If you're not using the `flask` CLI (e.g., running via `gunicorn wsgi:app`), `python-dotenv` doesn't auto-load. Do it explicitly:

```python
# wsgi.py
from dotenv import load_dotenv
load_dotenv()  # reads .env from cwd

from app import create_app
app = create_app()
```

---

## Docker Setup

For production deployments and reproducible dev environments, Docker is the standard.

### `Dockerfile` (production-style, multi-stage)

```dockerfile
# deploy/Dockerfile
FROM python:3.12-slim AS builder

# Install build deps for psycopg2, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements/ /app/requirements/
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements/prod.txt

# --- runtime stage ---
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy venv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY . .

# Create non-root user
RUN useradd -m -u 1000 flask && chown -R flask:flask /app
USER flask

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "wsgi:app"]
```

### `docker-compose.yml` (full stack)

```yaml
# deploy/docker-compose.yml
version: "3.9"

services:
  web:
    build:
      context: ..
      dockerfile: deploy/Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ../.env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ../app:/app/app  # for dev hot-reload; remove in prod

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myapp"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  worker:
    build:
      context: ..
      dockerfile: deploy/Dockerfile
    command: celery -A celery_worker.celery worker --loglevel=info
    env_file:
      - ../.env
    depends_on:
      - redis

volumes:
  pgdata:
```

### Build & run

```bash
$ cd deploy
$ docker-compose up --build
```

Visit `http://localhost:8000`. Postgres is on `localhost:5432`, Redis on `localhost:6379`.

### `.dockerignore`

```
.git
.gitignore
__pycache__
*.pyc
*.pyo
venv/
.venv/
.env
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
```

> [!warning] Don't bake secrets into images
> Never `COPY .env` into a Docker image. Use `env_file` in Compose, `--env-file` in `docker run`, or a secrets manager (Vault, AWS Secrets Manager) in production.

---

## Verifying the Installation

### Smoke test

```bash
(venv) $ python -c "import flask; print(flask.__version__)"
3.0.3
```

### Run a real app

```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Install verified!"

if __name__ == "__main__":
    app.run(debug=True)
```

```bash
(venv) $ flask --app app run --debug
 * Running on http://127.0.0.1:5000
```

Open the URL — you should see "Install verified!".

### Check installed extensions

```bash
(venv) $ pip list | grep -i flask
Flask                  3.0.3
Flask-SQLAlchemy       3.1.1
Flask-Migrate          4.0.7
Flask-Login            0.6.3
Flask-WTF              1.2.1
```

---

## Common Installation Issues

### Issue: `error: externally-managed-environment`

This happens on newer Linux distros (Ubuntu 23.04+, Debian 12+) that block `pip install` at the system level.

**Fix**: Always use a virtualenv. If you really need system-wide installs:

```bash
$ pip install --user --break-system-packages Flask
# OR
$ pipx install flask  # for CLI tools only
```

### Issue: `ModuleNotFoundError: No module named 'flask'` after install

**Cause**: Your shell is using the system Python, not the venv.

**Fix**: Re-activate the venv (`source venv/bin/activate`) and check `which python` shows `./venv/bin/python`.

### Issue: `psycopg2` build fails

```
Error: pg_config executable not found.
```

**Cause**: PostgreSQL dev headers missing.

**Fix**:

```bash
# Ubuntu
$ sudo apt install libpq-dev python3-dev

# macOS
$ brew install postgresql

# OR switch to psycopg2-binary for dev
$ pip install psycopg2-binary
```

### Issue: `SSL: CERTIFICATE_VERIFY_FAILED` on macOS

macOS Python doesn't trust system certificates.

**Fix**:

```bash
# Run the Install Certificates.command script bundled with python.org installer
$ open "/Applications/Python 3.12/Install Certificates.command"

# OR
$ pip install --upgrade certifi
```

### Issue: Permission denied when installing

**Cause**: `pip` is trying to write to system site-packages.

**Fix**: Never use `sudo pip install`. Use a venv, or `pip install --user`.

```mermaid
pie showData
    title Distribution of Flask install issues (by support tickets)
    "externally-managed-environment" : 25
    "Module not found after install" : 22
    "psycopg2 build fails" : 18
    "Permission denied" : 12
    "SSL certificate verify failed (macOS)" : 10
    "Wrong Python version" : 8
    "Other" : 5
```

---

## The Authoritative Setup (Recommended)

For a new project in 2024, the author recommends:

1. **Python 3.12** via `pyenv` or system package.
2. **`uv`** for dependency management (fast, modern, PEP 621-compliant).
3. **Docker Compose** for the dev database (Postgres + Redis).
4. **`.env` + `python-dotenv`** for secrets.
5. **`gunicorn`** in production.

```bash
# One-time setup
$ curl -LsSf https://astral.sh/uv/install.sh | sh
$ uv init my_flask_app && cd my_flask_app
$ uv add flask flask-sqlalchemy flask-migrate flask-login flask-wtf \
        python-dotenv psycopg2-binary redis marshmallow
$ uv add --dev pytest pytest-flask factory-boy ipython flask-debugtoolbar

# Database via Docker
$ docker run -d --name pg -p 5432:5432 \
    -e POSTGRES_DB=myapp -e POSTGRES_USER=myapp -e POSTGRES_PASSWORD=dev \
    postgres:16-alpine

# Write .env, then run
$ uv run flask --app run.py run --debug
```

---

## Next Steps

- [[Project-Structure]] — lay out your app's files.
- [[Flask-Overview]] — understand what you just installed.
- [[Flask-SQLAlchemy]] — your first database.
- [[Flask-Migrate]] — version-control the schema.
- [[Production-Deployment]] — put it on the internet.

---

## References

- [Flask installation docs](https://flask.palletsprojects.com/en/latest/installation/)
- [Python venv docs](https://docs.python.org/3/library/venv.html)
- [pip docs](https://pip.pypa.io/en/stable/)
- [pip-tools](https://pip-tools.readthedocs.io/)
- [Poetry docs](https://python-poetry.org/docs/)
- [uv docs](https://docs.astral.sh/uv/)
- [Docker for Python](https://docs.docker.com/language/python/)
- [pyenv](https://github.com/pyenv/pyenv) — manage multiple Python versions.

---

## Managing Multiple Python Versions

Different projects need different Python versions. Don't install Python 3.12 system-wide and break a project that needs 3.10. Use `pyenv` (or `uv python install`) to manage versions per-project.

### pyenv

```bash
# Install pyenv
$ curl https://pyenv.run | bash

# Add to shell rc:
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"

# Install a Python version
$ pyenv install 3.12.3
$ pyenv install 3.11.9

# Set per-project
$ cd my_flask_app
$ pyenv local 3.12.3   # creates .python-version file
```

When you `cd` into the directory, the shell automatically uses the right Python.

### uv (simpler)

```bash
$ uv python install 3.12 3.11
$ uv python pin 3.12
```

### asdf (multi-language)

If you also use Node, Ruby, etc., [asdf](https://asdf-vm.com/) manages all of them with one tool. Useful if you're a polyglot.

### Per-project version pinning

Always commit `.python-version` (pyenv) or `requires-python` in `pyproject.toml`:

```toml
# pyproject.toml
[project]
requires-python = ">=3.11,<3.13"
```

This prevents teammates from accidentally using Python 3.13 (which might break a dependency).

---

## Editor Setup

A good editor makes a huge difference. Here are the recommended setups.

### VS Code

Install these extensions:

- **Python** (Microsoft) — language server, debugging, formatting.
- **Pylance** — fast type checking.
- **Ruff** (Astral) — linting + formatting (replaces black, isort, flake8).
- **ms-python.black-formatter** — if you prefer Black over Ruff.
- **Flask-Snippets** — quick templates (optional).

Workspace settings (`.vscode/settings.json`):

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true
  }
}
```

### PyCharm

- Set the project interpreter to your venv (`./venv/bin/python`).
- Enable "Flask" facet (PyCharm recognizes Flask apps automatically).
- Configure pytest as the test runner.
- Use the built-in database tool for inspecting Postgres.

### Neovim

Use `nvim-lspconfig` with `pyright` or `ruff-lsp`. Add a `flake8`/`ruff` linter via `null-ls` or `nvim-lint`. See [kickstart.nvim](https://github.com/nvim-lua/kickstart.nvim) for a starting point.

### Jupyter (for exploration)

If you use notebooks for data exploration against your Flask models:

```bash
(venv) $ pip install jupyter ipython
(venv) $ flask shell  # OR: jupyter lab
```

```python
# In the notebook:
from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()
app.app_context().push()

User.query.limit(10).all()
```

---

## Dependency Management Deep Dive

### Why pin versions?

Unpinned dependencies (`Flask` instead of `Flask==3.0.3`) mean "install whatever is latest." This is fine for a quick prototype but breaks down because:

1. **Reproducibility**: tomorrow's install may differ from today's.
2. **CI fails mysteriously**: a transitive dep released a new version with a bug.
3. **Production drift**: dev has `Flask==3.0.3`, prod has `Flask==3.0.4`, behavior differs.

### Pinning strategies

```mermaid
quadrantChart
    title Python dependency managers compared
    x-axis "Slower" --> "Faster"
    y-axis "Less reproducible" --> "More reproducible"
    quadrant-1 "Fast & reproducible"
    quadrant-2 "Slow & reproducible"
    quadrant-3 "Slow & loose"
    quadrant-4 "Fast & loose"
    "pip + requirements.txt": [0.35, 0.55]
    "pip-tools": [0.3, 0.85]
    "pipenv": [0.2, 0.75]
    "poetry": [0.55, 0.9]
    "uv": [0.95, 0.92]
```

| Strategy | File | Pros | Cons |
|---|---|---|---|
| **Loose** (`Flask`) | `requirements.in` | Always get latest patches. | Non-reproducible. |
| **Compatible** (`Flask~=3.0`) | `requirements.in` | Patch + minor updates. | Still drifts. |
| **Pinned** (`Flask==3.0.3`) | `requirements.txt` | Fully reproducible. | Must manually bump. |
| **Locked** (`poetry.lock`/`uv.lock`) | lock file | Reproducible + locked transitives. | Lock file churns. |

> [!tip] Best practice
> Curate top-level deps in `requirements.in` (or `pyproject.toml`) with compatible-release constraints. Generate a fully-pinned `requirements.txt` (or `poetry.lock`) for deployment. Use the lock file in production.

### Upgrading dependencies

```bash
# pip-tools
$ pip-compile --upgrade requirements.in      # bumps all
$ pip-compile --upgrade-package Flask        # bumps just Flask

# poetry
$ poetry update flask

# uv
$ uv lock --upgrade-package flask
```

Always run tests after upgrading. Security-critical packages (`Flask`, `werkzeug`, `cryptography`, `requests`) deserve a closer review.

### Security scanning

```bash
(venv) $ pip install pip-audit
(venv) $ pip-audit
```

This checks installed packages against the [PyPI advisory database](https://github.com/pypa/advisory-database). Add to CI:

```yaml
# .github/workflows/audit.yml
name: Security audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install pip-audit
      - run: pip-audit -r requirements/prod.txt
```

---

## Summary: The 5-Minute Setup

If you read nothing else in this note, follow these steps:

```mermaid
gantt
    title 5-minute Flask setup timeline (using uv + Docker)
    dateFormat ss
    axisFormat %Ss
    section Tooling
    Install uv            :a1, 0, 10s
    uv init project        :a2, after a1, 5s
    uv add deps            :a3, after a2, 15s
    uv add --dev test deps :a4, after a3, 10s
    section Infra
    docker run postgres    :b1, after a4, 10s
    write .env             :b2, after b1, 10s
    section Verify
    flask run --debug      :c1, after b2, 5s
    smoke test :5000       :c2, after c1, 5s
    section Total
    Done                   :milestone, after c2, 0s
```

```bash
# 1. Install uv (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create project
uv init my_flask_app && cd my_flask_app

# 3. Add Flask + extensions
uv add flask flask-sqlalchemy flask-migrate flask-login flask-wtf \
       python-dotenv psycopg2-binary

# 4. Add dev deps
uv add --dev pytest pytest-flask factory-boy ipython

# 5. Start Postgres + Redis in Docker
docker run -d --name pg -p 5432:5432 \
  -e POSTGRES_DB=myapp -e POSTGRES_USER=myapp -e POSTGRES_PASSWORD=dev \
  postgres:16-alpine

# 6. Write .env
cat > .env <<'EOF'
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=postgresql://myapp:dev@localhost:5432/myapp
EOF

# 7. Run
uv run flask --app run.py run --debug
```

You now have a fully reproducible Flask environment in under 5 minutes. The rest of this vault's notes assume you have this foundation.

---

*See also: [[Flask-Overview]] · [[Project-Structure]] · [[00-Map-of-Content]]*
