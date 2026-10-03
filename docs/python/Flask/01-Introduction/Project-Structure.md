---
title: Project Structure
tags:
  - flask
  - structure
  - blueprints
  - packaging
  - layout
aliases:
  - Flask Project Layout
  - Flask Folder Structure
  - Flask App Structure
related:
  - "[[Flask-Overview]]"
  - "[[Installation-Guide]]"
  - "[[Flask-SQLAlchemy]]"
created: 2024-01-15
updated: 2024-01-15
---

# Project Structure

#flask #structure #blueprints #packaging

> [!info] Layout matters
> Flask is famously unopinionated about file structure — you can write a real app in a single file or split it across 200 modules. This note shows the layouts that actually scale, and explains where each extension should live.

A Flask app starts as a single `app.py` and grows. Without discipline, it becomes a 5000-line `app.py` that nobody wants to touch. This note documents three patterns — **single file**, **small package**, and **large application** — and where every extension fits in each.

---

## The Three Layouts

### 1. Single-file layout (toys, scripts, demos)

For a script that does one thing — a webhook receiver, a small dashboard, a CLI with a tiny web UI — a single file is fine.

```
my_app/
└── app.py
```

```python
# app.py
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json
    # ... process ...
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=True)
```

> [!warning] When to upgrade
> Move to a package as soon as you add: tests, a config file, a database, more than ~5 routes, or any extension that needs `init_app`.

### 2. Small package layout (most apps)

A small package is a directory containing `__init__.py`, separate modules for routes/models/forms, and parallel `tests/` and `templates/` folders.

```
my_app/
├── app/
│   ├── __init__.py        # application factory
│   ├── config.py          # configuration classes
│   ├── models.py          # SQLAlchemy models
│   ├── forms.py           # Flask-WTF forms
│   ├── routes.py          # all views (or split per concern)
│   ├── templates/
│   │   ├── base.html
│   │   └── index.html
│   └── static/
│       ├── style.css
│       └── app.js
├── tests/
│   ├── conftest.py
│   └── test_routes.py
├── requirements.txt
├── .env
├── .flaskenv
└── run.py
```

This is what Miguel Grinberg's Mega-Tutorial uses. It works well up to ~30 routes.

### 3. Large application layout (production apps)

For real production apps with multiple blueprints, background workers, and dedicated API surfaces, use the **blueprint-per-feature** layout.

```
my_app/
├── app/
│   ├── __init__.py              # create_app() factory
│   ├── extensions.py            # db, mail, cache, migrate — all created here
│   ├── config.py                # Config, DevelopmentConfig, ProductionConfig
│   ├── email.py                 # async email sending
│   ├── errors.py                # custom exception classes
│   ├── cli.py                   # custom flask CLI commands
│   │
│   ├── main/                    # blueprint: public website
│   │   ├── __init__.py          # bp = Blueprint("main", __name__)
│   │   ├── routes.py
│   │   ├── forms.py
│   │   └── templates/main/
│   │
│   ├── auth/                    # blueprint: authentication
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── forms.py
│   │   ├── email.py             # password-reset emails
│   │   └── templates/auth/
│   │
│   ├── api/                     # blueprint: REST API
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── users.py
│   │   │   ├── posts.py
│   │   │   └── tokens.py
│   │   ├── schemas.py           # Marshmallow schemas
│   │   ├── errors.py            # API error handlers
│   │   └── auth.py              # JWT decorators
│   │
│   ├── admin/                   # blueprint: Flask-Admin
│   │   ├── __init__.py
│   │   └── views.py
│   │
│   ├── models/                  # SQLAlchemy models, one file per domain
│   │   ├── __init__.py          # re-exports
│   │   ├── user.py
│   │   ├── post.py
│   │   └── mixins.py            # TimestampMixin, etc.
│   │
│   ├── services/                # business logic (not in views!)
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── post_service.py
│   │   └── billing_service.py
│   │
│   ├── tasks/                   # Celery tasks
│   │   ├── __init__.py          # celery = Celery(__name__, ...)
│   │   ├── emails.py
│   │   └── reports.py
│   │
│   ├── templates/               # shared templates (base.html, emails)
│   │   ├── base.html
│   │   ├── _macros.html
│   │   └── emails/
│   │       ├── password_reset.html
│   │       └── welcome.html
│   │
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
│
├── migrations/                  # Flask-Migrate / Alembic
│   ├── env.py
│   ├── versions/
│   └── alembic.ini
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # pytest fixtures
│   ├── factories.py             # factory_boy model factories
│   ├── unit/
│   │   ├── test_models.py
│   │   └── test_services.py
│   ├── integration/
│   │   ├── test_auth_flow.py
│   │   └── test_api.py
│   └── e2e/
│       └── test_checkout.py
│
├── scripts/                     # one-off maintenance scripts
│   ├── seed.py
│   └── cleanup.py
│
├── deploy/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── gunicorn.conf.py
│
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
│
├── .env                          # local secrets (gitignored)
├── .env.example                  # template, committed
├── .flaskenv                     # FLASK_APP=run.py, FLASK_ENV=development
├── .gitignore
├── pyproject.toml                # OR setup.cfg + requirements.txt
├── run.py                        # entrypoint: `python run.py`
├── wsgi.py                       # entrypoint: `gunicorn wsgi:app`
├── celery_worker.py              # entrypoint: `celery -A celery_worker.celery worker`
└── README.md
```

```mermaid
flowchart TB
  Root[my_app/] --> App[app/]
  Root --> Tests[tests/]
  Root --> Migrations[migrations/]
  Root --> Deploy[deploy/]
  Root --> Scripts[scripts/]
  Root --> Config[.env, pyproject.toml, run.py, wsgi.py]

  App --> Factory[__init__.py<br/>create_app]
  App --> Ext[extensions.py]
  App --> Models[models/]
  App --> Services[services/]
  App --> Tasks[tasks/]
  App --> Blueprints{blueprints}
  Blueprints --> Main[main/]
  Blueprints --> Auth[auth/]
  Blueprints --> API[api/]
  Blueprints --> Admin[admin/]
```

---

## Where Each Extension Lives

| Extension | File | Why |
|---|---|---|
| `Flask` (the app) | `app/__init__.py` | The factory `create_app()` is the single source of truth. |
| `Flask-SQLAlchemy` (`db`) | `app/extensions.py` | Created at module scope, `db.init_app(app)` inside factory. |
| `Flask-Migrate` (`migrate`) | `app/extensions.py` | Same pattern. Needs `db`. |
| `Flask-Login` (`login_manager`) | `app/extensions.py` | Init in factory; `user_loader` registered in `app/auth/__init__.py` or models. |
| `Flask-Mail` (`mail`) | `app/extensions.py` | Init in factory. |
| `Flask-Caching` (`cache`) | `app/extensions.py` | Init in factory. |
| `Flask-WTF` (`CSRFProtect`) | `app/extensions.py` | Init in factory; enabled for forms. |
| `Flask-CORS` | `app/__init__.py` (inside factory) | Often configured inline per-blueprint. |
| `Flask-Limiter` (`limiter`) | `app/extensions.py` | Init in factory; decorators in routes. |
| `Flask-JWT-Extended` (`jwt`) | `app/extensions.py` | Init in factory; decorators in API routes. |
| `Flask-Admin` (`admin`) | `app/admin/__init__.py` | Per-blueprint because admin has its own init. |
| `Marshmallow` (`ma`) | `app/extensions.py` | Init in factory; schemas in `app/api/schemas.py`. |
| `Celery` (`celery`) | `app/tasks/__init__.py` | Separate entrypoint (`celery_worker.py`). |
| `Flask-SocketIO` (`socketio`) | `app/extensions.py` | Init last; wraps the app instead of being wrapped. |
| `Flask-RESTful` (`api`) | `app/api/__init__.py` | Per-blueprint resources. |

### The `extensions.py` pattern

```python
# app/extensions.py
"""
Module-scope instantiation of extensions.

Each extension is created here, *unbound* to any specific Flask app.
The factory in app/__init__.py binds them with `ext.init_app(app)`.

This pattern lets you:
- Have multiple Flask apps in one process (e.g., public + admin)
- Use the extension in tests without circular imports
- Avoid the `app` global that breaks Flask 1.x style code
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_caching import Cache
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from marshmallow import Marshmallow

# Databases & migrations
db = SQLAlchemy()
migrate = Migrate()

# Auth
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
jwt = JWTManager()

# Utilities
mail = Mail()
cache = Cache()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per hour"])
cors = CORS()
socketio = SocketIO()
ma = Marshmallow()
```

```python
# app/__init__.py
from flask import Flask
from config import Config
from app.extensions import (
    db, migrate, login_manager, jwt, mail, cache,
    csrf, limiter, cors, socketio, ma,
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init all extensions against this app.
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    ma.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*")

    # Register blueprints
    from app.main import bp as main_bp
    from app.auth import bp as auth_bp
    from app.api import bp as api_bp
    from app.admin import bp as admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Register user loader
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register CLI commands
    from app.cli import register_cli_commands
    register_cli_commands(app)

    return app
```

> [!tip] Avoid circular imports
> The `extensions.py` pattern exists specifically to avoid circular imports between `app/__init__.py`, `models.py`, and `routes.py`. Models import `db` from `extensions.py`; routes import `db` and models; the factory imports routes via blueprints. No cycle.

```mermaid
classDiagram
    class FlaskApp {
        +create_app() Flask
    }
    class ExtensionsModule {
        +db: SQLAlchemy
        +migrate: Migrate
        +login_manager: LoginManager
        +jwt: JWTManager
        +mail: Mail
        +cache: Cache
    }
    class ModelModule {
        +User
        +Post
        +Comment
    }
    class RoutesModule {
        +main_bp
        +auth_bp
        +api_bp
    }
    class ServiceModule {
        +post_service
        +auth_service
    }
    class BlueprintModule {
        +bp: Blueprint
    }

    FlaskApp --> ExtensionsModule : imports db etc.
    FlaskApp --> BlueprintModule : register_blueprint
    ModelModule --> ExtensionsModule : imports db
    RoutesModule --> ExtensionsModule : imports db
    RoutesModule --> ModelModule : imports User, Post
    RoutesModule --> ServiceModule : calls services
    ServiceModule --> ExtensionsModule : imports db, mail
    ServiceModule --> ModelModule : imports models
    BlueprintModule --> RoutesModule : imports routes

    note for FlaskApp "Factory imports blueprints lazily (inside create_app) to break the cycle."
    note for ExtensionsModule "No imports from app/ — fully leaf module. This is what breaks the cycle."
```

The arrows all flow *downward*: extensions is a leaf, models depend on extensions, services depend on both, routes depend on all three, and the factory wires them together. No arrows point back up.

---

## Configuration Files

### `config.py` — configuration classes

```python
# app/config.py
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base config. Production and dev override as needed."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-in-prod"

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{basedir}/../app.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }

    # Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # CSRF
    WTF_CSRF_TIME_LIMIT = 3600

    # Mail
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")

    # Cache
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Rate limiting
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "redis://localhost:6379/1")

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # CORS
    CORS_ORIGIN_WHITELIST = ["https://example.com", "http://localhost:3000"]

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL",
        f"sqlite:///{basedir}/../dev.db",
    )
    SESSION_COOKIE_SECURE = False  # http://localhost


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    RATELIMIT_ENABLED = False
    CACHE_TYPE = "SimpleCache"


class ProductionConfig(Config):
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # Production-only side effects (e.g., Sentry init)
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        sentry_sdk.init(
            dsn=os.environ.get("SENTRY_DSN"),
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
        )


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
```

### `.env` — local secrets (gitignored)

```bash
# .env — never commit this file
SECRET_KEY=your-random-256-bit-hex-string
DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=another-random-string
MAIL_USERNAME=you@example.com
MAIL_PASSWORD=app-specific-password
SENTRY_DSN=https://...@sentry.io/...
```

### `.env.example` — template (committed)

```bash
# .env.example — copy to .env and fill in real values
SECRET_KEY=
DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=
MAIL_USERNAME=
MAIL_PASSWORD=
SENTRY_DSN=
```

### `.flaskenv` — Flask CLI defaults

```bash
# .flaskenv — read by `flask` CLI
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
```

The `python-dotenv` library (installed with Flask) reads these automatically when you run `flask run` or `flask shell`.

### `run.py` and `wsgi.py`

```python
# run.py — for local development (`python run.py` or `flask run`)
from app import create_app
from app.config import config

app = create_app(config["development"])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
```

```python
# wsgi.py — for production (`gunicorn wsgi:app`)
from app import create_app
from app.config import config
import os

app = create_app(config[os.environ.get("FLASK_CONFIG", "production")])
```

### `requirements.txt` (or `pyproject.toml`)

```
# requirements/base.txt
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
gunicorn==22.0.0
```

```
# requirements/dev.txt
-r base.txt
pytest==8.2.2
pytest-cov==5.0.0
pytest-flask==1.3.0
factory-boy==3.3.0
ipython==8.25.0
flask-debugtoolbar==0.15.1
```

See [[Installation-Guide]] for the full setup walkthrough.

---

## The Service Layer Pattern

A common Flask anti-pattern is putting business logic in view functions. Don't. Views should be thin: parse input, call a service, return a response.

```python
# ❌ Bad: business logic in route
@bp.route("/posts", methods=["POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data)
        post.author = current_user
        # ... 20 more lines of business logic ...
        db.session.add(post)
        db.session.commit()
        send_email(current_user.email, "Post published!")
        enqueue_seo_reindex(post.id)
        return redirect(url_for("main.post", id=post.id))
    return render_template("posts/new.html", form=form)
```

```python
# ✅ Good: thin route, fat service
@bp.route("/posts", methods=["POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = post_service.create_post(
            author=current_user,
            title=form.title.data,
            body=form.body.data,
        )
        return redirect(url_for("main.post", id=post.id))
    return render_template("posts/new.html", form=form)
```

```python
# app/services/post_service.py
from app.extensions import db, mail
from app.models.post import Post
from app.tasks.emails import send_publication_email
from app.tasks.seo import reindex_post


def create_post(*, author, title, body, publish=True):
    """Create and persist a new post. Returns the saved Post."""
    post = Post(title=title, body=body, author=author, is_published=publish)
    db.session.add(post)
    db.session.commit()

    # Side effects — async via Celery
    send_publication_email.delay(author.id, post.id)
    reindex_post.delay(post.id)

    return post
```

> [!tip] The rule of thumb
> If a view function is more than ~20 lines, extract a service. If a service is more than ~150 lines, split it. If a model file is more than ~300 lines, you have two models.

```mermaid
flowchart LR
    Req[HTTP Request] --> Route[Route handler<br/>thin: parse + validate]
    Route --> Form[Flask-WTF form]
    Form -->|valid| Service[Service function<br/>fat: business logic]
    Form -->|invalid| Route
    Service --> Model[SQLAlchemy model]
    Service --> DB[(Database)]
    Service --> Task[Celery task<br/>.delay\(\)]
    Service --> Schema[Marshmallow schema]
    Schema --> Resp[JSON/HTML response]
    Task -.->|async| DB
    Route --> Resp
```

The view's only job is to translate HTTP ↔ service calls. Everything else — DB writes, side effects, async work — happens in the service.

---

## Mermaid: A Blueprint-Aware App

```mermaid
flowchart TB
  subgraph Factory[app/__init__.py — create_app]
    F1[Load config] --> F2[Init extensions]
    F2 --> F3[Register blueprints]
    F3 --> F4[Register error handlers]
    F4 --> F5[Register CLI commands]
  end

  subgraph Blueprints
    Main[main.bp]
    Auth[auth.bp — /auth]
    API[api.bp — /api/v1]
    Admin[admin.bp — /admin]
  end

  subgraph Domain
    Models[models/user.py<br/>models/post.py]
    Services[services/post_service.py<br/>services/auth_service.py]
    Tasks[tasks/emails.py<br/>tasks/reports.py]
  end

  Factory --> Blueprints
  Blueprints --> Services
  Services --> Models
  Services --> Tasks
  Tasks --> Models
```

---

## Common Mistakes

> [!warning] Don't do these
> 1. **Putting `db = SQLAlchemy(app)` inside `create_app`.** This breaks tests — each test creates a new app, but `db` is still bound to the first one.
> 2. **Importing views at the top of `__init__.py`.** This causes circular imports because views import models which import `db` which is in `extensions.py`. Use blueprint-internal imports.
> 3. **Using `app.config["SECRET_KEY"] = "hardcoded"`.** Always read from environment. See [[Security-Best-Practices]].
> 4. **Forgetting `migrations/` in version control.** Migrations are code. Commit them. See [[Flask-Migrate]].
> 5. **One giant `models.py`.** Once you have more than ~5 models, split per domain.
> 6. **No `tests/` directory.** Even an empty `test_smoke.py` makes you start writing tests.
> 7. **`SECRET_KEY` in `.env.example`.** The example file should have empty values, not real-looking ones, so people don't accidentally commit a "real-looking" secret.
> 8. **`flask run` in production.** Use Gunicorn. See [[Production-Deployment]].

---

## Practical Exercise

Build a small blog following the large-app layout:

1. Create the folder structure above (you can skip `admin/`, `tasks/`, `api/` for now).
2. Implement `User`, `Post`, `Comment` models — see [[Flask-SQLAlchemy]].
3. Add `flask db init` → `flask db migrate` → `flask db upgrade` — see [[Flask-Migrate]].
4. Add `auth` blueprint with login/logout — see [[Flask-Login]].
5. Add `main` blueprint with post list/detail routes.
6. Write 3 tests using pytest — see [[Pytest-Flask]].

Once done, you'll have the skeleton that the rest of this vault's notes plug into.

---

## Next Steps

- [[Installation-Guide]] — actually set up the environment.
- [[Flask-SQLAlchemy]] — define your models.
- [[Flask-Migrate]] — version-control the schema.
- [[Common-Patterns]] — more architectural patterns (repository, CQRS, etc.)

---

## References

- [Larger Applications — Flask docs](https://flask.palletsprojects.com/en/latest/patterns/packages/)
- [Application Factories — Flask docs](https://flask.palletsprojects.com/en/latest/patterns/appfactories/)
- [The Flask Mega-Tutorial — Miguel Grinberg](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
- [Cookiecutter Flask](https://github.com/cookiecutter-flask/cookiecutter-flask) — a popular Flask project template.
- [Structuring Flask Apps — Hackers and Slackers](https://hackersandslackers.com/organize-flask-apps/)

---

## Anti-Patterns to Avoid

Beyond the obvious mistakes already called out, here are subtler anti-patterns that creep into Flask codebases:

### Anti-pattern: The God Object `app.py`

A single file with the factory, the routes, the models, and the config all inlined. Works for a script, breaks down at ~200 lines. The fix is always the same: split into `app/__init__.py` (factory), `app/extensions.py` (extensions), `app/models/` (models), `app/main/routes.py` (views).

```mermaid
flowchart TD
    Start[God Object app.py<br/>5000 lines] --> Step1{Extract config}
    Step1 -->|move classes| ConfigFile[app/config.py]
    Start --> Step2{Extract extensions}
    Step2 -->|move db, etc.| ExtFile[app/extensions.py]
    Start --> Step3{Extract models}
    Step3 -->|move classes| ModelsDir[app/models/<br/>user.py, post.py]
    Start --> Step4{Extract routes}
    Step4 -->|move @app.route| BPDir[app/main/<br/>__init__.py, routes.py]
    Start --> Step5{Extract services}
    Step5 -->|move business logic| ServicesDir[app/services/<br/>post_service.py]
    ConfigFile --> Factory[app/__init__.py<br/>create_app factory]
    ExtFile --> Factory
    ModelsDir --> Factory
    BPDir --> Factory
    ServicesDir --> Factory
    Factory --> Done[~200 lines total<br/>across 10+ files]
```

### Anti-pattern: Logic in Templates

Jinja2 is powerful, which makes it tempting to put business logic in templates. Resist this. Templates should *display* data, not compute it. If you find yourself writing `{% set total = items | map(attribute='price') | sum %}`, move that calculation into the view function.

### Anti-pattern: Globals for Everything

```python
# ❌ Bad
from flask import g, current_app

def get_db():
    if "db" not in g:
        g.db = create_connection(current_app.config["DATABASE_URL"])
    return g.db
```

This pattern (from the official Flask tutorial) is fine for raw DBAPI connections but unnecessary if you use Flask-SQLAlchemy — `db.session` already handles per-request scoping. Don't reinvent it.

### Anti-pattern: `app.run()` in Production

The Flask dev server (`app.run()`) is single-threaded, doesn't handle SSL, doesn't scale. Production needs Gunicorn (or uWSGI, or `waitress` on Windows). See [[Production-Deployment]].

### Anti-pattern: Committing the SQLite `.db` File

If you use SQLite in development, add `*.db` to `.gitignore`. Committing the database file means every developer's local data gets pushed, leading to merge conflicts on a binary file. Use a seed script instead — see `scripts/seed.py` in the structure above.

### Anti-pattern: Importing Models in `__init__.py` Eagerly

```python
# ❌ Bad — circular import
# app/__init__.py
from app import models   # imports models, which import db, which is defined here
```

Always import models lazily — either inside `create_app()` after `db.init_app(app)`, or in the blueprint that uses them.

```mermaid
stateDiagram-v2
    [*] --> ModuleImport: Python imports app/__init__.py
    ModuleImport --> ExtensionsCreated: db, migrate, ... instantiated\nunbound
    ExtensionsCreated --> FactoryCalled: create_app\(\) invoked
    FactoryCalled --> ConfigLoaded: app.config.from_object
    ConfigLoaded --> ExtInit: db.init_app\(app\)\nmigrate.init_app\(app, db\)
    ExtInit --> BPsRegistered: register_blueprint called per bp
    BPsRegistered --> LoadersWired: user_loader, jwt hooks
    LoadersWired --> AppReady: return app
    AppReady --> Serving: gunicorn / flask run
    Serving --> AppReady: new request handled\n(app context pushed per request)
    Serving --> [*]: process exit

    note right of ExtInit
        Models must NOT be imported before this point
        or db.metadata will be empty.
    end note
```

---

## Scaling Beyond a Single Process

The structure above assumes a single Flask process. As you scale, you'll need to think about multi-process concerns:

### Multiple Gunicorn workers

Gunicorn forks your app into N worker processes (typically `2 * CPU + 1`). Each worker has its own Python interpreter, its own in-memory state. Implications:

- **In-memory caches don't share.** A value cached in `flask_caching` with `SimpleCache` is per-worker. Use Redis for shared cache.
- **Sessions: fine.** Flask sessions are cookie-based (signed), so they work across workers automatically.
- **Database connections: per-worker.** Each worker has its own connection pool. With `pool_size=20` and 8 workers, you have 160 connections to Postgres. Make sure your DB can handle that.

### Celery workers

Celery runs in a separate process (or many). It does NOT share the Flask app's memory. To use Flask extensions in Celery tasks:

```python
# app/tasks/__init__.py
from celery import Celery
from app import create_app

flask_app = create_app()
celery = Celery(flask_app.import_name,
                broker=flask_app.config["CELERY_BROKER_URL"],
                backend=flask_app.config["CELERY_RESULT_BACKEND"])

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask
```

See [[Celery]] for the full pattern.

### Multiple machines (horizontal scaling)

When you scale beyond one machine:

- **Sessions: still fine** (cookie-based).
- **Cache: must be shared.** Redis, Memcached.
- **File uploads: must be shared.** S3, not local disk.
- **Database: must be shared.** Managed Postgres (RDS, Cloud SQL).
- **WebSockets: tricky.** Flask-SocketIO needs a message queue (Redis) to broadcast across nodes. See [[Flask-SocketIO]].

### Mermaid: Scaling stages

```mermaid
flowchart TB
  Stage1[Stage 1: single process<br/>flask run] --> Stage2[Stage 2: Gunicorn<br/>2N+1 workers]
  Stage2 --> Stage3[Stage 3: Gunicorn + Celery<br/>background tasks]
  Stage3 --> Stage4[Stage 4: Multiple machines<br/>behind load balancer]
  Stage4 --> Stage5[Stage 5: Microservices<br/>split by domain]

  Stage2 -.-> Need1[Need: shared DB pool]
  Stage3 -.-> Need2[Need: shared Redis<br/>for broker & cache]
  Stage4 -.-> Need3[Need: shared S3<br/>for uploads]
  Stage5 -.-> Need4[Need: API contracts<br/>+ observability]
```

Each stage adds operational complexity. Don't skip ahead — a single Gunicorn worker with a tuned DB connection pool handles most small-to-medium apps.

---

## A Checklist for a Production-Ready Structure

Before you ship, verify your project has:

- [ ] Application factory pattern (`create_app()`)
- [ ] `extensions.py` with all extensions created unbound
- [ ] Config classes for dev, test, prod
- [ ] `.env` (gitignored) and `.env.example` (committed)
- [ ] `requirements/` split into `base.txt`, `dev.txt`, `prod.txt`
- [ ] `tests/` directory with `conftest.py`
- [ ] `migrations/` committed to git
- [ ] `deploy/` with Dockerfile, docker-compose.yml, nginx config
- [ ] Service layer separating business logic from views
- [ ] Blueprints for major feature areas (auth, api, admin)
- [ ] `gunicorn` configured (`deploy/gunicorn.conf.py`)
- [ ] Logging configured (not just `print()`)
- [ ] Sentry or equivalent error tracking
- [ ] Health-check endpoint (`/health`)

If any of these are missing, see the relevant note: [[Project-Structure]] for layout, [[Production-Deployment]] for ops, [[Security-Best-Practices]] for hardening.

---

*See also: [[Flask-Overview]] · [[Installation-Guide]] · [[Flask-SQLAlchemy]] · [[00-Map-of-Content]]*
