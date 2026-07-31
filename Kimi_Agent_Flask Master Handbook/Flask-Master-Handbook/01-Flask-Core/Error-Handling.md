---
title: Error Handling
description: How Flask handles errors — custom error pages, exception handling, and logging
chapter: 01-Flask-Core
tags:
  - error-handling
  - exceptions
  - logging
  - http-errors
  - errorhandlers
  - core
difficulty: Beginner
prerequisites:
  - [[01-Flask-Core/Templates]]
---

# Error Handling

> Errors are inevitable. Your database might be unreachable, a user might request a non-existent resource, or a third-party API might fail. How your Flask application handles these errors determines the user experience and your ability to diagnose problems. This chapter covers Flask's error handling mechanisms comprehensively.

## Learning Objectives

After completing this chapter, you will be able to:

- Register custom error handlers for HTTP errors and Python exceptions
- Create custom error page templates
- Handle 404, 500, and other common HTTP errors gracefully
- Implement application-wide error logging
- Use Flask's exception classes (HTTPException, abort)
- Distinguish between development and production error handling

## HTTP Errors in Flask

When something goes wrong, Flask returns an HTTP error response. By default:

- **404 Not Found**: No route matches the requested URL
- **405 Method Not Allowed**: Route exists but not for this HTTP method
- **500 Internal Server Error**: An unhandled exception occurred

### The `abort()` Function

Use `abort()` to immediately end a request with an HTTP error:

```python
from flask import abort

@app.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        abort(404)  # Return 404 Not Found
    return jsonify(user.to_dict())
```

You can abort with any HTTP status code:

```python
abort(400)   # Bad Request
abort(401)   # Unauthorized
abort(403)   # Forbidden
abort(404)   # Not Found
abort(422)   # Unprocessable Entity
abort(500)   # Internal Server Error
```

With a custom message:

```python
abort(404, description='User not found')
abort(400, description='Invalid email format')
```

## Custom Error Handlers

Use `app.errorhandler()` to register custom handlers for HTTP errors or exceptions:

```python
from flask import render_template, jsonify

@app.errorhandler(404)
def not_found(error):
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({'error': 'Resource not found'}), 404
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Roll back database transaction
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('errors/500.html'), 500
```

### Handling Custom Exceptions

Define your own exception classes and handle them:

```python
class ValidationError(Exception):
    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field
        self.message = message

class ResourceNotFoundError(Exception):
    def __init__(self, resource_type, resource_id):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f'{resource_type} {resource_id} not found')

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    response = {'error': error.message}
    if error.field:
        response['field'] = error.field
    return jsonify(response), 422

@app.errorhandler(ResourceNotFoundError)
def handle_not_found_error(error):
    return jsonify({
        'error': str(error),
        'resource_type': error.resource_type,
        'resource_id': error.resource_id
    }), 404

# Usage in view functions
@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        raise ResourceNotFoundError('User', user_id)
    return jsonify(user.to_dict())
```

### Generic Exception Handler

Catch all unhandled exceptions (use carefully):

```python
import traceback
import logging

logger = logging.getLogger(__name__)

@app.errorhandler(Exception)
def handle_unhandled_exception(error):
    logger.error(f"Unhandled exception: {str(error)}\n{traceback.format_exc()}")
    
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({'error': 'An unexpected error occurred'}), 500
    return render_template('errors/500.html'), 500
```

> [!WARNING]
> Always log the full exception (including traceback) before returning a generic error response. Otherwise, you will have no way to diagnose production issues. Never expose internal error details or stack traces to users in production.

## Error Page Templates

Create user-friendly error pages:

```html
<!-- templates/errors/404.html -->
{% extends "base.html" %}

{% block title %}Page Not Found{% endblock %}

{% block content %}
<div class="error-page">
    <h1>404 - Page Not Found</h1>
    <p>The page you are looking for does not exist.</p>
    <a href="{{ url_for('index') }}">Go Home</a>
</div>
{% endblock %}
```

```html
<!-- templates/errors/500.html -->
{% extends "base.html" %}

{% block title %}Server Error{% endblock %}

{% block content %}
<div class="error-page">
    <h1>500 - Server Error</h1>
    <p>Something went wrong on our end. We have been notified and are working to fix it.</p>
    <a href="{{ url_for('index') }}">Go Home</a>
</div>
{% endblock %}
```

## The Flask Debugger

In development mode (`FLASK_ENV=development` or `FLASK_DEBUG=1`), Flask shows an interactive debugger when an error occurs:

```
$ flask run --debug
```

The debugger:
- Shows the full traceback with clickable frames
- Allows you to inspect variables at each frame
- Provides an interactive console for executing code

> [!WARNING]
> **Never enable the debugger in production.** The interactive console allows arbitrary Python code execution, which is a critical security vulnerability.

## Logging

Flask uses Python's standard `logging` module. Configure logging for your application:

```python
import logging
from logging.handlers import RotatingFileHandler
import os

def configure_logging(app):
    if not app.debug:
        # Ensure log directory exists
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler with rotation (max 10MB, keep 10 backups)
        file_handler = RotatingFileHandler(
            'logs/flask_app.log',
            maxBytes=1024 * 1024 * 10,  # 10 MB
            backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Flask application startup')
```

Use logging in your application:

```python
from flask import current_app

@app.route('/process')
def process():
    current_app.logger.debug('Starting processing')
    try:
        result = do_something_complex()
        current_app.logger.info(f'Processing completed: {result}')
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f'Processing failed: {str(e)}')
        raise
```

### Log Levels

| Level | When to Use |
|-------|-------------|
| `DEBUG` | Detailed information for debugging |
| `INFO` | General application events (startup, completion) |
| `WARNING` | Something unexpected but not an error |
| `ERROR` | An error that prevented an operation from completing |
| `CRITICAL` | A serious error that may prevent the application from continuing |

## Database Error Handling

When using SQLAlchemy, always handle database errors:

```python
from sqlalchemy.exc import IntegrityError, OperationalError

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        user = User(**request.get_json())
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'User with this email already exists'}), 409
    except OperationalError:
        db.session.rollback()
        current_app.logger.error('Database connection failed')
        return jsonify({'error': 'Database unavailable'}), 503
```

## Error Handling Patterns

### Consistent API Error Format

Define a standard error response format for your API:

```python
def api_error(message, code=400, details=None):
    response = {'error': message}
    if details:
        response['details'] = details
    return jsonify(response), code

# Usage
@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return api_error('User not found', 404)
    return jsonify(user.to_dict())
```

### Global Error Middleware

```python
@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(422)
@app.errorhandler(500)
def handle_http_errors(error):
    """Handle all HTTP errors with a consistent format."""
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({
            'error': error.description if hasattr(error, 'description') else str(error),
            'status_code': error.code if hasattr(error, 'code') else 500
        }), error.code if hasattr(error, 'code') else 500
    return render_template(f'errors/{error.code}.html'), error.code
```

## Common Mistakes

**Mistake: Not rolling back database transactions on error**
Unrolled-back transactions can lock database rows. Always call `db.session.rollback()` in error handlers for 500 errors.

**Mistake: Exposing stack traces in production**
The Flask debugger and detailed error pages must never be enabled in production.

**Mistake: Silencing exceptions**
Bare `except:` clauses hide bugs. Always log exceptions before handling them.

**Mistake: Not handling 404s for API routes**
API clients need JSON error responses, not HTML error pages.

## Best Practices

- Create user-friendly error pages for web routes
- Return JSON errors for API routes
- Log all 500 errors with full tracebacks
- Roll back database transactions on errors
- Use custom exception classes for application-specific errors
- Never enable the debugger in production
- Set up log rotation to prevent disk space issues
- Use different error handling for development and production

## Exercises

1. **Custom Error Pages**: Create beautiful 404 and 500 error page templates for a Flask application.

2. **API Error Handler**: Implement a consistent JSON error response format and handler for all 4xx and 5xx errors.

3. **Custom Exceptions**: Define custom exceptions for your application (ValidationError, NotFoundError, PermissionError) and register handlers for each.

4. **Error Logging**: Set up logging to a rotating file. Add error handlers that log full tracebacks for all 500 errors.

## Quiz

**Question 1**: How do you register a custom error handler in Flask?

**Question 2**: What is the difference between `abort(404)` and `raise NotFound()`?

**Question 3**: Why should you never enable Flask's debugger in production?

**Question 4**: How do you distinguish between web and API requests when handling errors?

**Question 5**: Why is it important to roll back database transactions in error handlers?

## Interview Questions

1. "How would you implement custom error pages in Flask?"

2. "What is the difference between `app.errorhandler` and `app.register_error_handler`?"

3. "How would you handle errors differently for web pages vs. API endpoints?"

4. "A production Flask app returns 500 errors but you cannot see the details. How do you diagnose the problem?"

5. "Explain how you would set up logging for a production Flask application."

## Related Chapters

- Previous: [[01-Flask-Core/Templates]]
- Next: [[01-Flask-Core/Flask-CLI]]
- [[10-Advanced/Logging]] — Advanced logging strategies
- [[08-Security/Security-Overview]] — Security implications of error handling

## Official Documentation References

- [Flask Error Handling](https://flask.palletsprojects.com/en/latest/errorhandling/)
- [Flask Logging](https://flask.palletsprojects.com/en/latest/logging/)
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Werkzeug HTTP Exceptions](https://werkzeug.palletsprojects.com/en/latest/exceptions/)

---

*Previous: [[01-Flask-Core/Templates]] | Next: [[01-Flask-Core/Flask-CLI]]*