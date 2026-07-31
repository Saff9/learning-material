---
title: Configuration
description: How to configure Flask applications for development, testing, and production environments
chapter: 01-Flask-Core
tags:
  - configuration
  - config
  - environment-variables
  - python-dotenv
  - production
  - core
difficulty: Beginner
prerequisites:
  - [[01-Flask-Core/Flask-CLI]]
---

# Configuration

> Every Flask application needs configuration — database URLs, secret keys, API credentials, debug flags. Managing these settings across development, testing, and production environments is a critical skill. Done wrong, you leak secrets or deploy insecure defaults. Done right, your application adapts seamlessly to any environment.

## Learning Objectives

After completing this chapter, you will be able to:

- Configure Flask using Python dictionaries, object attributes, and environment variables
- Implement environment-specific configuration classes
- Use `python-dotenv` for local development configuration
- Manage secret keys and sensitive credentials securely
- Validate configuration at application startup
- Explain the configuration hierarchy and precedence rules

## Flask's Config Object

Flask stores configuration in `app.config`, a dictionary-like object:

```python
from flask import Flask

app = Flask(__name__)

# Direct assignment
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
```

### Built-in Configuration Keys

| Key | Default | Purpose |
|-----|---------|---------|
| `DEBUG` | `False` | Enable debug mode (auto-reload, debugger) |
| `TESTING` | `False` | Enable testing mode (propagate exceptions) |
| `SECRET_KEY` | `None` | Key for signing sessions and tokens |
| `SERVER_NAME` | `None` | Hostname and port (for URL generation) |
| `APPLICATION_ROOT` | `/` | Root path for the application |
| `MAX_CONTENT_LENGTH` | `None` | Max request body size (bytes) |
| `PERMANENT_SESSION_LIFETIME` | `timedelta(days=31)` | Session cookie duration |
| `USE_X_SENDFILE` | `False` | Use web server for file sending |
| `JSON_AS_ASCII` | `True` | Escape non-ASCII JSON characters |
| `JSON_SORT_KEYS` | `True` | Sort JSON keys alphabetically |
| `JSONIFY_PRETTYPRINT_REGULAR` | `False` | Pretty-print JSON responses |

### Extension Configuration Keys

Extensions add their own configuration keys:

| Key | Extension | Purpose |
|-----|-----------|---------|
| `SQLALCHEMY_DATABASE_URI` | Flask-SQLAlchemy | Database connection string |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | Flask-SQLAlchemy | Track object modifications |
| `MAIL_SERVER` | Flask-Mail | SMTP server hostname |
| `MAIL_PORT` | Flask-Mail | SMTP server port |
| `MAIL_USERNAME` | Flask-Mail | SMTP authentication username |
| `MAIL_PASSWORD` | Flask-Mail | SMTP authentication password |
| `MAIL_DEFAULT_SENDER` | Flask-Mail | Default "from" address |
| `WTF_CSRF_ENABLED` | Flask-WTF | Enable CSRF protection |
| `WTF_CSRF_SECRET_KEY` | Flask-WTF | Separate key for CSRF tokens |

## Configuration Methods

### 1. Direct Dictionary Assignment

```python
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'hardcoded-secret'
```

Simple but not maintainable for complex applications.

### 2. From Python Object

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log all SQL queries

class ProductionConfig(Config):
    DEBUG = False
    # Production overrides

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Load configuration
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config_by_name[env])
```

This is the recommended pattern for production Flask applications.

### 3. From Environment Variable

```python
app.config.from_envvar('FLASK_SETTINGS')
```

The `FLASK_SETTINGS` environment variable points to a Python file:

```bash
export FLASK_SETTINGS=/path/to/production_settings.py
```

The file contains Python code that sets configuration values:

```python
# /path/to/production_settings.py
SECRET_KEY = 'actual-production-secret'
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@dbhost/app'
DEBUG = False
```

### 4. From Python File

```python
app.config.from_pyfile('config.py', silent=True)
```

Loads configuration from a Python file relative to the application root.

### 5. From JSON File

```python
app.config.from_json('config.json', silent=True)
```

### 6. From Mapping

```python
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE='sqlite:///app.db',
)
```

### 7. From Environment Variables (python-dotenv)

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file before reading config

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
```

`.env` file (never commit to version control):

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///dev.db
FLASK_DEBUG=1
```

> [!WARNING]
> Never commit `.env` files containing real secrets to version control. Add `.env` to your `.gitignore` immediately.

## Configuration Hierarchy

Configuration can be loaded from multiple sources. Later loads override earlier ones:

1. Default Flask configuration
2. `app.config.from_object()` — base configuration class
3. `app.config.from_pyfile()` — environment-specific file
4. `app.config.from_envvar()` — environment variable pointing to file
5. Direct assignment — runtime overrides

```python
app = Flask(__name__)
app.config.from_object('config.DefaultConfig')   # Base
app.config.from_pyfile('production.py', silent=True)  # Override
app.config.from_envvar('APP_CONFIG', silent=True)     # Final override
```

## Environment-Specific Configuration Pattern

The recommended structure for a production Flask application:

```python
# config.py
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "data-dev.db")}'
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.test'

class ProductionConfig(Config):
    """Production configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "data.db")}'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=10)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
```

Usage with application factory:

```python
# app/__init__.py
from flask import Flask
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    
    # Register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
```

## Secret Key Management

The `SECRET_KEY` is used for signing session cookies and other security features. It must be cryptographically random and kept secret.

### Generating a Secret Key

```python
import secrets
secret_key = secrets.token_hex(32)  # 64-character hex string
```

```bash
# Command line
python -c "import secrets; print(secrets.token_hex(32))"
```

### Environment Variable Pattern

```bash
# .env (never commit this!)
SECRET_KEY=a1b2c3d4e5f6...64-char-hex-string...
```

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError('No SECRET_KEY set for application')
```

### Docker Secret Pattern

In Docker deployments, use Docker secrets:

```python
class Config:
    SECRET_KEY = _read_secret('/run/secrets/secret_key')

def _read_secret(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except FileNotFoundError:
        return os.environ.get('SECRET_KEY')
```

## Configuration Validation

Validate configuration at startup to catch missing or invalid values:

```python
def validate_config(app):
    required = ['SECRET_KEY', 'SQLALCHEMY_DATABASE_URI']
    missing = [key for key in required if not app.config.get(key)]
    if missing:
        raise RuntimeError(f'Missing required configuration: {", ".join(missing)}')
    
    if app.config['ENV'] == 'production':
        if app.config.get('DEBUG'):
            app.logger.warning('DEBUG should not be enabled in production')
        if not app.config.get('SECRET_KEY') or len(app.config['SECRET_KEY']) < 16:
            raise RuntimeError('SECRET_KEY must be at least 16 characters in production')
```

## Instance Folders

Flask supports instance folders — a separate directory for configuration and data that should not be under version control:

```
myapp/
    __init__.py
    static/
    templates/
instance/
    config.py  # Not in version control
```

```python
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py', silent=True)  # Loads from instance/
```

The instance folder is ideal for:
- Production configuration with secrets
- SQLite database files
- Uploaded files
- SSL certificates

## Common Mistakes

**Mistake: Hardcoding secrets in source code**
Never commit API keys, passwords, or `SECRET_KEY` to version control. Use environment variables.

**Mistake: Using the same secret key for all environments**
Each environment should have its own `SECRET_KEY`.

**Mistake: Not setting `TESTING = True` in test configuration**
Without this, Flask will not propagate exceptions in tests.

**Mistake: Using debug mode in production**
Debug mode exposes stack traces and enables the interactive debugger — both critical security vulnerabilities.

## Best Practices

- Use configuration classes for different environments
- Never commit secrets to version control
- Use `python-dotenv` for local development
- Validate configuration at startup
- Use environment variables for production secrets
- Set `instance_relative_config=True` for instance folder support
- Log configuration issues clearly
- Use separate `SECRET_KEY` values per environment

## Exercises

1. **Config Classes**: Create configuration classes for development, testing, and production. Load the correct one based on an environment variable.

2. **Secret Generation**: Write a script that generates a secure secret key and saves it to a `.env` file.

3. **Config Validation**: Add validation to your configuration that raises a clear error if required values are missing.

4. **Instance Folder**: Set up an instance folder with production configuration and a SQLite database.

## Quiz

**Question 1**: What are the different ways to load configuration in Flask?

**Question 2**: Why should you use configuration classes instead of direct dictionary assignment?

**Question 3**: How do you keep secrets out of version control while still making them available to your application?

**Question 4**: What is an instance folder, and when would you use it?

**Question 5**: What happens if `SECRET_KEY` is not set, and why is it critical?

## Interview Questions

1. "How would you structure configuration for a Flask app with development, staging, and production environments?"

2. "Where do you store secrets like database passwords and API keys? Why?"

3. "What is the difference between `app.config.from_object()` and `app.config.from_pyfile()`?"

4. "How would you validate configuration at application startup?"

5. "Explain the instance folder pattern in Flask. When is it useful?"

## Related Chapters

- Previous: [[01-Flask-Core/Flask-CLI]]
- [[06-Blueprints/Application-Factory]] — Configuration with the factory pattern
- [[Appendix/python-dotenv]] — Deep dive into python-dotenv
- [[07-Deployment/Environment-Variables]] — Production environment configuration

## Official Documentation References

- [Flask Configuration Handling](https://flask.palletsprojects.com/en/latest/config/)
- [Flask Instance Folders](https://flask.palletsprojects.com/en/latest/config/#instance-folders)
- [python-dotenv Documentation](https://saurabh-kumar.com/python-dotenv/)

---

*Previous: [[01-Flask-Core/Flask-CLI]] | Next: [[02-Jinja2/Jinja2-Overview]]*