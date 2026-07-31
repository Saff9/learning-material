---
title: Flask CLI
description: Flask's command-line interface for running the development server, managing the application, and creating custom commands
chapter: 01-Flask-Core
tags:
  - cli
  - flask-command
  - development-server
  - click
  - custom-commands
  - core
difficulty: Beginner
prerequisites:
  - [[01-Flask-Core/Error-Handling]]
---

# Flask CLI

> Flask provides a powerful command-line interface for running your application, interacting with it via a Python shell, and creating custom management commands. Understanding the CLI thoroughly will speed up your development workflow significantly.

## Learning Objectives

After completing this chapter, you will be able to:

- Use `flask run` for development with auto-reloading and debugger
- Use `flask shell` for interactive debugging and data inspection
- Create custom CLI commands using Click decorators
- Configure environment variables for Flask CLI
- Debug common CLI issues (FLASK_APP not found, import errors)
- Build management commands for database seeding, cache clearing, etc.

## The `flask` Command

Flask installs a `flask` command-line script. It discovers your application through the `FLASK_APP` environment variable:

```bash
# Set the application
export FLASK_APP=hello.py        # File containing the app
export FLASK_APP=myapp:create_app  # Factory function
export FLASK_APP=myapp           # Package with factory

# Run the development server
flask run

# Open a Python shell with app context
flask shell

# Show all routes
flask routes
```

## `flask run` — Development Server

The development server is for local development only:

```bash
# Basic usage
flask run

# Custom host and port
flask run --host=0.0.0.0 --port=8080

# Enable debugger and auto-reload
flask run --debug

# Or set environment variable
export FLASK_DEBUG=1
flask run
```

> [!WARNING]
> The development server is single-threaded (by default) and not security-hardened. Never use it in production. Use Gunicorn behind Nginx instead.

### Debug Mode

```bash
flask run --debug
```

Enables:
- **Auto-reloader**: Server restarts when code changes
- **Debugger**: Interactive traceback page on errors
- **Verbose error pages**: Detailed error information

> [!WARNING]
> Never enable debug mode in production. The interactive debugger allows arbitrary code execution.

## `flask shell` — Interactive Shell

Opens a Python REPL with the application context pre-pushed:

```bash
$ flask shell
>>> app
<Flask 'myapp'>
>>> current_app.name
'myapp'
>>> from myapp.models import User
>>> User.query.all()
[<User 'alice'>, <User 'bob'>]
```

### Custom Shell Context

```python
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Post': Post,
        'app': app
    }
```

Now these are available without importing:

```bash
$ flask shell
>>> User.query.first()
<User 'alice'>
>>> db.session.query(User).count()
2
```

## `flask routes` — Route Inspector

Shows all registered routes:

```bash
$ flask routes
Endpoint    Methods    Rule
----------  ---------  ------------------------
index       GET        /
user        GET        /user/<username>
static      GET        /static/<path:filename>
```

## Custom CLI Commands

Flask uses Click for custom commands. Register them with `@app.cli.command()`:

### Basic Command

```python
import click

@app.cli.command('hello')
@click.option('--name', default='World', help='Who to greet')
def hello_command(name):
    """Say hello."""
    click.echo(f'Hello, {name}!')
```

Usage:

```bash
$ flask hello
Hello, World!

$ flask hello --name=Flask
Hello, Flask!
```

### Command with Arguments

```python
@app.cli.command('create-user')
@click.argument('username')
@click.option('--email', required=True, help='Email address')
@click.option('--admin', is_flag=True, help='Make user admin')
def create_user_command(username, email, admin):
    """Create a new user."""
    user = User(username=username, email=email, is_admin=admin)
    db.session.add(user)
    db.session.commit()
    click.echo(f'Created user: {username} (admin={admin})')
```

```bash
$ flask create-user john --email=john@example.com --admin
Created user: john (admin=True)
```

### Database Seeding Command

```python
@app.cli.command('seed-db')
def seed_db_command():
    """Seed the database with sample data."""
    # Clear existing data
    db.drop_all()
    db.create_all()
    
    # Create sample users
    users = [
        User(username='alice', email='alice@example.com'),
        User(username='bob', email='bob@example.com'),
        User(username='charlie', email='charlie@example.com'),
    ]
    for user in users:
        db.session.add(user)
    
    db.session.commit()
    click.echo(f'Created {len(users)} users')
```

### Command Group

```python
@app.cli.group('db')
def db_group():
    """Database management commands."""
    pass

@db_group.command('create')
def db_create():
    """Create all tables."""
    db.create_all()
    click.echo('Tables created')

@db_group.command('drop')
@click.confirmation_option(prompt='Are you sure?')
def db_drop():
    """Drop all tables."""
    db.drop_all()
    click.echo('Tables dropped')

@db_group.command('reset')
def db_reset():
    """Drop and recreate all tables."""
    db.drop_all()
    db.create_all()
    click.echo('Database reset')
```

```bash
$ flask db --help
$ flask db create
$ flask db drop
Are you sure? [y/N]: y
Tables dropped
$ flask db reset
```

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `FLASK_APP` | Python import path to app | `hello.py`, `myapp:create_app` |
| `FLASK_ENV` | Environment (deprecated, use FLASK_DEBUG) | `development`, `production` |
| `FLASK_DEBUG` | Enable debug mode | `1`, `0` |
| `FLASK_RUN_HOST` | Default host for `flask run` | `0.0.0.0` |
| `FLASK_RUN_PORT` | Default port for `flask run` | `8080` |
| `FLASK_RUN_CERT` | SSL certificate file | `cert.pem` |
| `FLASK_RUN_KEY` | SSL private key file | `key.pem` |

### `.flaskenv` File

Store environment variables in a `.flaskenv` file (loaded by `python-dotenv`):

```
FLASK_APP=myapp:create_app
FLASK_DEBUG=1
FLASK_RUN_PORT=5000
```

## CLI with Application Factory

When using the application factory pattern:

```python
# myapp/__init__.py
def create_app(config_name='default'):
    app = Flask(__name__)
    # ... configure app ...
    return app
```

```bash
export FLASK_APP="myapp:create_app"
flask run
```

If the factory takes arguments, Click options can be added, but this is uncommon. Instead, use environment variables or configuration files.

## Common CLI Issues

### `Could not locate a Flask application`

```
Error: Could not locate a Flask application.
```

**Cause**: `FLASK_APP` is not set or points to a non-existent module.

**Fix**:
```bash
export FLASK_APP=hello.py  # Use the correct filename
```

### Import Errors

If your app imports fail, the CLI may show a traceback. Ensure:
- You are in the correct directory
- Your virtual environment is activated
- All dependencies are installed

### Module Not Found in Package

For package-based apps:
```bash
export FLASK_APP=myapp          # Package name
export PYTHONPATH="${PWD}"      # Add current dir to path
flask run
```

## Best Practices

- Use `flask shell` for database inspection and debugging
- Create custom commands for repetitive tasks (seeding, cleanup)
- Store `FLASK_APP` in `.flaskenv`
- Use `click.echo()` instead of `print()` in CLI commands
- Add help text and descriptions to all commands
- Use `@click.confirmation_option()` for destructive operations
- Never use the development server in production

## Exercises

1. **Custom Command**: Create a CLI command that lists all users in the database with their email addresses.

2. **Seed Command**: Create a command that seeds the database with 100 sample posts and users.

3. **Maintenance Command**: Create a command group with subcommands for clearing cache, rebuilding search index, and checking database connectivity.

## Quiz

**Question 1**: What environment variable tells the Flask CLI where to find your application?

**Question 2**: What is the difference between `flask run` and running `python app.py`?

**Question 3**: How do you create a custom CLI command in Flask?

**Question 4**: What is `flask shell`, and why is it more useful than a regular Python shell?

**Question 5**: Why should you use `click.echo()` instead of `print()` in CLI commands?

## Interview Questions

1. "How would you create a custom CLI command for database seeding in Flask?"

2. "What are the differences between running Flask with `flask run` and using a production WSGI server?"

3. "How would you use `flask shell` to debug a production data issue?"

4. "Explain the application factory pattern and how it works with the Flask CLI."

## Related Chapters

- Previous: [[01-Flask-Core/Error-Handling]]
- Next: [[01-Flask-Core/Configuration]]
- [[06-Blueprints/Application-Factory]] — Deep dive into the factory pattern
- [[Appendix/python-dotenv]] — Environment variable management

## Official Documentation References

- [Flask CLI Documentation](https://flask.palletsprojects.com/en/latest/cli/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Flask Custom Commands](https://flask.palletsprojects.com/en/latest/cli/#custom-commands)

---

*Previous: [[01-Flask-Core/Error-Handling]] | Next: [[01-Flask-Core/Configuration]]*