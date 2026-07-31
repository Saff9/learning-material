---
title: Pydantic-Settings
tags:
  - flask
  - pydantic
  - pydantic-v2
  - configuration
  - typed-config
  - env-vars
  - secrets
  - validation
aliases:
  - pydantic-settings
  - basesettings
  - typed-config
  - pydantic-config
related:
  - "[[Flask-Environments]]"
  - "[[Flask-Injector]]"
  - "[[Flask-SQLAlchemy]]"
  - "[[Flask-Caching]]"
  - "[[Flask-FeatureFlags]]"
created: 2024-01-15
updated: 2024-01-15
---

# Pydantic-Settings

#flask #pydantic #pydantic-v2 #configuration #typed-config #env-vars #secrets #validation

> [!info] Type-safe configuration for Flask with Pydantic v2
> **Pydantic-Settings** (the `pydantic-settings` package, the successor to `pydantic.BaseSettings` from v1) brings Pydantic v2's validation engine to application configuration. Instead of mutating `app.config["DATABASE_URL"] = os.environ["DATABASE_URL"]` and discovering at runtime that you mistyped the env var name, you declare a typed `Settings` class and get: validation, default values, `.env` file loading, secret managers, nested config, and IDE auto-complete — all in one place.
>
> Pair this with [[Flask-Environments]] (which selects the right settings class per environment) and [[Flask-Injector]] (which injects the resulting `Settings` instance into your services), and you have a configuration story that rivals anything in the typed-config ecosystem.

Think of Pydantic-Settings as a **bouncer at the door of your application**. Every configuration value — database URL, Stripe key, sentry DSN, log level — has to walk past the bouncer before it gets in. The bouncer checks three things: (1) is the value the right *type* (a URL, an int, an enum)? (2) does it pass *custom rules* (is the port > 1024? is the URL reachable?)? (3) is it *authorised* to be here at all (does this secret actually belong to this environment)? If any check fails, the bouncer throws the value out — and your app refuses to start rather than running with a broken config.

---

## 1. Overview & Metaphor

### Why typed config?

Flask's built-in `app.config` is a `dict` subclass. That gives you exactly two affordances:

1. `app.config["KEY"]` — read a value.
2. `app.config.from_object(...)` — load values from a Python module's attributes.

What it does *not* give you:

- **Type checking.** `app.config["PORT"]` could be `"5432"` (string) or `5432` (int) depending on how it was set. Bugs from this are subtle and only surface at runtime.
- **Validation.** `app.config["REDIS_URL"]` could be `not-a-url` and Flask will happily accept it. You discover the typo when your first request tries to connect.
- **Defaults.** You write `app.config.setdefault("LOG_LEVEL", "INFO")` everywhere, or you remember to set defaults in your config object — but nothing enforces it.
- **Documentation.** The set of valid config keys lives only in your head and in scattered `app.config["..."]` reads. No grep will show you the full schema.
- **Secret management.** Secrets live alongside non-secret config, with no separation of concerns and no integration with secret managers.

Pydantic-Settings fixes all five. The schema *is* the documentation; the schema *is* the validator; the schema *is* the source of defaults.

### The five primitives

| Primitive | Purpose | Example |
|---|---|---|
| **`BaseSettings`** | Subclass this; each class attribute is a config field. | `class Settings(BaseSettings): ...` |
| **`SettingsConfigDict`** | Tuning: env prefix, nested delimiter, case sensitivity, `.env` file. | `model_config = SettingsConfigDict(env_prefix="APP_")` |
| **Field types** | Anything Pydantic v2 supports: `int`, `HttpUrl`, `PostgresDsn`, `SecretStr`, `Enum`, custom. | `database_url: PostgresDsn` |
| **Validators** | `@field_validator` and `@model_validator` for custom rules. | `@field_validator("port")` |
| **Custom sources** | Subclass `PydanticBaseSettingsSource` to read from AWS Secrets Manager, Vault, etc. | `customise_sources(...)` |

### Config loading flow

```mermaid
flowchart TD
    A[App startup] --> B[Instantiate Settings]
    B --> C[Customise sources:<br/>1. init args<br/>2. env vars<br/>3. .env file<br/>4. secrets manager]
    C --> D[For each field:<br/>resolve from sources<br/>in priority order]
    D --> E[Type-coerce<br/>via Pydantic]
    E --> F[Run field validators]
    F --> G[Run model validator]
    G --> H{All pass?}
    H -- yes --> I[Settings instance<br/>frozen, hashable]
    H -- no --> J[Raise ValidationError<br/>app refuses to start]
    I --> K[Bind into Flask app.config<br/>or Flask-Injector]
```

The "app refuses to start" property is the killer feature. A misconfigured production deploy fails loudly at boot, in your orchestrator's logs — not silently in the middle of the night when a user hits the broken endpoint.

---

## 2. Installation & Setup

```bash
pip install pydantic pydantic-settings
# Optional companions:
pip install python-dotenv      # .env file parsing (already a dependency)
pip install pydantic[email]    # email validation
pip install Flask-Injector     # to inject Settings into services — see [[Flask-Injector]]
```

> [!note] Pydantic v1 vs v2 vs `pydantic-settings`
> In Pydantic v1, `BaseSettings` lived in `pydantic` itself. In v2 it was extracted to a separate `pydantic-settings` package — same idea, separate release cadence. The imports below assume v2 + `pydantic-settings>=2.0`.

### Minimal integration with Flask

```python
# app/config.py
from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",            # APP_DATABASE_URL, APP_SECRET_KEY, etc.
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid",               # reject unknown env vars
    )

    # Required — no default, app will not start without them.
    database_url: PostgresDsn
    secret_key: SecretStr = Field(min_length=32)

    # Optional with defaults.
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    sentry_dsn: str | None = None    # None = Sentry disabled
    max_upload_mb: int = 10
    enable_swagger: bool = True
```

```python
# app/__init__.py
from flask import Flask
from .config import Settings

def create_app() -> Flask:
    settings = Settings()    # raises ValidationError if config is bad
    app = Flask(__name__)

    # Optional: copy settings into app.config for libraries that read it.
    app.config.update(settings.model_dump())

    # Recommended: stash the typed Settings for injection later.
    app.settings = settings

    return app
```

> [!tip] Don't fully replace `app.config`
> Many Flask extensions (Flask-SQLAlchemy, Flask-Mail, Flask-Caching) read from `app.config` by convention. Don't fight this — let Pydantic-Settings be the *source of truth* and copy into `app.config` with `app.config.update(settings.model_dump())`. Extensions keep working; your code reads from the typed `app.settings` object. Best of both worlds.
>
> One caveat: `SecretStr` dumps to `"**********"` by default. For secrets that need to land in `app.config`, use `SecretStr` for storage but `app.config["SECRET_KEY"] = settings.secret_key.get_secret_value()` explicitly.

---

## 3. Core Concepts

### Field types matter

The type annotation is not just documentation — it determines how the env var string is coerced:

```python
class Settings(BaseSettings):
    port: int                    # "5432" -> 5432
    debug: bool                  # "true", "1", "yes" -> True
    allowed_origins: list[str]   # "a.com,b.com" -> ["a.com", "b.com"]
    feature_flags: dict[str, bool]  # 'X=true,Y=false' -> {"X": True, "Y": False}
    database_url: PostgresDsn    # validated as a real Postgres URL
    cache_ttl: timedelta         # "5m" -> timedelta(minutes=5)
```

Pydantic v2 ships validators for ~40 built-in types including `HttpUrl`, `EmailStr`, `IPvAnyAddress`, `UUID4`, and timedelta-with-units (`"30s"`, `"1h"`). For anything more specialised, write a custom type:

```python
from pydantic import BaseModel, RootModel

class LogLevel(RootModel):
    root: str
    @field_validator("root")
    def check(cls, v):
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"log level must be one of {allowed}")
        return v.upper()

class Settings(BaseSettings):
    log_level: LogLevel = LogLevel("INFO")
```

### `SettingsConfigDict` — the knobs

| Setting | What it does | Example |
|---|---|---|
| `env_prefix` | Prefix stripped from env var names | `env_prefix="APP_"` → `APP_PORT` sets `port` |
| `env_nested_delimiter` | Parses `APP_DB__HOST` into `settings.db.host` | `env_nested_delimiter="__"` |
| `env_file` | Path(s) to `.env` file(s) | `env_file=(".env", ".env.prod")` |
| `env_file_encoding` | Encoding of `.env` file | `"utf-8"` (default) |
| `case_sensitive` | Whether env var names are case-sensitive | `False` (default) — recommended |
| `extra` | `"forbid"` rejects unknown fields; `"ignore"` silently drops them | `"forbid"` for prod safety |
| `secrets_dir` | Directory of files whose names are field names (Docker secrets pattern) | `"/run/secrets"` |

### Nested config

```python
class DatabaseSettings(BaseModel):
    url: PostgresDsn
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False

class RedisSettings(BaseModel):
    url: str = "redis://localhost:6379/0"
    socket_timeout: float = 0.5

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",
        env_file=".env",
    )

    database: DatabaseSettings
    redis: RedisSettings = RedisSettings()
    secret_key: SecretStr
```

Env vars become:

```
APP_DATABASE__URL=postgresql://user:pass@db:5432/app
APP_DATABASE__POOL_SIZE=20
APP_REDIS__URL=redis://cache:6379/0
APP_SECRET_KEY=...
```

The double underscore is the *only* delimiter that works reliably across shells; `.` collides with extensions like `BASH_SUBSHELL`.

---

## 4. Validation: Field & Model Validators

### Field validators

```python
from pydantic import field_validator

class Settings(BaseSettings):
    port: int = 8000
    workers: int = 4

    @field_validator("port")
    @classmethod
    def port_in_ephemeral_range(cls, v: int) -> int:
        if not (1024 <= v <= 65535):
            raise ValueError("port must be between 1024 and 65535")
        return v

    @field_validator("workers")
    @classmethod
    def workers_match_cpu(cls, v: int) -> int:
        import os
        cpu = os.cpu_count() or 1
        if v > cpu * 2:
            raise ValueError(f"workers={v} too high for {cpu} CPUs")
        return v
```

### Model validators — cross-field rules

```python
from pydantic import model_validator

class Settings(BaseSettings):
    environment: str = "dev"
    debug: bool = True
    sentry_dsn: str | None = None

    @model_validator(mode="after")
    def prod_must_have_sentry(self) -> "Settings":
        if self.environment == "prod" and not self.sentry_dsn:
            raise ValueError("prod environment requires SENTRY_DSN")
        if self.environment != "prod" and self.debug is False:
            # dev/test should usually have debug on
            pass
        return self
```

`mode="after"` runs after all fields are parsed, so you can read any field. `mode="before"` runs on the raw input dict and is useful for renaming keys or transforming values before type coercion.

### Validation pipeline

```mermaid
flowchart LR
    E[Env vars] --> P[Parse JSON/CSV<br/>for complex types]
    P --> BC[Before-model<br/>validators]
    BC --> TC[Type coercion<br/>via Pydantic]
    TC --> FV[Field validators<br/>per field]
    FV --> AV[After-model<br/>validator]
    AV --> FF{All pass?}
    FF -- yes --> I[Settings instance]
    FF -- no --> X[ValidationError<br/>with all errors aggregated]
```

A critical property of Pydantic v2: **all errors are collected and reported together**. If you have three bad fields, you get three errors in one exception, not three sequential failures. This makes debugging misconfigurations dramatically faster.

```python
try:
    settings = Settings()
except ValidationError as e:
    # e.errors() returns a list of all validation failures
    for err in e.errors():
        print(f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}")
    raise SystemExit(1)
```

---

## 5. `.env` File Loading

### Priority order

Pydantic-Settings merges sources in this priority (highest first):

1. **Init kwargs** — `Settings(database_url="...")`
2. **Environment variables** — actual `os.environ`
3. **`.env` file** — only for variables not already in `os.environ`
4. **Secrets directory** — `/run/secrets/<field_name>`
5. **Default** — the value declared in the class

### Multiple `.env` files

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local", ".env.prod"),
        env_file_encoding="utf-8",
    )
```

Later files override earlier ones. A common pattern:
- `.env` — committed to git, contains non-secret defaults like `APP_LOG_LEVEL=INFO`.
- `.env.local` — git-ignored, contains developer-specific overrides.
- `.env.prod` — provisioned by the deploy pipeline at container start, contains production secrets.

> [!warning] Never commit `.env` files containing real secrets
> Add `.env.local`, `.env.prod`, and any file matching `.env.*` (except `.env.example`) to `.gitignore`. The number of production-incident post-mortems that begin with "a developer accidentally committed the AWS keys to `.env`" is enormous.

### Example `.env` file

```bash
# .env.example — committed to the repo as documentation
APP_ENVIRONMENT=dev
APP_DEBUG=true
APP_LOG_LEVEL=DEBUG

APP_DATABASE__URL=postgresql://flask:flask@localhost:5432/flaskdev
APP_DATABASE__POOL_SIZE=5
APP_DATABASE__ECHO=true

APP_REDIS__URL=redis://localhost:6379/0

APP_SECRET_KEY=change-me-in-production-min-32-chars-long-please

APP_SENTRY_DSN=
APP_MAX_UPLOAD_MB=10
APP_ENABLE_SWAGGER=true
```

Developers copy this to `.env` and customise; the `extra="forbid"` setting means any typo (`APP_DATABSE__URL=...`) is caught at boot.

---

## 6. Secrets Management

### `SecretStr` — the safe string

```python
class Settings(BaseSettings):
    secret_key: SecretStr
    stripe_secret: SecretStr

settings = Settings(secret_key="abc", stripe_secret="sk_live_xxx")
print(settings.secret_key)          # SecretStr('**********')
print(repr(settings.secret_key))    # SecretStr('**********')
print(settings.secret_key.get_secret_value())  # 'abc' — explicit opt-in
```

`SecretStr` prevents secrets from accidentally appearing in logs, error messages, or `repr()` dumps. To use the actual value you must call `.get_secret_value()`, which makes accidental leakage visible in code review.

### Docker / Kubernetes secrets pattern

Mount secrets as files in `/run/secrets/`:

```yaml
# docker-compose.yml
services:
  web:
    image: myapp:latest
    secrets:
      - secret_key
      - stripe_secret
    environment:
      - APP_ENVIRONMENT=prod

secrets:
  secret_key:
    file: ./secrets/secret_key.txt
  stripe_secret:
    file: ./secrets/stripe_secret.txt
```

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        secrets_dir="/run/secrets",
    )
    secret_key: SecretStr
    stripe_secret: SecretStr
```

Pydantic-Settings reads `/run/secrets/secret_key` (filename = field name) and populates the field. This pattern is the standard for Swarm/Kubernetes deployments.

### Custom source: AWS Secrets Manager

```python
# app/sources.py
import json
import boto3
from pydantic_settings import PydanticBaseSettingsSource
from pydantic_settings.sources import EnvSettingsSource

class AWSSecretsManagerSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls, secret_id: str, region: str = "us-east-1"):
        super().__init__(settings_cls)
        self.client = boto3.client("secretsmanager", region_name=region)
        self.secret_id = secret_id
        self._cache: dict[str, str] | None = None

    def _load(self) -> dict[str, str]:
        if self._cache is None:
            resp = self.client.get_secret_value(SecretId=self.secret_id)
            self._cache = json.loads(resp["SecretString"])
        return self._cache

    def get_field_value(self, field, field_name):
        if field_name in self._load():
            return self._load()[field_name], field_name, False
        return None, field_name, False

    def __call__(self):
        d = {}
        for field_name in self.settings_cls.model_fields:
            v, _, _ = self.get_field_value(None, field_name)
            if v is not None:
                d[field_name] = v
        return d
```

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import PydanticBaseSettingsSource

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        # Order = priority. Later sources only fill gaps.
        return (
            init_settings,                         # 1. explicit kwargs
            env_settings,                          # 2. os.environ
            dotenv_settings,                       # 3. .env file
            AWSSecretsManagerSource(               # 4. AWS Secrets Manager
                settings_cls,
                secret_id="myapp/prod",
            ),
            file_secret_settings,                  # 5. /run/secrets dir
        )
```

The same pattern works for HashiCorp Vault, GCP Secret Manager, Azure Key Vault — anything with a Python client.

### Source resolution hierarchy

```mermaid
flowchart TB
    subgraph "Priority (highest → lowest)"
        S1[1. Init kwargs<br/>Settings database_url=...]
        S2[2. Environment variables<br/>os.environ]
        S3[3. .env file<br/>.env, .env.local]
        S4[4. Secret manager<br/>AWS / Vault / GCP]
        S5[5. File secrets<br/>/run/secrets/*]
        S6[6. Class default<br/>Field default=...]
    end
    S1 --> S2 --> S3 --> S4 --> S5 --> S6
    Note[First non-None wins.<br/>Later sources only fill gaps.] -.-> S1
    style S1 fill:#dfd,stroke:#070
    style S6 fill:#fdd,stroke:#700
```

The ordering encodes a critical principle: **runtime-supplied values beat build-time values**. If your CI pipeline bakes a `.env` into the image but the orchestrator injects a different value via `os.environ`, the orchestrator wins. This is what makes the same image safely deployable across staging and production — the image is identical, only the runtime environment differs.

---

## 7. Replacing Flask's Built-in Config

### Before (Flask's `app.config` only)

```python
# config.py
class ProdConfig:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-do-not-use-in-prod")
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    # ... 30 more lines of this

# __init__.py
app.config.from_object("config.ProdConfig")
```

Pain points:
- `SQLALCHEMY_DATABASE_URI` could be `""` or `not-a-url` and Flask accepts it.
- `SECRET_KEY` falls back to a dev value silently — a frequent source of security incidents.
- No IDE auto-complete on `app.config["SOMETHING"]`.
- `os.environ.get` returns `Optional[str]`, so every reader has to handle `None`.

### After (Pydantic-Settings)

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="forbid")

    debug: bool = False
    testing: bool = False
    database_url: PostgresDsn          # required, validated
    secret_key: SecretStr = Field(min_length=32)   # required, length-checked
    redis_url: str = "redis://localhost:6379/0"
```

| Concern | Before (`app.config`) | After (Pydantic-Settings) |
|---|---|---|
| **Type safety** | None | Full, validated at boot |
| **Defaults** | Manual `os.environ.get(..., default)` | `Field(default=...)` |
| **Required fields** | Implicit (silently `None` if missing) | Explicit — app won't start |
| **Secret handling** | Mixed with non-secrets | `SecretStr` + `secrets_dir` |
| **Documentation** | Scattered across codebase | Schema is the docs |
| **IDE auto-complete** | None on `app.config["..."]` | Full on `settings.database_url` |
| **Validation errors** | Discovered at runtime | Discovered at boot, all at once |
| **`.env` support** | Manual `python-dotenv` calls | Built-in |
| **Secret managers** | Custom code | `customise_sources` hook |

### Bridging the two worlds

```python
def create_app() -> Flask:
    settings = Settings()  # raises if invalid
    app = Flask(__name__)

    # 1. Let Flask extensions read from app.config as usual.
    app.config["SQLALCHEMY_DATABASE_URI"] = str(settings.database_url)
    app.config["SECRET_KEY"] = settings.secret_key.get_secret_value()
    app.config["REDIS_URL"] = settings.redis_url
    app.config["DEBUG"] = settings.debug

    # 2. Make the typed settings available app-wide.
    app.settings = settings

    # 3. Optionally bind into Flask-Injector for typed injection.
    from flask_injector import FlaskInjector
    from injector import Binder, singleton

    def bind_settings(binder: Binder):
        binder.bind(Settings, to=settings, scope=singleton)

    FlaskInjector(app=app, modules=[bind_settings])
    return app
```

Now any service can do:

```python
from injector import inject
from app.config import Settings

class PaymentService:
    @inject
    def __init__(self, settings: Settings):
        self.stripe_key = settings.stripe_secret.get_secret_value()
```

No more `current_app.config["STRIPE_KEY"]` reads scattered through the codebase. The single source of truth is the typed `Settings` instance — see [[Flask-Injector]] §6.

---

## 8. Environment-Specific Settings

Pydantic-Settings pairs naturally with the multi-config-class pattern from [[Flask-Environments]].

```python
# app/config.py
from abc import ABC

class BaseSettings_(BaseSettings, ABC):
    """Common base. Abstract: never instantiated directly."""
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="forbid")

    secret_key: SecretStr = Field(min_length=32)
    database_url: PostgresDsn
    redis_url: str
    log_level: str = "INFO"
    sentry_dsn: str | None = None

class DevSettings(BaseSettings_):
    debug: bool = True
    log_level: str = "DEBUG"
    enable_swagger: bool = True

class ProdSettings(BaseSettings_):
    debug: bool = False
    log_level: str = "INFO"
    enable_swagger: bool = False

    @model_validator(mode="after")
    def prod_requires_sentry(self) -> "ProdSettings":
        if not self.sentry_dsn:
            raise ValueError("prod requires APP_SENTRY_DSN")
        return self

class TestSettings(BaseSettings_):
    testing: bool = True
    database_url: PostgresDsn = "postgresql://test:test@localhost:5432/test"
    secret_key: SecretStr = "test-only-secret-key-32-chars-padding"
```

```python
# app/__init__.py
import os
from .config import DevSettings, ProdSettings, TestSettings

def create_app():
    env = os.environ.get("APP_ENVIRONMENT", "dev").lower()
    settings_cls = {
        "dev":  DevSettings,
        "prod": ProdSettings,
        "test": TestSettings,
    }[env]
    settings = settings_cls()
    ...
```

Because each subclass can add fields, override defaults, and add validators, you get a fully-typed environment hierarchy. The abstract base guarantees the common fields exist everywhere.

---

## 9. Testing with Pydantic-Settings

```python
# tests/conftest.py
import pytest
from myapp.config import TestSettings

@pytest.fixture
def settings():
    # TestSettings has safe defaults; override per-test as needed.
    return TestSettings(
        database_url="postgresql://test:test@localhost:5432/test",
        secret_key="x" * 32,
    )

@pytest.fixture
def app(settings):
    from myapp import create_app
    return create_app(settings=settings)
```

```python
# myapp/__init__.py — accept explicit settings for tests
def create_app(settings: Settings | None = None) -> Flask:
    if settings is None:
        settings = _load_settings_from_env()
    ...
```

> [!example] Why this matters for tests
> Tests can now pass `Settings(database_url="sqlite:///:memory:")` directly, with full validation. A typo in the test's database URL is caught at fixture setup, not three asserts later when the test mysteriously fails. The same validator that protects production protects tests.

---

## 10. Common Pitfalls & Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ValidationError: field required` for a var that IS set | `env_prefix="APP_"` but env var is `DATABASE_URL` (no prefix) | Either add prefix to env var, or remove `env_prefix` |
| Nested field not populated from env var | `env_nested_delimiter` not set, or wrong delimiter | Set `env_nested_delimiter="__"` and use `APP_DB__URL` |
| `SecretStr` value is empty in `app.config` | Used `model_dump()` which masks secrets | Use `.get_secret_value()` explicitly for the few fields that need to land in `app.config` |
| `.env` file values ignored | File path is relative to CWD, not the module | Use absolute path: `env_file=Path(__file__).parent.parent / ".env"` |
| Validation error message is huge | Pydantic v2 dumps the entire input by default | Set `model_config["hide_input_in_errors"] = True` |
| Boolean `"False"` evaluates to `True` | Some shells quote `"False"` as a non-empty string; Pydantic treats non-empty strings as truthy without bool coercion | Ensure env var is `APP_DEBUG=false` (lowercase) or use `field_validator` to handle string→bool explicitly |
| Tests fail with "port already in use" | Validators check `os.cpu_count()` or similar system state | Mock system calls in the validator, or skip the validator in test config |

> [!danger] Don't `print(settings)` in logs
> `SecretStr.__repr__` masks the value, but if you do `print(settings.model_dump())` the dump *also* masks — good. But `print(settings.model_dump(mode="json", context={"reveal": True}))` or iterating fields and printing values bypasses the mask. Audit any logging code that touches settings.

---

## 11. Best Practices Checklist

> [!success] Typed-config hygiene
> - [ ] One `BaseSettings` subclass per environment (dev/prod/test), sharing an abstract base.
> - [ ] `model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="forbid")`.
> - [ ] Required fields have no default — app refuses to boot if missing.
> - [ ] Secrets are `SecretStr`, accessed via `.get_secret_value()` only where needed.
> - [ ] Production-only invariants enforced via `@model_validator(mode="after")` on `ProdSettings`.
> - [ ] `.env.example` committed; `.env*` git-ignored except `.env.example`.
> - [ ] A `Settings` instance is bound into Flask-Injector (see [[Flask-Injector]]) so services never read `current_app.config`.
> - [ ] Validators are pure: no I/O, no `current_app` references, no time-dependent logic.
> - [ ] `customise_sources` is overridden only when integrating secret managers; the default order is correct for 90% of apps.
> - [ ] CI runs `Settings()` instantiation as a step — misconfigured env vars fail the build before deploy.

---

## 12. Further Reading & Cross-References

- **Official docs:** <https://docs.pydantic.dev/latest/concepts/pydantic_settings/> — the canonical reference for `pydantic-settings` v2.
- **Pydantic v2 migration guide:** <https://docs.pydantic.dev/latest/migration/> — if you're upgrading from v1 `BaseSettings`.
- **12-Factor App, §III Config:** <https://12factor.net/config> — the philosophical basis for env-var-driven config.
- **Related notes in this vault:**
  - [[Flask-Environments]] — environment selection that picks the right `Settings` subclass.
  - [[Flask-Injector]] — injecting the `Settings` instance into services.
  - [[Flask-SQLAlchemy]] — `database_url: PostgresDsn` flows straight into `SQLALCHEMY_DATABASE_URI`.
  - [[Flask-Caching]] — `redis_url` from settings feeds `CacheConfig`.
  - [[Flask-FeatureFlags]] — feature flag defaults can live in `Settings`.

> [!quote] The Twelve-Factor App
> "Apps sometimes use config files that do not get checked into version control, such as `config/database.yml` in Rails. This is an improvement over using constants which are checked into the code repo, but still has weaknesses: it's easy to mistakenly check in a config file to the repo; there tends to be a proliferation of config files… The twelve-factor app stores config in environment variables."
>
> Pydantic-Settings is the typed, validated, secret-aware realisation of that principle for Flask.
