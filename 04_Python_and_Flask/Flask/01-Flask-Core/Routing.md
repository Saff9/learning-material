---
title: Routing
description: How Flask maps URLs to Python functions — the foundation of every web application
chapter: 01-Flask-Core
tags:
  - routing
  - url-rules
  - endpoints
  - decorators
  - werkzeug
  - core
difficulty: Beginner
prerequisites:
  - [[01-Flask-Core/Flask-Architecture]]
---

# Routing

> Routing is the mechanism that connects a URL to a Python function. When a user visits `/users/123`, routing determines which function handles that request. Understanding routing deeply — including URL rules, variable sections, endpoint naming, and reverse URL construction — is fundamental to building any Flask application.

## Learning Objectives

After completing this chapter, you will be able to:

- Explain how Flask's routing system works using Werkzeug's Map and Rule classes
- Create routes using the `@app.route()` decorator
- Define variable URL sections with type converters
- Use `url_for()` to generate URLs from endpoint names
- Implement dynamic routing patterns for REST APIs
- Understand the difference between routes and endpoints
- Debug routing issues using `flask routes` and app.url_map

## What Is Routing?

**Routing** is the process of mapping an incoming HTTP request URL to the Python function (called a **view function**) that handles it. It is the first step in processing any request after it arrives at the WSGI server.

```mermaid
graph LR
    A[HTTP Request<br/>GET /users/123] --> B[URL Router]
    B --> C{Match URL rules}
    C -->|/users/<int:id>| D[View Function<br/>get_user(id)]
    C -->|No match| E[404 Not Found]
    C -->|Wrong method| F[405 Method Not Allowed]
```

## The `@app.route()` Decorator

Flask's primary routing mechanism is the `route()` decorator:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About this site'
```

The decorator registers the function with Flask's URL map. Internally, Flask creates a `Rule` object and adds it to Werkzeug's `Map`:

```python
# What @app.route('/') does internally (simplified):
rule = Rule('/', endpoint='index', methods=['GET'])
app.url_map.add(rule)
```

### How the Decorator Works

The `route()` decorator is a method on the Flask app instance. It takes a URL pattern and optional parameters, creates a `Rule`, and returns a decorator that registers the function:

```python
class Flask:
    def route(self, rule, **options):
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator
```

The `add_url_rule()` method is the lower-level API that actually creates the mapping. You can use it directly instead of the decorator:

```python
def index():
    return 'Hello, World!'

app.add_url_rule('/', view_func=index)
```

Both approaches produce the same result. The decorator is more common and more readable.

## Variable Rules

URL patterns can contain **variable sections** marked with `<>`:

```python
@app.route('/user/<username>')
def show_user(username):
    return f'User: {username}'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    return f'Post #{post_id}'
```

Variable sections capture parts of the URL and pass them to the view function as keyword arguments.

### Built-in Converters

Flask provides several built-in converters:

| Converter | Example | Matches | Python Type |
|-----------|---------|---------|-------------|
| `string` (default) | `<name>` | Any text without slashes | `str` |
| `int` | `<int:age>` | Positive integers | `int` |
| `float` | `<float:price>` | Positive floats | `float` |
| `path` | `<path:filepath>` | Text including slashes | `str` |
| `uuid` | `<uuid:identifier>` | UUID strings | `uuid.UUID` |

```python
@app.route('/files/<path:filepath>')
def show_file(filepath):
    # filepath can contain slashes: 'docs/manual.pdf'
    return f'File: {filepath}'

@app.route('/item/<uuid:item_id>')
def show_item(item_id):
    # item_id is a uuid.UUID object
    return f'Item: {item_id}'
```

### Custom Converters

You can create custom converters by subclassing `BaseConverter`:

```python
from werkzeug.routing import BaseConverter

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super().__init__(url_map)
        self.regex = items[0]

class DateConverter(BaseConverter):
    """Matches dates in YYYY-MM-DD format."""
    regex = r'\d{4}-\d{2}-\d{2}'
    
    def to_python(self, value):
        from datetime import datetime
        return datetime.strptime(value, '%Y-%m-%d').date()
    
    def to_url(self, value):
        return value.strftime('%Y-%m-%d')

app.url_map.converters['date'] = DateConverter

@app.route('/events/<date:event_date>')
def show_events(event_date):
    # event_date is a datetime.date object
    return f'Events on {event_date}'
```

Custom converters must implement:
- `regex`: The regular expression pattern to match
- `to_python(value)`: Convert the URL string to a Python object
- `to_url(value)`: Convert a Python object back to a URL string (for `url_for()`)

## URL Rules and Patterns

### Static Routes

```python
@app.route('/')
def index():
    return 'Home'

@app.route('/about')
def about():
    return 'About'
```

Static routes match exact paths. They are the simplest and most efficient type of route.

### Routes with Multiple Variables

```python
@app.route('/users/<int:user_id>/posts/<int:post_id>')
def show_user_post(user_id, post_id):
    return f'User {user_id}, Post {post_id}'
```

Variables can appear anywhere in the URL. Flask passes them as keyword arguments to the view function.

### Optional Routes

You can register multiple rules for the same view function:

```python
@app.route('/profile/')
@app.route('/profile/<username>')
def profile(username=None):
    if username is None:
        return 'Your own profile'
    return f'Profile of {username}'
```

Both `/profile/` and `/profile/john` will call the same function.

### Trailing Slashes

Flask has specific behavior regarding trailing slashes:

```python
@app.route('/projects/')   # With trailing slash
def projects():
    return 'Projects list'
```

- `/projects/` → matches (200 OK)
- `/projects` → Flask redirects to `/projects/` (308 Permanent Redirect)

```python
@app.route('/about')       # Without trailing slash
def about():
    return 'About'
```

- `/about` → matches (200 OK)
- `/about/` → 404 Not Found

> [!TIP]
> Be consistent. Either always use trailing slashes or never use them. The Flask convention is to use trailing slashes for "folder-like" routes (index/listing pages) and no trailing slash for "file-like" routes (detail pages).

## HTTP Methods

By default, routes only respond to GET (and HEAD). You can specify which methods a route accepts:

```python
@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        return create_user()
    return list_users()
```

Or use method-specific decorators (Flask 2.0+):

```python
@app.get('/users')
def list_users():
    return 'List of users'

@app.post('/users')
def create_user():
    return 'User created', 201

@app.put('/users/<int:user_id>')
def update_user(user_id):
    return f'User {user_id} updated'

@app.delete('/users/<int:user_id>')
def delete_user(user_id):
    return f'User {user_id} deleted', 204
```

These are cleaner and more explicit. Always prefer method-specific decorators when the route handles only one method.

## Endpoints and `url_for()`

Every route has an **endpoint** — an internal name used to refer to the route. By default, the endpoint is the function name:

```python
@app.route('/')
def index():          # endpoint = 'index'
    return 'Home'

@app.route('/hello')
def hello():          # endpoint = 'hello'
    return 'Hello!'
```

You can specify a custom endpoint:

```python
@app.route('/home', endpoint='homepage')
def index():
    return 'Home'
```

### Reverse URL Building

`url_for()` generates URLs from endpoint names. This decouples your URLs from your code:

```python
from flask import url_for

@app.route('/')
def index():
    # url_for('profile', username='john') → '/profile/john'
    user_link = url_for('profile', username='john')
    return f'<a href="{user_link}">John\'s profile</a>'

@app.route('/profile/<username>')
def profile(username):
    return f'Profile of {username}'
```

Benefits of `url_for()`:
- **URL changes are painless**: Change the route path in one place
- **Automatic URL escaping**: Special characters are handled correctly
- **Query parameters**: Extra kwargs become query parameters
- **Blueprints**: Handles blueprint URL prefixes automatically

```python
url_for('profile', username='john doe')
# '/profile/john%20doe'  (properly URL-encoded)

url_for('profile', username='john', tab='settings')
# '/profile/john?tab=settings'

url_for('profile', username='john', _external=True)
# 'http://localhost:5000/profile/john'  (absolute URL)

url_for('profile', username='john', _anchor='bio')
# '/profile/john#bio'
```

## The URL Map

Flask stores all routes in `app.url_map`, a Werkzeug `Map` object. You can inspect it:

```python
>>> print(app.url_map)
Map([<Rule '/' (HEAD, OPTIONS, GET) -> index>,
 <Rule '/static/<filename>' (HEAD, OPTIONS, GET) -> static>,
 <Rule '/profile/<username>' (HEAD, OPTIONS, GET) -> profile>,
 <Rule '/users' (POST, OPTIONS, GET) -> users>])
```

The `flask routes` CLI command also shows all registered routes:

```bash
$ flask routes
Endpoint    Methods    Rule
----------  ---------  ---------------------------
index       GET        /
profile     GET        /profile/<username>
users       GET, POST  /users
static      GET        /static/<path:filename>
```

## URL Building in Templates

Use `url_for()` in Jinja2 templates to generate URLs:

```html
<a href="{{ url_for('index') }}">Home</a>
<a href="{{ url_for('profile', username='john') }}">John</a>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
```

This is the recommended way to create links in Flask templates. Never hardcode URLs.

## Route Defaults

You can provide default values for route arguments:

```python
@app.route('/greet/')
@app.route('/greet/<name>')
def greet(name='World'):
    return f'Hello, {name}!'
```

Or specify defaults in the decorator:

```python
@app.route('/page/', defaults={'page_num': 1})
@app.route('/page/<int:page_num>')
def show_page(page_num):
    return f'Page {page_num}'
```

## Route Ordering and Specificity

Flask matches routes in the order they are defined. More specific routes should come before less specific ones:

```python
# Correct order
@app.route('/users/new')
def new_user():
    return 'New user form'

@app.route('/users/<int:user_id>')
def show_user(user_id):
    return f'User {user_id}'

# WRONG order — /users/new would match /users/<int:user_id> first!
@app.route('/users/<int:user_id>')   # Matches /users/new as user_id='new'
def show_user(user_id):
    ...

@app.route('/users/new')
def new_user():
    ...
```

> [!WARNING]
> If `/users/new` is defined after `/users/<int:user_id>`, a request to `/users/new` will match the variable route first (trying to parse 'new' as an integer, which fails, resulting in a 404). Always order static routes before dynamic ones.

## Request Hooks

Flask provides hooks that run before and after requests:

```python
@app.before_request
def before_request():
    """Runs before each request."""
    g.request_start_time = time.time()

@app.after_request
def after_request(response):
    """Runs after each request. Can modify the response."""
    duration = time.time() - g.request_start_time
    response.headers['X-Request-Duration'] = str(duration)
    return response

@app.teardown_request
def teardown_request(exception=None):
    """Runs after each request, even if an exception occurred."""
    # Clean up resources (close database connections, etc.)
    pass

@app.context_processor
def inject_globals():
    """Inject variables into all templates."""
    return {'app_name': 'My Flask App'}
```

## Subdomain Routing

Flask supports subdomain-based routing:

```python
app.config['SERVER_NAME'] = 'example.com'

@app.route('/', subdomain='<user>')
def user_home(user):
    return f'Welcome to {user}.example.com'

@app.route('/', subdomain='api')
def api_home():
    return 'API endpoint'
```

This enables multi-tenant applications where each user gets their own subdomain.

## Common Mistakes

**Mistake: Hardcoding URLs in templates**
Always use `url_for()` instead of hardcoded paths. When you change a route, `url_for()` handles the update automatically.

**Mistake: Wrong route order**
Static routes must be defined before dynamic routes that could match the same path.

**Mistake: Forgetting to specify methods**
POST-only routes without `methods=['POST']` return 405 Method Not Allowed.

**Mistake: Using the same endpoint name for multiple routes**
Each endpoint must be unique. Flask will raise an AssertionError if you reuse endpoint names.

## Best Practices

- Use method-specific decorators (`@app.get()`, `@app.post()`) for clarity
- Always use `url_for()` instead of hardcoded URLs
- Order static routes before dynamic routes
- Use meaningful endpoint names
- Keep URL patterns RESTful and predictable
- Use converters to validate and type-cast URL parameters

## Exercises

1. **CRUD Routes**: Define complete CRUD routes for a `Post` resource using RESTful conventions.

2. **Custom Converter**: Create a converter that matches hexadecimal color codes (`#RRGGBB`) and converts them to RGB tuples.

3. **URL Generator**: Write a helper function that generates navigation links using `url_for()` for all routes in an application.

4. **Route Inspector**: Write a script that reads `app.url_map` and outputs a table of all routes, methods, and endpoints.

## Quiz

**Question 1**: What is the difference between a route and an endpoint in Flask?

**Question 2**: How does Flask handle a request to `/projects` when the route is defined as `/projects/`?

**Question 3**: Why should you use `url_for()` instead of hardcoding URLs?

**Question 4**: What happens if you define `/users/<int:id>` before `/users/new`?

**Question 5**: Explain the purpose of `before_request` and `after_request` hooks.

## Interview Questions

1. "How does Flask's routing system work internally?"

2. "What is the difference between `@app.route()` and `app.add_url_rule()`?"

3. "How would you implement a route that accepts both `/profile` and `/profile/<username>`?"

4. "Explain `url_for()` and why it is preferred over hardcoded URLs."

5. "How would you create a custom URL converter in Flask?"

6. "What happens when multiple routes could match the same URL?"

## Related Chapters

- Previous: [[01-Flask-Core/Flask-Architecture]]
- Next: [[01-Flask-Core/URL-Converters]]
- [[01-Flask-Core/Request-Response]] — Handling requests and responses
- [[06-Blueprints/Blueprints]] — Organizing routes with blueprints

## Official Documentation References

- [Flask Routing Documentation](https://flask.palletsprojects.com/en/latest/quickstart/#routing)
- [Flask URL Building](https://flask.palletsprojects.com/en/latest/quickstart/#url-building)
- [Werkzeug Routing Documentation](https://werkzeug.palletsprojects.com/en/latest/routing/)
- [Flask Request Hooks](https://flask.palletsprojects.com/en/latest/api/#flask.Flask.before_request)

---

*Previous: [[01-Flask-Core/Flask-Architecture]] | Next: [[01-Flask-Core/URL-Converters]]*