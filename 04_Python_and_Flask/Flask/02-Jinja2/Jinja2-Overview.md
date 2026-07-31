---
title: Jinja2 Overview
description: Flask's template engine — syntax, variables, control structures, and integration patterns
chapter: 02-Jinja2
tags:
  - jinja2
  - templates
  - syntax
  - rendering
  - flask
difficulty: Beginner
prerequisites:
  - [[01-Flask-Core/Templates]]
---

# Jinja2 Overview

> Jinja2 is Flask's template engine. It transforms templates (HTML with special syntax) into rendered output by combining them with Python data. Understanding Jinja2 thoroughly — its syntax, features, and security model — is essential for building any Flask application that renders HTML.

## Learning Objectives

After completing this chapter, you will be able to:

- Write Jinja2 templates using all core syntax elements
- Pass data from Flask views to templates and access it
- Use template inheritance for consistent page layouts
- Apply filters, tests, and global functions in templates
- Understand autoescaping and write XSS-safe templates
- Configure Jinja2 for optimal performance

## What Is Jinja2?

Jinja2 is a modern, designer-friendly template engine for Python. It was created by Armin Ronacher (the creator of Flask) and is modeled after Django's template engine but with more flexibility and a more powerful expression syntax.

Key features:
- **Sandboxed execution**: Templates cannot execute arbitrary Python code
- **Autoescaping**: Automatically escapes HTML to prevent XSS
- **Template inheritance**: Build base templates that child templates extend
- **Custom filters and tests**: Extend template functionality
- **Macros**: Reusable template fragments
- **Fast**: Compiles templates to Python bytecode

## Jinja2 Syntax

Jinja2 uses three types of syntax delimiters:

| Delimiter | Purpose | Example |
|-----------|---------|---------|
| `{{ ... }}` | Expression output | `{{ user.name }}` |
| `{% ... %}` | Statements (logic) | `{% if user %}`, `{% for item in items %}` |
| `{# ... #}` | Comments | `{# This is ignored #}` |

### Variables

Access Python variables and their attributes:

```html
<p>Hello, {{ name }}!</p>
<p>User: {{ user.name }}</p>
<p>Email: {{ user['email'] }}</p>  {# Dict-style access #}
<p>List item: {{ items[0] }}</p>
```

### Filters

Transform values with the pipe operator:

```html
<p>{{ name|upper }}</p>           {# Uppercase #}
<p>{{ name|title }}</p>           {# Title Case #}
<p>{{ name|default('Anonymous') }}</p>
<p>{{ price|round(2) }}</p>       {# Round to 2 decimal places #}
<p>{{ html_content|safe }}</p>    {# Mark as safe HTML #}
<p>{{ items|length }}</p>         {# Count items #}
<p>{{ items|join(', ') }}</p>     {# Join with separator #}
<p>{{ created_at|datetimeformat('%Y-%m-%d') }}</p>
```

Filters can be chained:

```html
<p>{{ name|trim|title }}</p>
```

### Tests

Check conditions with the `is` operator:

```html
{% if user is defined %}
    <p>User exists</p>
{% endif %}

{% if items is not none and items is iterable %}
    <p>Has {{ items|length }} items</p>
{% endif %}

{% if number is divisibleby 3 %}
    <p>Divisible by 3</p>
{% endif %}
```

## Control Structures

### Conditionals

```html
{% if user.is_admin %}
    <a href="/admin">Admin Panel</a>
{% elif user.is_moderator %}
    <a href="/moderate">Moderation</a>
{% else %}
    <p>Standard user</p>
{% endif %}
```

Inline conditionals:

```html
<p>Status: {{ 'Active' if user.active else 'Inactive' }}</p>
```

### Loops

```html
{% for post in posts %}
    <article>
        <h2>{{ post.title }}</h2>
        <p>{{ post.summary }}</p>
    </article>
{% else %}
    <p>No posts found.</p>
{% endfor %}
```

Loop variables:

```html
{% for post in posts %}
    <p>{{ loop.index }}: {{ post.title }}</p>       {# 1-based index #}
    <p>{{ loop.index0 }}: {{ post.title }}</p>      {# 0-based index #}
    <p>{{ loop.first }}: First iteration</p>         {# Boolean #}
    <p>{{ loop.last }}: Last iteration</p>           {# Boolean #}
    <p>{{ loop.revindex }}: From end (1-based)</p>   {# Reverse index #}
{% endfor %}
```

### Set Variable

```html
{% set title = 'My Page' %}
{% set nav_items = [('Home', '/'), ('About', '/about')] %}
```

### Include

Include another template:

```html
{% include 'partials/navbar.html' %}

{# Include with context #}
{% include 'partials/sidebar.html' with context %}

{# Include without context #}
{% include 'partials/header.html' without context %}
```

### Macros

Reusable template functions:

```html
{% macro input(name, type='text', value='', placeholder='') %}
    <input type="{{ type }}" name="{{ name }}" 
           value="{{ value }}" placeholder="{{ placeholder }}">
{% endmacro %}

{% macro textarea(name, rows=4, cols=50) %}
    <textarea name="{{ name }}" rows="{{ rows }}" cols="{{ cols }}"></textarea>
{% endmacro %}

{# Usage #}
{{ input('username', placeholder='Enter username') }}
{{ input('password', type='password') }}
{{ textarea('bio', rows=6) }}
```

Macros with caller (content blocks):

```html
{% macro modal(title) %}
<div class="modal">
    <div class="modal-header">
        <h3>{{ title }}</h3>
        <button class="close">&times;</button>
    </div>
    <div class="modal-body">
        {{ caller() }}
    </div>
</div>
{% endmacro %}

{% call modal('Confirm Delete') %}
    <p>Are you sure you want to delete this item?</p>
    <button>Delete</button>
{% endcall %}
```

## Template Inheritance

Template inheritance is Jinja2's most powerful feature. Define a base template with blocks that child templates can override.

### Base Template

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Default Title{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <header>
        {% block header %}
        <nav>
            <a href="{{ url_for('index') }}">Home</a>
            {% block nav %}{% endblock %}
        </nav>
        {% endblock %}
    </header>
    
    <main>
        {% block content %}
        <p>Default content goes here.</p>
        {% endblock %}
    </main>
    
    <footer>
        {% block footer %}
        <p>&copy; 2024 My App</p>
        {% endblock %}
    </footer>
    
    <script src="{{ url_for('static', filename='app.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Child Template

```html
<!-- templates/page.html -->
{% extends "base.html" %}

{% block title %}About Us - My App{% endblock %}

{% block content %}
    <h1>About Us</h1>
    <p>We are a company that builds things.</p>
{% endblock %}
```

### super() — Parent Block Content

Access the parent block's content:

```html
{% block content %}
    <div class="wrapper">
        {{ super() }}  {# Includes parent's content #}
    </div>
{% endblock %}
```

### Named endblock

```html
{% block content %}
    <p>Content here</p>
{% endblock content %}  {# More readable for complex templates #}
```

## Autoescaping

Jinja2 autoescaping is enabled by default in Flask. Special HTML characters are escaped:

```html
<!-- If user_input = '<script>alert("XSS")</script>' -->
<p>{{ user_input }}</p>
<!-- Output: &lt;script&gt;alert("XSS")&lt;/script&gt; -->
```

### Marking Content as Safe

For trusted HTML content:

```html
<!-- In template -->
<p>{{ trusted_html|safe }}</p>

<!-- In Python -->
from markupsafe import Markup
html = Markup('<strong>Bold</strong>')
```

> [!WARNING]
> Never mark user input as safe. This creates XSS vulnerabilities. Only mark content you control completely — like rendered Markdown from a trusted admin.

### Raw Blocks

Disable escaping for a block:

```html
{% raw %}
    <p>This {{ will }} not be processed by Jinja2</p>
{% endraw %}
```

## Flask-Specific Features

### Automatic Globals

Flask automatically makes these available in all templates:

```html
<a href="{{ url_for('index') }}">Home</a>

{% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
        <div class="flash {{ category }}">{{ message }}</div>
    {% endfor %}
{% endwith %}

<p>Config value: {{ config['APP_NAME'] }}</p>
<p>Request path: {{ request.path }}</p>
<p>User ID: {{ session.user_id }}</p>
```

### tojson Filter

Serialize Python data for JavaScript:

```html
<script>
    const userData = {{ user.to_dict()|tojson }};
    console.log(userData.name);
</script>
```

This is safe — the filter properly escapes the JSON for HTML context.

## Whitespace Control

Control whitespace around tags:

```html
{# Strip whitespace before/after tag #}
{% for item in items -%}
    {{ item }}
{%- endfor %}

{# Global config #}
app.jinja_env.trim_blocks = True    # Remove first newline after tag
app.jinja_env.lstrip_blocks = True  # Strip leading whitespace
```

## Common Mistakes

**Mistake: Logic in templates**
Keep business logic in Python. Templates should handle presentation only.

**Mistake: Disabling autoescaping globally**
Never set `autoescape=False`. Use `|safe` for specific trusted content only.

**Mistake: Forgetting to quote string literals**
```html
{# Wrong #}
{% if role == admin %}  {# admin is treated as a variable #}

{# Correct #}
{% if role == 'admin' %}
```

**Mistake: Modifying lists in templates**
Templates should not modify data. Do that in the view function.

## Best Practices

- Use template inheritance from the start — create a `base.html`
- Keep templates focused on presentation — no complex logic
- Use `url_for()` for all internal links
- Never mark user input as safe without sanitization
- Use macros for repeated UI patterns
- Use `super()` to extend parent blocks without replacing them
- Use `set` to simplify complex expressions
- Use `include` for reusable template fragments

## Exercises

1. **Base Template**: Create a `base.html` with blocks for title, navigation, content, footer, CSS, and JavaScript.

2. **Macro Library**: Create a macros file with reusable components: form input, button, alert message, and pagination.

3. **Conditional Layout**: Create a template that shows different layouts for authenticated vs. anonymous users.

4. **Data Table**: Create a template that renders a sortable HTML table from a list of dictionaries.

## Quiz

**Question 1**: What are the three Jinja2 delimiter types and their purposes?

**Question 2**: How does template inheritance work? What is the purpose of `{% block %}`?

**Question 3**: What is autoescaping, and why is it important?

**Question 4**: How do you safely pass Python data to JavaScript in a template?

**Question 5**: What is the difference between `{% include %}` and `{% extends %}`?

## Interview Questions

1. "Explain Jinja2 template inheritance. How would you structure templates for a multi-page Flask app?"

2. "What is autoescaping, and how does it prevent XSS?"

3. "How would you create reusable template components in Jinja2?"

4. "What are Jinja2 macros, and when would you use them?"

5. "How do you pass data from a Flask view to a Jinja2 template?"

## Related Chapters

- [[02-Jinja2/Template-Inheritance]] — Advanced inheritance patterns
- [[02-Jinja2/Filters]] — Built-in and custom filters
- [[02-Jinja2/Macros]] — Advanced macro usage
- [[02-Jinja2/Custom-Filters]] — Creating custom filters
- [[02-Jinja2/Context-Processors]] — Injecting template globals

## Official Documentation References

- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Jinja2 Template Designer Documentation](https://jinja.palletsprojects.com/en/latest/templates/)
- [Flask Templating](https://flask.palletsprojects.com/en/latest/templating/)

---

*Previous: [[01-Flask-Core/Static-Files]]*