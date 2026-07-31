---
title: Flask-Environments
tags:
  - flask
  - configuration
  - environments
  - dev-prod-test
  - config-inheritance
  - flask-env
  - twelve-factor
aliases:
  - flask-environments
  - flask-env
  - flask-config
  - environment-classes
  - config-inheritance
related:
  - "[[Pydantic-Settings]]"
  - "[[Flask-Injector]]"
  - "[[Flask-FeatureFlags]]"
  - "[[Flask-SQLAlchemy]]"
  - "[[Flask-Caching]]"
created: 2024-01-15
updated: 2024-01-15
---

# Flask-Environments

#flask #configuration #environments #dev-prod-test #config-inheritance #flask-env #twelve-factor

> [!info] Environment-aware configuration for Flask
> **Flask-Environments** is the practice — and a small family of libraries — of selecting different configuration objects based on the deployment environment (development, staging, production, test). Flask itself supports this natively via `app.config.from_object()`; the `Flask-Environments` package and its peers (`python-dotenv`, `dynaconf`) add sugar on top: environment auto-detection, config inheritance, per-environment `.env` files, and CLI helpers.
>
> Paired with [[Pydantic-Settings]] (which gives each environment a typed `Settings` class) and [[Flask-Injector]] (which injects the selected settings into services), this gives you a config story where the same code runs unchanged from a developer laptop to a Kubernetes pod — only the environment variables and config class differ.

Think of Flask-Environments as a **wardrobe for your app**. The app is the same person, but it wears different clothes to different occasions: sweatpants and slippers at home (dev), a clean shirt at the office (staging), and a tailored suit on stage (production). The person doesn't change — only the outfit. The `FLASK_ENV` variable is the calendar entry that tells the app which occasion it's walking into, so it knows which wardrobe to open.

---

## 1. Overview & Metaphor

### Why environments exist

A real Flask app needs different behaviour in different contexts:

- **Development:** Debug mode on, SQLite database, auto-reload, no rate limiting, verbose logs.
- **Test:** In-memory database, deterministic secrets, rate limiting off, mail backend = `locmem`.
- **Staging:** Production-equivalent config, but with non-sensitive data and a staging Sentry DSN.
- **Production:** Debug off, Postgres with a real pool, rate limiting on, real Sentry DSN, secrets from a secret manager.

Hard-coding any one of these into the app code makes the other three impossible. The Twelve-Factor App methodology (see <https://12factor.net/config>) prescribes: *the same code, different config, selected by environment variables.* Flask-Environments is the Flask idiom for putting that prescription into practice.

### The three patterns

| Pattern | Mechanism | Strengths | Weaknesses |
|---|---|---|---|
| **Plain Flask `from_object`** | `app.config.from_object(f"app.config.{env.title()}Config")` | No dependencies; the simplest thing that works | No validation, no env auto-detection |
| **`Flask-Environments` package** | `env.from_object("config")` picks subclass by `FLASK_ENV` | Auto-detection, inheritance helper, CLI integration | Adds a dependency for modest gains |
| **`Pydantic-Settings` + class hierarchy** | `DevSettings`, `ProdSettings`, `TestSettings` subclasses of `BaseSettings` | Full type safety + environment hierarchy | Requires Pydantic v2 — see [[Pydantic-Settings]] |

The third pattern is what we recommend for new projects. The first is fine for tiny apps. The second is a middle ground that some legacy codebases still use.

### Config selection flow

```mermaid
flowchart TD
    A[App boot] --> B[Read FLASK_ENV<br/>or APP_ENVIRONMENT]
    B --> C{env value?}
    C -- dev --> D[DevConfig]
    C -- staging --> E[StagingConfig]
    C -- prod --> F[ProdConfig]
    C -- test --> G[TestConfig]
    C -- missing --> H[Default: DevConfig<br/>with warning]
    D --> I[app.config.from_object]
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J[Optionally overlay<br/>secrets from env vars<br/>or secret manager]
    J --> K[App ready]
```

---

## 2. Installation & Setup

```bash
pip install Flask-Environments     # the package
# OR (recommended for new projects):
pip install pydantic-settings       # typed config — see [[Pydantic-Settings]]
pip install python-dotenv           # .env file support (already a Flask dependency)
```

### The plain-Flask approach (no extra package)

```python
# app/config.py
import os

class BaseConfig:
    """Defaults shared by every environment."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://flask:flask@localhost:5432/flaskdev"
    )
    CACHE_TYPE = "SimpleCache"
    MAIL_SUPPRESS_SEND = True
    RATELIMIT_ENABLED = False

class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )
    SECRET_KEY = "test-only-not-secret"
    CACHE_TYPE = "NullCache"
    MAIL_SUPPRESS_SEND = True
    RATELIMIT_ENABLED = False
    WTF_CSRF_ENABLED = False

class ProdConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]  # required
    SECRET_KEY = os.environ["SECRET_KEY"]                 # required
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.environ["REDIS_URL"]
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = os.environ["REDIS_URL"]
    SENTRY_DSN = os.environ["SENTRY_DSN"]
```

```python
# app/__init__.py
import os
from flask import Flask

def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.environ.get("FLASK_ENV", "dev")
    app = Flask(__name__)
    app.config.from_object(f"app.config.{config_name.title()}Config")
    return app
```

That's the entire pattern. Set `FLASK_ENV=prod` in your environment, and `ProdConfig` is loaded. No magic, no dependencies, no surprises.

> [!note] `FLASK_ENV` is deprecated in Flask 2.3+
> Flask's built-in `FLASK_ENV` variable (which used to flip `DEBUG` automatically) was deprecated in Flask 2.3 and removed in 3.0. The pattern above uses `FLASK_ENV` as a *convention* for selecting your own config class — that still works, because you're reading the variable yourself, not relying on Flask's behaviour. To avoid confusion, many projects use `APP_ENVIRONMENT` instead.

---

## 3. Config Inheritance

The `DevConfig(BaseConfig)` line is where the power is. Inheritance gives you:

1. **A single source of truth for shared defaults.** Change `SQLALCHEMY_TRACK_MODIFICATIONS = False` in one place, every environment picks it up.
2. **Explicit per-environment overrides.** `ProdConfig` says "DEBUG = False" out loud, even though that's the default — it makes the prod intent visible to anyone reading the file.
3. **A clear place to add environment-specific validators.** `ProdConfig` can have a `validate()` classmethod that asserts required env vars are present (though `Pydantic-Settings` does this better — see §6).

### Inheritance hierarchy

```mermaid
classDiagram
    class BaseConfig {
        <<abstract>>
        +SECRET_KEY
        +SQLALCHEMY_TRACK_MODIFICATIONS
        +JSON_SORT_KEYS
    }
    class DevConfig {
        +DEBUG = True
        +CACHE_TYPE = SimpleCache
        +RATELIMIT_ENABLED = False
    }
    class TestConfig {
        +TESTING = True
        +SQLALCHEMY_DATABASE_URI = sqlite:///:memory:
        +WTF_CSRF_ENABLED = False
    }
    class StagingConfig {
        +DEBUG = False
        +CACHE_TYPE = RedisCache
        +SENTRY_ENV = staging
    }
    class ProdConfig {
        +DEBUG = False
        +RATELIMIT_ENABLED = True
        +SENTRY_ENV = production
    }
    BaseConfig <|-- DevConfig
    BaseConfig <|-- TestConfig
    BaseConfig <|-- StagingConfig
    StagingConfig <|-- ProdConfig
```

Note the `StagingConfig <|-- ProdConfig` arrow: staging is "production-lite" — same database type, same caching, but with a staging Sentry DSN and no rate limiting. Production extends staging and tightens the knobs. This is the **environment pyramid**: each layer adds constraints, never relaxes them.

### Inheritance direction matters

> [!warning] Don't make `ProdConfig` the base
> A common anti-pattern is `class DevConfig(ProdConfig)` with overrides that relax prod constraints. This is backwards — it means a missing override in `DevConfig` accidentally leaves a prod constraint active in dev. Always inherit from `BaseConfig` (or from a more-permissive environment) *towards* more-constrained environments.

---

## 4. The `Flask-Environments` Package

If you want a little more sugar — auto-detection, a `flask env` CLI command, declarative YAML config — the `Flask-Environments` package adds it.

```python
# app/__init__.py
from flask import Flask
from flask_environments import Environment

def create_app() -> Flask:
    app = Flask(__name__)
    env = Environment(app)
    env.from_object("app.config")
    # Auto-selects app.config.<FLASK_ENV>Config, with DevConfig as default.
    return app
```

### YAML alternative

```yaml
# config.yml
default:
  SQLALCHEMY_TRACK_MODIFICATIONS: false
  JSON_SORT_KEYS: false

development:
  DEBUG: true
  SQLALCHEMY_DATABASE_URI: postgresql://flask:flask@localhost:5432/flaskdev

production:
  DEBUG: false
  SQLALCHEMY_DATABASE_URI: "{{ DATABASE_URL }}"
  SENTRY_DSN: "{{ SENTRY_DSN }}"
```

```python
env.from_yaml("config.yml")  # uses FLASK_ENV to pick the section
```

`{{ VAR }}` placeholders are interpolated from `os.environ` — useful for keeping structure in YAML while pulling actual values from environment variables. The same pattern is what `dynaconf` (§7 below) implements more fully.

### CLI helper

```bash
$ flask env
Current environment: development
Config class: app.config.DevConfig
DEBUG: True
SQLALCHEMY_DATABASE_URI: postgresql://flask:flask@localhost:5432/flaskdev
```

This is invaluable when debugging "why is my app behaving like that in this environment?" — the operator can see exactly which config object is loaded and what its values are, without poking at the shell.

---

## 5. Environment-Aware App Factory

The full pattern, integrating everything from this vault:

```python
# app/__init__.py
import os
from flask import Flask

from .config import DevSettings, ProdSettings, TestSettings, StagingSettings

SETTINGS_REGISTRY = {
    "dev":     DevSettings,
    "test":    TestSettings,
    "staging": StagingSettings,
    "prod":    ProdSettings,
}

def create_app(env: str | None = None) -> Flask:
    env = (env or os.environ.get("APP_ENVIRONMENT") or "dev").lower()
    if env not in SETTINGS_REGISTRY:
        raise ValueError(
            f"Unknown APP_ENVIRONMENT={env!r}. "
            f"Expected one of: {sorted(SETTINGS_REGISTRY)}"
        )

    settings = SETTINGS_REGISTRY[env]()   # raises ValidationError if misconfigured
    app = Flask(__name__)
    app.config["APP_ENVIRONMENT"] = env
    app.config.update(_flatten_settings(settings))
    app.settings = settings

    # Wire extensions
    from .extensions import db, migrate, cache, mail, limiter, login
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    login.init_app(app)

    # Register blueprints
    from .routes import bp as api_bp
    app.register_blueprint(api_bp)

    # Bind settings into Flask-Injector
    from flask_injector import FlaskInjector
    from injector import Binder, singleton

    def bind_settings(binder: Binder):
        binder.bind(type(settings), to=settings, scope=singleton)

    FlaskInjector(app=app, modules=[bind_settings])
    return app


def _flatten_settings(settings):
    """Copy settings into app.config for extensions that read it."""
    dump = settings.model_dump()
    flat = {}
    for k, v in dump.items():
        if hasattr(v, "get_secret_value"):
            flat[k.upper()] = v.get_secret_value()
        else:
            flat[k.upper()] = v
    return flat
```

### Boot-time validation

```python
if __name__ == "__main__":
    # Local dev: just run
    create_app().run(debug=True)
else:
    # WSGI server: validate eagerly
    app = create_app()
    # At this point, if config was bad, Settings() already raised.
```

Because `Settings()` raises `ValidationError` on bad config, the WSGI process refuses to start. Container orchestrators (Kubernetes, ECS, Nomad) see the crash-loop and surface it in their dashboards — the operator gets a clear "your env vars are wrong" error, not a slow drift of broken requests.

---

## 6. Environment Hierarchy & Promotion

Most teams follow a **promotion path**: `dev → staging → prod`. Each environment should be a strict superset of the previous one's constraints. The diagram below shows the relationship:

```mermaid
flowchart LR
    Dev[DevConfig<br/>DEBUG=true<br/>SQLite allowed<br/>No rate limit] --> Staging[StagingConfig<br/>DEBUG=false<br/>Postgres required<br/>Sentry on]
    Staging --> Prod[ProdConfig<br/>DEBUG=false<br/>Rate limit on<br/>Secret manager required]
    Test[TestConfig<br/>TESTING=true<br/>In-memory DB<br/>CSRF off] -.parallel.-> Dev
    style Prod fill:#fee,stroke:#c00,stroke-width:2px
    style Staging fill:#fed,stroke:#a70
    style Dev fill:#dfd,stroke:#070
    style Test fill:#ddf,stroke:#007
```

### Promotion rules of thumb

| Rule | Why |
|---|---|
| **Prod never inherits from Dev** | A prod config that's a subclass of dev can accidentally inherit a relaxed constraint when dev is updated. |
| **Every constraint added in staging must also hold in prod** | Otherwise staging doesn't actually validate prod behaviour. |
| **Test config is a sibling, not a child, of Dev** | Tests need different invariants (in-memory DB, CSRF off) that should never leak into dev. |
| **Secret defaults are only valid in Dev and Test** | `SECRET_KEY = "dev-only"` is fine in `DevConfig`; `ProdConfig` must read from env with no default. |
| **Validators tighten as you move up** | `ProdConfig` may assert `len(SECRET_KEY) >= 32`; `DevConfig` does not. |

### `environment_is_at_least` helper

```python
ENV_ORDER = {"dev": 0, "test": 0, "staging": 1, "prod": 2}

def environment_is_at_least(env: str, threshold: str) -> bool:
    return ENV_ORDER[env] >= ENV_ORDER[threshold]

# Usage:
if environment_is_at_least(app.config["APP_ENVIRONMENT"], "staging"):
    # Enable stricter checks only in staging/prod
    ...
```

This is the kind of small helper that, once present, gets used everywhere — and makes the intent of conditional code crystal-clear in review.

---

## 7. Comparison: python-dotenv, dynaconf, Flask-Environments

| Feature | Plain `app.config.from_object` | **Flask-Environments** | `python-dotenv` | `dynaconf` |
|---|---|---|---|---|
| **Per-env config objects** | Manual | Auto from `FLASK_ENV` | None (env vars only) | Auto, with `env` sections |
| **YAML config** | No | Yes | No | Yes (`settings.toml`, `.yaml`, `.json`) |
| **Env var overlay** | Manual `os.environ.get` | `{{ VAR }}` template | Yes — that's its only job | Yes, layered |
| **Secret management** | Manual | Manual | None | `@format` + Vault integration |
| **Type validation** | None | None | None | Optional (via `validator`) |
| **Hot reload** | No | No | No | Yes (`dynaconf.reload`) |
| **Footprint** | Zero | Small | Tiny | Large |
| **Best for** | Simple Flask apps | Mid-size Flask apps | Loading `.env` files | Multi-language, multi-source config |

### Recommendation matrix

- **Tiny app, single developer:** Plain `app.config.from_object` + `python-dotenv` for `.env` files. No reason to add a dependency.
- **Mid-size Flask app, multiple environments:** Either Flask-Environments (YAML-friendly teams) or Pydantic-Settings (type-safety-first teams) — see [[Pydantic-Settings]].
- **Large org, multiple services in multiple languages:** `dynaconf`. It supports the same `settings.toml` across Python, JavaScript, and Go services, with environment overlays and secret-manager integration.
- **Any size, strict type-safety requirement:** Pydantic-Settings + the class-hierarchy pattern from §6 of [[Pydantic-Settings]]. This is the future-proof choice.

### Example: dynaconf for a polyglot shop

```toml
# settings.toml
[default]
SQLALCHEMY_TRACK_MODIFICATIONS = false
LOG_LEVEL = "INFO"

[development]
DEBUG = true
SQLALCHEMY_DATABASE_URI = "postgresql://flask:flask@localhost:5432/flaskdev"

[production]
DEBUG = false
SQLALCHEMY_DATABASE_URI = "@env DATABASE_URL"
SECRET_KEY = "@env SECRET_KEY"
SENTRY_DSN = "@env SENTRY_DSN"
```

```python
from dynaconf import FlaskDynaconf
app = Flask(__name__)
FlaskDynaconf(app)   # reads settings.toml, picks [development] or [production]
# app.config.SQLALCHEMY_DATABASE_URI etc.
```

`@env DATABASE_URL` is dynaconf's syntax for "pull this value from the environment variable of the same name" — explicit, auditable, no silent fallback.

---

## 8. Per-Environment `.env` Files

A pattern that scales well: one `.env` per environment, loaded conditionally.

```python
# app/__init__.py
from dotenv import load_dotenv
import os

def create_app():
    env = os.environ.get("APP_ENVIRONMENT", "dev")
    load_dotenv(f".env.{env}", override=False)   # environment-specific
    load_dotenv(f".env", override=False)          # shared defaults
    # Now instantiate settings — env vars are populated.
    ...
```

```
.env                 # shared defaults, committed
.env.dev             # developer overrides, git-ignored
.env.staging         # staging secrets, provisioned by CI
.env.prod            # prod secrets, provisioned by deploy pipeline
.env.example         # documentation, committed
```

### Layered loading priority

```mermaid
flowchart TD
    A[Container env vars<br/>set by orchestrator] --> B[load_dotenv .env.prod<br/>override=False]
    B --> C[load_dotenv .env<br/>override=False]
    C --> D[Settings reads<br/>os.environ]
    D --> E[Typed, validated<br/>Settings instance]
    style A fill:#fee,stroke:#c00
    style E fill:#dfd,stroke:#070
```

`override=False` means *don't replace* values already in `os.environ` — so the orchestrator's secrets (set via Kubernetes Secrets, for example) take priority over anything in the `.env` file. This is the correct priority: runtime-injected secrets should win over files baked into the image.

---

## 9. Testing Across Environments

A common test pattern is "this behaviour is correct in dev, different in prod":

```python
# tests/test_config.py
import pytest
from myapp import create_app
from myapp.config import DevSettings, ProdSettings

def test_dev_allows_sqlite():
    settings = DevSettings(database_url="sqlite:///dev.db")
    assert settings.debug is True

def test_prod_rejects_sqlite():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ProdSettings(
            database_url="sqlite:///prod.db",   # PostgresDsn validator rejects this
            secret_key="x" * 32,
            sentry_dsn="https://example.com",
        )

def test_prod_requires_sentry():
    from pydantic import ValidationError
    with pytest.raises(ValidationError, match="SENTRY_DSN"):
        ProdSettings(
            database_url="postgresql://u:p@h:5432/db",
            secret_key="x" * 32,
            sentry_dsn=None,
        )
```

These tests are **configuration contracts**: they document and enforce what each environment guarantees. Run them in CI on every PR; a config-relaxing change to `ProdConfig` will fail the test and force a conversation.

> [!example] The "config contract" test pattern
> Treat your config classes like public APIs. Every invariant — "prod never has DEBUG=true", "test never has CSRF enabled", "staging always has SENTRY_DSN" — should have a test. These tests are the cheapest possible way to prevent config regressions, because they run in milliseconds and require no infrastructure.

---

## 10. Common Pitfalls & Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| App runs in prod with `DEBUG=True` | `FLASK_ENV` not set, defaulted to dev | Set `APP_ENVIRONMENT=prod` in the orchestrator; fail-fast if missing in prod deploy |
| `KeyError: 'DATABASE_URL'` at boot | `ProdConfig` reads `os.environ["DATABASE_URL"]` (no default) — by design | Set the env var. The error is the feature. |
| Config changes don't take effect | Flask caches `app.config` after `from_object` | Restart the process. (Hot-reload of config is rarely worth the complexity.) |
| Tests use prod config | `create_app()` called without arg in test, picks up `APP_ENVIRONMENT=prod` from CI env | Pass `create_app("test")` explicitly in test fixtures |
| `DevConfig` accidentally has `DEBUG=False` | Forgot to override after inheriting from `BaseConfig` where `DEBUG=False` is the default | Either set `DEBUG=True` explicitly in `DevConfig`, or omit `DEBUG` from `BaseConfig` entirely |
| Secret visible in logs | `app.config` was logged at startup | Don't log `app.config`. Log only `app.config["APP_ENVIRONMENT"]` and non-secret keys. |
| `.env.prod` committed to git | Misconfigured `.gitignore` | Add `.env.*` to `.gitignore`, only allow `.env.example` |
| `from_object("app.config.DevConfig")` raises `ImportError` | Typo in env var, or config class name doesn't match `FLASK_ENV.title() + "Config"` | Validate env value against a whitelist before `from_object` |

> [!danger] The silent-fallback trap
> ```python
> SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
> ```
> This is the most dangerous line in legacy Flask code. In dev it works. In prod, if `SECRET_KEY` isn't set, the app *runs* with `"dev-only-change-me"` as its secret key — every session token is forgeable. Always require secrets explicitly in prod:
> ```python
> SECRET_KEY = os.environ["SECRET_KEY"]   # KeyError at boot if missing
> ```
> Or, with Pydantic-Settings, just declare `secret_key: SecretStr` with no default — the app refuses to start without it.

---

## 11. Best Practices Checklist

> [!success] Environment-config hygiene
> - [ ] One config class per environment, all inheriting from a shared `BaseConfig`.
> - [ ] `BaseConfig` contains only truly shared defaults; nothing environment-specific.
> - [ ] `ProdConfig` has no fallback defaults for secrets — missing env var → boot failure.
> - [ ] `APP_ENVIRONMENT` is validated against a whitelist; unknown values fail fast.
> - [ ] `.env` files are layered: shared `.env` first, then `.env.<env>`, with `override=False`.
> - [ ] `.env.example` is committed and documents every variable the app understands.
> - [ ] `.env.*` (except `.env.example`) is in `.gitignore`.
> - [ ] Config contracts are tested: every environment invariant has a pytest case.
> - [ ] `app.config` is never logged verbatim — secrets live there.
> - [ ] Promotion path is documented: `dev → staging → prod`, with each layer adding constraints.
> - [ ] The same code runs in all environments; only `APP_ENVIRONMENT` and env vars differ.

---

## 12. Further Reading & Cross-References

- **The Twelve-Factor App, §III Config:** <https://12factor.net/config> — the foundational text on environment-based config.
- **Flask config docs:** <https://flask.palletsprojects.com/en/latest/config/> — the built-in `app.config` API.
- **Flask-Environments package:** <https://github.com/briancappello/flask-environments> — the small extension that adds auto-detection.
- **dynaconf:** <https://www.dynaconf.com/> — when you outgrow plain Python config objects.
- **Related notes in this vault:**
  - [[Pydantic-Settings]] — the typed, validated partner to environment classes.
  - [[Flask-Injector]] — inject the selected `Settings` into your services.
  - [[Flask-SQLAlchemy]] — `SQLALCHEMY_DATABASE_URI` differs per environment.
  - [[Flask-Caching]] — `CACHE_TYPE` differs per environment (`SimpleCache` in dev, `RedisCache` in prod).
  - [[Flask-FeatureFlags]] — flag defaults are often environment-specific.

> [!quote] The Twelve-Factor App
> "Apps sometimes use config files that do not get checked into version control, such as `config/database.yml` in Rails. This is an improvement over using constants which are checked into the code repo, but still has weaknesses: it's easy to mistakenly check in a config file to the repo; there tends to be a proliferation of config files… The twelve-factor app stores config in environment variables."
>
> Flask-Environments is the Flask idiom that lives this principle: one config class per environment, selected by an env var, with secrets pulled from the environment at boot.
