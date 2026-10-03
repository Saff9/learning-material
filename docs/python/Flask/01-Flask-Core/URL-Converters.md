---
title: URL Converters
description: Built-in and custom URL converters for type-safe route parameters in Flask
chapter: 01-Flask-Core
tags:
  - url-converters
  - routing
  - werkzeug
  - custom-converters
  - type-safety
  - core
difficulty: Intermediate
prerequisites:
  - [[01-Flask-Core/Routing]]
---

# URL Converters

> URL converters transform URL path segments into typed Python objects. They provide type safety, input validation, and clean URL handling. Understanding built-in converters and how to create custom ones is essential for building robust Flask routing.

## Learning Objectives

After completing this chapter, you will be able to:

- Use all built-in URL converters (string, int, float, path, uuid)
- Create custom converters for domain-specific types
- Understand converter registration and the converter API
- Implement validation logic in custom converters
- Choose the right converter for each URL parameter

## Built-in Converters

Flask provides five built-in converters:

### `string` (Default)

Matches any text except slashes. This is the default when no converter is specified.

```python
@app.route('/user/<username>')           # Same as <string:username>
def show_user(username):
    # username is a string
    return f'User: {username}'
```

Pattern: `[^/]+`

### `int`

Matches positive integers. Zero is allowed.

```python
@app.route('/post/<int:post_id>')
def show_post(post_id):
    # post_id is an int
    return f'Post #{post_id}'

# /post/123     → post_id = 123 (int)
# /post/abc     → 404 Not Found
# /post/-1      → 404 Not Found
# /post/0123    → post_id = 123 (leading zeros stripped)
```

Pattern: `\d+`

### `float`

Matches positive floating-point numbers.

```python
@app.route('/price/<float:amount>')
def show_price(amount):
    # amount is a float
    return f'Price: ${amount:.2f}'

# /price/19.99  → amount = 19.99 (float)
# /price/20     → 404 Not Found (must have decimal)
# /price/abc    → 404 Not Found
```

Pattern: `\d+\.\d+`

> [!NOTE]
> The `float` converter requires a decimal point. `20` does not match — use `20.0` or stick with the `string` converter and parse manually.

### `path`

Like `string` but accepts slashes. Useful for file paths or nested resources.

```python
@app.route('/files/<path:filepath>')
def show_file(filepath):
    # filepath can contain slashes
    return f'File: {filepath}'

# /files/docs/manual.pdf → filepath = 'docs/manual.pdf'
```

Pattern: `.*` (greedy — consumes all remaining URL segments)

### `uuid`

Matches UUID (Universally Unique Identifier) strings.

```python
import uuid
from flask import jsonify

@app.route('/item/<uuid:item_id>')
def show_item(item_id):
    # item_id is a uuid.UUID object
    return jsonify({'item_id': str(item_id)})

# /item/12345678-1234-5678-1234-567812345678 → UUID object
# /item/not-a-uuid → 404 Not Found
```

Pattern: `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}`

### Converter Summary

| Converter | Pattern | Python Type | Slashes? | Example |
|-----------|---------|-------------|----------|---------|
| `string` | `[^/]+` | `str` | No | `hello`, `user-name` |
| `int` | `\d+` | `int` | No | `123`, `0` |
| `float` | `\d+\.\d+` | `float` | No | `3.14`, `100.0` |
| `path` | `.*` | `str` | Yes | `a/b/c` |
| `uuid` | UUID regex | `uuid.UUID` | No | `550e8400-e29b-41d4-a716-446655440000` |

## Custom Converters

Create custom converters by subclassing `werkzeug.routing.BaseConverter`.

### Basic Custom Converter

```python
from werkzeug.routing import BaseConverter

class DateConverter(BaseConverter):
    """Matches dates in YYYY-MM-DD format."""
    
    regex = r'\d{4}-\d{2}-\d{2}'
    
    def to_python(self, value):
        """Convert URL string to Python object."""
        from datetime import datetime
        return datetime.strptime(value, '%Y-%m-%d').date()
    
    def to_url(self, value):
        """Convert Python object back to URL string."""
        return value.strftime('%Y-%m-%d')

# Register the converter
app.url_map.converters['date'] = DateConverter

# Use it
@app.route('/events/<date:event_date>')
def show_events(event_date):
    # event_date is a datetime.date object
    events = Event.query.filter_by(date=event_date).all()
    return render_template('events.html', events=events, date=event_date)

# URL generation works both ways
url_for('show_events', event_date=date(2024, 7, 15))
# → '/events/2024-07-15'
```

### Enum Converter

```python
from enum import Enum
from werkzeug.routing import BaseConverter

class Color(Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'

class EnumConverter(BaseConverter):
    """Matches enum values."""
    
    def __init__(self, url_map, enum_class):
        super().__init__(url_map)
        self.enum_class = enum_class
        # Build regex from enum values
        values = '|'.join(e.value for e in enum_class)
        self.regex = f'({values})'
    
    def to_python(self, value):
        return self.enum_class(value)
    
    def to_url(self, value):
        if isinstance(value, self.enum_class):
            return value.value
        return str(value)

# Register
app.url_map.converters['color'] = EnumConverter

# Use with a specific enum
@app.route('/theme/<color:theme_color>')
def set_theme(theme_color):
    # theme_color is a Color enum
    return f'Selected theme: {theme_color.value}'
```

### List Converter

```python
class ListConverter(BaseConverter):
    """Matches comma-separated values."""
    
    regex = r'[^/]+(?:,[^/]+)*'
    
    def to_python(self, value):
        return value.split(',')
    
    def to_url(self, values):
        return ','.join(str(v) for v in values)

app.url_map.converters['list'] = ListConverter

@app.route('/tags/<list:tags>')
def show_tags(tags):
    # tags is a list of strings
    # /tags/python,flask,web → ['python', 'flask', 'web']
    posts = Post.query.filter(Post.tags.overlap(tags)).all()
    return render_template('posts.html', posts=posts)
```

### Slug Converter

```python
class SlugConverter(BaseConverter):
    """Matches URL-friendly slugs (lowercase letters, numbers, hyphens)."""
    
    regex = r'[a-z0-9]+(?:-[a-z0-9]+)*'
    
    def to_python(self, value):
        return value.lower()

app.url_map.converters['slug'] = SlugConverter

@app.route('/blog/<slug:post_slug>')
def show_blog_post(post_slug):
    post = Post.query.filter_by(slug=post_slug).first_or_404()
    return render_template('post.html', post=post)

# /blog/hello-world → post_slug = 'hello-world'
# /blog/Hello World → 404 (spaces not allowed)
# /blog/hello_world → 404 (underscores not allowed)
```

## Converter Registration

Register converters in three ways:

### 1. Direct Registration

```python
app.url_map.converters['mytype'] = MyConverter
```

### 2. Multiple Converters

```python
app.url_map.converters.update({
    'date': DateConverter,
    'slug': SlugConverter,
    'list': ListConverter,
})
```

### 3. Using a Blueprint (Limited)

Converters are registered on the app, not blueprints. Register them when creating the app or in a setup function.

## Converter API Reference

```python
class BaseConverter:
    """Base class for all converters."""
    
    regex = '[^/]+'       # Regular expression pattern
    weight = 100           # Priority for URL building (lower = higher priority)
    
    def __init__(self, url_map, *args):
        """Initialize with the URL map and any converter arguments."""
    
    def to_python(self, value):
        """Convert the matched URL string to a Python object.
        
        Called when routing an incoming request.
        Raises ValueError to trigger a 404.
        """
        return value
    
    def to_url(self, value):
        """Convert a Python object to a URL string.
        
        Called when generating URLs with url_for().
        """
        return str(value)
```

## Best Practices

- Use `int` for numeric IDs — it rejects non-numeric input automatically
- Create custom converters for domain-specific types (dates, slugs, enums)
- Keep converter regex patterns efficient — complex regex slows routing
- Always implement `to_url()` for bidirectional URL generation
- Raise `ValueError` in `to_python()` for invalid values (triggers 404)

## Exercises

1. **Date Converter**: Create a converter that matches dates and converts them to `datetime.date` objects.

2. **Hex Color Converter**: Create a converter that matches hex color codes (`#RRGGBB`) and converts them to RGB tuples.

3. **Language Converter**: Create a converter that matches ISO 639-1 language codes (`en`, `es`, `fr`) and converts them to a custom `Language` enum.

4. **URL Generation**: Verify that your custom converters work correctly with `url_for()` in both directions.

## Quiz

**Question 1**: What are the five built-in URL converters in Flask? What does each match?

**Question 2**: Why does the `float` converter not match `20` (without a decimal)?

**Question 3**: What two methods must a custom converter implement, and what do they do?

**Question 4**: How do you register a custom converter with Flask?

**Question 5**: What happens if `to_python()` raises a `ValueError`?

## Interview Questions

1. "What URL converters does Flask provide by default? When would you use each?"

2. "How would you create a custom URL converter for a specific data type?"

3. "Explain the difference between `to_python()` and `to_url()` in a custom converter."

4. "What is the purpose of the `path` converter? How does it differ from `string`?"

## Related Chapters

- Previous: [[01-Flask-Core/Routing]]
- [[01-Flask-Core/Request-Response]] — Handling converted values in view functions

## Official Documentation References

- [Flask Custom Converters](https://flask.palletsprojects.com/en/latest/quickstart/#custom-converters)
- [Werkzeug Routing Documentation](https://werkzeug.palletsprojects.com/en/latest/routing/)

---

*Previous: [[01-Flask-Core/Routing]] | Next: [[01-Flask-Core/Request-Response]]*