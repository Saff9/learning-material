---
title: Templates
description: How Flask renders HTML using Jinja2 — template inheritance, rendering patterns, and context
chapter: 01-Flask-Core
tags:
  - templates
  - jinja2
  - html
  - render_template
  - static-files
  - core
difficulty: Beginner
prerequisites:
  - [[01-Flask-Core/Application-Context]]
  - [[00-Foundations/Web-Technologies]]
---

# Templates

> Flask does not generate HTML directly in Python strings. Instead, it uses Jinja2 — a powerful template engine that separates presentation from logic. Understanding how Flask integrates with Jinja2 enables you to build maintainable, secure web interfaces.

## Learning Objectives

After completing this chapter, you will be able to:

- Explain how Flask integrates with Jinja2 for HTML generation
- Use `render_template()` and `render_template_string()` correctly
- Understand template inheritance and include patterns
- Pass data from view functions to templates
- Use template globals and context processors
- Configure Jinja2 options in Flask
- Understand autoescaping and XSS prevention in templates

## Flask and Jinja2

Flask includes Jinja2 by default. When you create a Flask app, it automatically creates a Jinja2 environment configured with:

- **Autoescaping**: Enabled for HTML and XML templates (XSS protection)
- **Template folders**: Looks for templates in the `templates/` directory
- **Globals**: `url_for()`, `get_flashed_messages()`, `config`, `request`, `session`, `g`
- **Filters**: Custom Flask filters like `tojson`, `safe`

## The `render_template()` Function

```python
from flask import render_template

@app.route('/hello/<name>')
def hello(name):
    return render_template('hello.html', name=name, title='Greeting')
```

Flask looks for `templates/hello.html` and renders it with the provided context:

```html
<!-- templates/hello.html -->
<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body>
    <h1>Hello, {{ name }}!</h1>
</body>
</html>
```

### Template Search Path

Flask searches for templates in:
1. The `templates/` folder in your application package
2. The `templates/` folder in each registered blueprint

```
myapp/
    __init__.py
    templates/
        base.html
        hello.html
    auth/
        templates/
            auth/
                login.html
                register.html
```

Blueprint templates must be namespaced (placed in a subfolder matching the blueprint name) to avoid conflicts.

### `render_template_string()`

For inline templates (use sparingly — prefer separate files):

```python
from flask import render_template_string

@app.route('/simple')
def simple():
    name = 'World'
    return render_template_string('<h1>Hello, {{ name }}!</h1>', name=name)
```

> [!WARNING]
> Never use `render_template_string()` with user-provided template strings. This enables **Server-Side Template Injection (SSTI)** — a critical vulnerability where users can execute arbitrary Python code.

## Template Context

Variables passed to `render_template()` become available in the template:

```python
@app.route('/user/<int:user_id>')
def show_user(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(author=user).all()
    return render_template('user.html', user=user, posts=posts)
```

```html
<!-- templates/user.html -->
<h1>{{ user.name }}</h1>
<p>{{ user.bio }}</p>

<h2>Posts ({{ posts|length }})</h2>
{% for post in posts %}
    <article>
        <h3>{{ post.title }}</h3>
        <p>{{ post.summary }}</p>
    </article>
{% endfor %}
```

### Automatic Template Globals

Flask automatically injects these into every template:

| Variable | Description |
|----------|-------------|
| `url_for` | Generates URLs for endpoints |
| `get_flashed_messages` | Retrieves flashed messages |
| `config` | Current app configuration (read-only) |
| `request` | Current request object |
| `session` | Current session |
| `g` | Request-scoped storage |

```html
<nav>
    <a href="{{ url_for('index') }}">Home</a>
    {% if session.user_id %}
        <a href="{{ url_for('profile') }}">{{ g.current_user.name }}</a>
    {% else %}
        <a href="{{ url_for('login') }}">Login</a>
    {% endif %}
</nav>

{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="flash {{ category }}">{{ message }}</div>
        {% endfor %}
    {% endif %}
{% endwith %}
```

## Template Inheritance

Template inheritance is the most powerful Jinja2 feature. It allows you to define a base template with blocks that child templates can override.

### Base Template

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <header>
        <nav>
            <a href="{{ url_for('index') }}">Home</a>
            {% block nav %}{% endblock %}
        </nav>
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>&copy; 2024 My App</p>
    </footer>
    
    {% block scripts %}{% endblock %}
</body>
</html>
```

### Child Template

```html
<!-- templates/about.html -->
{% extends "base.html" %}

{% block title %}About - My App{% endblock %}

{% block content %}
    <h1>About</h1>
    <p>This is my Flask application.</p>
{% endblock %}
```

The child template extends `base.html` and fills in the `content` block. All other blocks (`title`, `extra_css`, `nav`, `scripts`) keep their default values.

> [!TIP]
> Always use template inheritance from the start of your project. Define a `base.html` with blocks for title, content, CSS, and JavaScript. Every page template extends it.

## Context Processors

Context processors inject variables into all templates automatically:

```python
@app.context_processor
def inject_globals():
    return {
        'app_name': 'My Flask App',
        'current_year': datetime.now().year,
        'format_date': lambda d: d.strftime('%B %d, %Y')
    }
```

Now all templates can use `{{ app_name }}`, `{{ current_year }}`, and `{{ format_date(post.created_at) }}`.

Context processors run on every template render, so keep them lightweight. For expensive computations, use `g` in a `before_request` hook instead.

## Template Filters

Flask provides several built-in filters:

| Filter | Example | Output |
|--------|---------|--------|
| `safe` | `{{ html\|safe }}` | Marks string as safe HTML (do not escape) |
| `tojson` | `{{ data\|tojson }}` | Serializes to JSON string |
| `escape` | `{{ text\|escape }}` | Escapes HTML entities |

```html
<!-- Safe HTML (e.g., from a rich text editor) -->
<div>{{ article.body|safe }}</div>

<!-- JSON for JavaScript -->
<script>
    const userData = {{ current_user.to_dict()|tojson }};
</script>
```

> [!WARNING]
> Only use `|safe` on content you trust completely. Using it on user input creates an XSS vulnerability.

## Autoescaping and XSS Prevention

Jinja2 **autoescaping** is enabled by default in Flask. All template variables are automatically escaped:

```python
user_input = '<script>alert("XSS")</script>'
```

```html
<!-- Rendered as text, not executed -->
<p>{{ user_input }}</p>
<!-- Output: &lt;script&gt;alert("XSS")&lt;/script&gt; -->
```

This prevents **Cross-Site Scripting (XSS)** attacks where attackers inject malicious scripts.

To disable escaping for trusted content:

```html
<!-- Mark a string as safe (trusted HTML) -->
{{ trusted_html|safe }}

<!-- Use the Markup class in Python -->
from markupsafe import Markup
html = Markup('<strong>Bold</strong>')
```

> [!WARNING]
> Never mark user input as safe. If you must render user-provided HTML, sanitize it first with a library like Bleach or nh3.

## Flash Messages

Flash messages are one-time notifications stored in the session and displayed on the next page load:

```python
from flask import flash, redirect, url_for

@app.route('/login', methods=['POST'])
def login():
    # ... validate credentials ...
    flash('Welcome back!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_item(id):
    # ... delete item ...
    flash('Item deleted successfully.', 'info')
    return redirect(url_for('index'))
```

In templates:

```html
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        <div class="flash-messages">
            {% for category, message in messages %}
                <div class="flash flash-{{ category }}">
                    {{ message }}
                </div>
            {% endfor %}
        </div>
    {% endif %}
{% endwith %}
```

Flash categories (arbitrary strings, commonly):
- `success` — Positive feedback
- `error` / `danger` — Something went wrong
- `warning` — Caution needed
- `info` — Neutral information

## Configuring Jinja2

You can customize Jinja2 through Flask's configuration:

```python
app = Flask(__name__)

# Auto-reload templates in development
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Custom Jinja2 options
app.jinja_options = {
    'trim_blocks': True,        # Remove first newline after a block
    'lstrip_blocks': True,      # Strip leading whitespace
    'newline_sequence': '\n',   # Use Unix line endings
}

# Add custom filters
@app.template_filter('format_currency')
def format_currency(amount):
    return f'${amount:,.2f}'

# Usage: {{ price|format_currency }}
```

## Template Caching

In production, Flask caches compiled templates. The cache is automatically cleared on code reload in debug mode. You can control caching:

```python
app.config['EXPLAIN_TEMPLATE_LOADING'] = True  # Debug template search
```

## Common Mistakes

**Mistake: Using `render_template_string()` with user input**
This creates a Server-Side Template Injection vulnerability. Always use `render_template()` with file-based templates.

**Mistake: Disabling autoescaping globally**
Never set `autoescape=False` globally. Use `|safe` for specific trusted content.

**Mistake: Putting business logic in templates**
Templates should handle presentation only. Complex logic belongs in view functions or model methods.

**Mistake: Hardcoding URLs**
Always use `url_for()` in templates. Hardcoded URLs break when routes change.

## Best Practices

- Use template inheritance from the start — define a `base.html`
- Keep templates focused on presentation — no business logic
- Use `url_for()` for all internal links
- Never mark user input as safe without sanitization
- Use context processors for globally needed template variables
- Use flash messages for user feedback after form submissions
- Organize templates in subdirectories by feature

## Exercises

1. **Base Template**: Create a `base.html` template with blocks for title, content, navigation, CSS, and JavaScript. Create three child templates that extend it.

2. **Flash Messages**: Implement a login form that flashes success and error messages. Style the messages differently based on category.

3. **Context Processor**: Create a context processor that injects the current time and a navigation menu into all templates.

4. **Custom Filter**: Write a custom Jinja2 filter that formats dates as "2 hours ago", "yesterday", etc. (relative time).

## Quiz

**Question 1**: What is the difference between `render_template()` and `render_template_string()`? When would you use each?

**Question 2**: How does template inheritance work in Jinja2? What is the purpose of `{% block %}`?

**Question 3**: What is autoescaping, and why is it important for security?

**Question 4**: How do context processors work? When should you use them?

**Question 5**: What is the correct way to display trusted HTML in a Jinja2 template?

## Interview Questions

1. "How does Flask integrate with Jinja2? What Jinja2 features are most important for Flask development?"

2. "Explain template inheritance. How would you structure templates for a multi-page Flask application?"

3. "What is autoescaping, and how does it prevent XSS attacks?"

4. "How do flash messages work in Flask? How do you display them in templates?"

5. "What is a context processor? Give an example of when you would use one."

6. "A developer uses `{{ user_input|safe }}` on untrusted user content. What vulnerability does this create?"

## Related Chapters

- Previous: [[01-Flask-Core/Application-Context]]
- Next: [[01-Flask-Core/Error-Handling]]
- [[02-Jinja2/Jinja2-Overview]] — Deep dive into Jinja2
- [[02-Jinja2/Template-Inheritance]] — Advanced inheritance patterns
- [[08-Security/XSS-Prevention]] — XSS security details

## Official Documentation References

- [Flask Templates](https://flask.palletsprojects.com/en/latest/quickstart/#rendering-templates)
- [Flask Template Inheritance](https://flask.palletsprojects.com/en/latest/patterns/templateinheritance/)
- [Flask Context Processors](https://flask.palletsprojects.com/en/latest/templating/#context-processors)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)

---

*Previous: [[01-Flask-Core/Application-Context]] | Next: [[01-Flask-Core/Error-Handling]]*