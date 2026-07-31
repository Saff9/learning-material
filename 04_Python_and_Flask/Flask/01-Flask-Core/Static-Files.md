---
title: Static Files
description: Serving CSS, JavaScript, images, and other static assets in Flask
chapter: 01-Flask-Core
tags:
  - static-files
  - css
  - javascript
  - assets
  - cache-busting
  - core
difficulty: Beginner
prerequisites:
  - [[01-Flask-Core/Cookies]]
---

# Static Files

> Every web application needs static assets — CSS for styling, JavaScript for interactivity, images for visual content. Flask provides a built-in mechanism for serving static files during development, but understanding how to organize, reference, and optimize these assets is essential for production applications.

## Learning Objectives

After completing this chapter, you will be able to:

- Serve static files using Flask's built-in static file endpoint
- Reference static files correctly in templates and Python code
- Organize static assets for maintainability
- Implement cache-busting strategies for production
- Configure multiple static folders and custom static routes
- Understand the security implications of serving user-uploaded files

## Flask's Static File System

Flask automatically creates a route for serving files from the `static/` folder:

```
myapp/
    __init__.py
    static/
        style.css
        script.js
        images/
            logo.png
            avatar.jpg
    templates/
```

### Referencing Static Files

In templates:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
<script src="{{ url_for('static', filename='script.js') }}"></script>
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
```

In Python code:

```python
from flask import url_for

css_url = url_for('static', filename='style.css')
# → '/static/style.css'
```

### The `static/` Route

Flask automatically registers a route for static files:

```python
# Equivalent to Flask's built-in behavior
app.add_url_rule('/static/<path:filename>', endpoint='static',
                 view_func=app.send_static_file)
```

The `send_static_file` method serves files from the `static_folder` directory.

## Configuration

| Config Key | Default | Description |
|------------|---------|-------------|
| `STATIC_FOLDER` | `'static'` | Folder name (relative to app root) |
| `STATIC_URL_PATH` | `'/static'` | URL path for static files |

### Custom Static Folder

```python
app = Flask(__name__,
            static_folder='assets',        # Look in 'assets/' instead of 'static/'
            static_url_path='/assets')     # Serve at /assets/ instead of /static/
```

### Absolute Path

```python
import os

app = Flask(__name__,
            static_folder='/var/www/static',
            static_url_path='/static')
```

### Multiple Static Folders

Flask does not natively support multiple static folders, but blueprints do (see [[06-Blueprints/Blueprints]]). Each blueprint can have its own static folder:

```python
main = Blueprint('main', __name__, static_folder='static')
auth = Blueprint('auth', __name__, static_folder='static')
```

Blueprint static files are accessed at `/blueprint_name/static/...` by default.

## Serving Static Files in Production

> [!WARNING]
> **Never use Flask to serve static files in production.** Flask's static file handler is not optimized for production traffic. Use a reverse proxy (Nginx) or a CDN instead.

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name example.com;
    
    # Serve static files directly
    location /static {
        alias /var/www/myapp/static;  # Path to your static folder
        expires 1y;                    # Cache for 1 year
        add_header Cache-Control "public, immutable";
    }
    
    # Proxy everything else to Flask
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

With this setup, Nginx serves static files directly without ever hitting Flask. This is dramatically faster.

## Cache Busting

Browsers cache static files aggressively. When you update `style.css`, returning visitors may still see the old version.

### Query String Cache Busting

```html
<link rel="stylesheet" href="{{ url_for('static', filename='style.css', v='1.2.3') }}">
<!-- → /static/style.css?v=1.2.3 -->
```

### Filename-based Cache Busting

More reliable — some proxies ignore query strings for caching:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='style.1.2.3.css') }}">
<!-- → /static/style.1.2.3.css -->
```

### Flask-Assets

The `Flask-Assets` extension automates cache busting and asset pipeline tasks:

```python
from flask_assets import Environment, Bundle

assets = Environment(app)

# Bundle and minify CSS
css_bundle = Bundle(
    'css/normalize.css',
    'css/main.css',
    filters='cssmin',
    output='gen/packed.css'
)
assets.register('css_all', css_bundle)
```

```html
{% assets "css_all" %}
    <link rel="stylesheet" href="{{ ASSET_URL }}">
{% endassets %}
```

## User-Uploaded Files

User-uploaded files should **not** be served from the static folder. They should be stored separately and served with controlled access.

### Upload Configuration

```python
import os

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

### Secure File Upload

```python
from flask import request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import uuid

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Secure the filename and add UUID to prevent collisions
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded successfully')
        return redirect(url_for('profile'))
```

### Serving Uploaded Files Securely

```python
from flask import send_from_directory
import os

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # Validate filename to prevent directory traversal
    safe_name = secure_filename(filename)
    upload_path = os.path.join(app.root_path, 'uploads')
    return send_from_directory(upload_path, safe_name)
```

> [!WARNING]
> Always use `secure_filename()` on user-provided filenames. Without it, attackers can use paths like `../../../etc/passwd` to read arbitrary files. Better yet, generate your own filenames (UUIDs) and discard the original name.

## MIME Types

Flask guesses MIME types based on file extensions. Common mappings:

| Extension | MIME Type |
|-----------|-----------|
| `.css` | `text/css` |
| `.js` | `application/javascript` |
| `.png` | `image/png` |
| `.jpg`, `.jpeg` | `image/jpeg` |
| `.gif` | `image/gif` |
| `.svg` | `image/svg+xml` |
| `.ico` | `image/x-icon` |
| `.woff2` | `font/woff2` |
| `.pdf` | `application/pdf` |

Add custom MIME types:

```python
import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
```

## Common Mistakes

**Mistake: Using Flask to serve static files in production**
Always use Nginx, a CDN, or a dedicated file server for static assets in production.

**Mistake: Storing uploaded files in the static folder**
User uploads should be stored separately with access controls. The static folder is for application assets only.

**Mistake: Not using `secure_filename()`**
Always sanitize uploaded filenames to prevent directory traversal attacks.

**Mistake: Hardcoding static file URLs**
Always use `url_for('static', filename='...')` — it handles URL prefixes and cache busting.

## Best Practices

- Use `url_for('static', filename=...)` for all static file references
- Serve static files via Nginx or CDN in production
- Implement cache-busting for CSS and JS files
- Store user uploads separately from static files
- Always use `secure_filename()` on uploaded files
- Generate UUID filenames for uploads to prevent collisions
- Set appropriate `Cache-Control` headers for static assets
- Use subdirectories within `static/` to organize assets

## Exercises

1. **Organize Assets**: Create a well-organized static folder structure for a web application with CSS, JS, images, and fonts.

2. **Cache Busting**: Implement a version-based cache busting system that appends a query parameter to static file URLs.

3. **Secure Upload**: Create a file upload handler that validates file types, sanitizes filenames, and stores files securely.

4. **Nginx Config**: Write an Nginx configuration that serves static files directly while proxying dynamic requests to Flask.

## Quiz

**Question 1**: How do you reference a static file in a Flask template?

**Question 2**: Why should you not use Flask to serve static files in production?

**Question 3**: What is cache busting, and why is it necessary?

**Question 4**: Why should user-uploaded files not be stored in the static folder?

**Question 5**: What does `secure_filename()` do, and why is it important?

## Interview Questions

1. "How does Flask handle static files? What would you change for production?"

2. "How would you implement cache busting for static assets in a Flask application?"

3. "What security measures should you take when handling file uploads in Flask?"

4. "Why should user-uploaded files be served separately from application static files?"

## Related Chapters

- Previous: [[01-Flask-Core/Cookies]]
- [[02-Jinja2/Jinja2-Overview]] — Using static files in templates
- [[07-Deployment/Nginx]] — Nginx configuration for static files
- [[08-Security/Security-Overview]] — File upload security

## Official Documentation References

- [Flask Static Files](https://flask.palletsprojects.com/en/latest/quickstart/#static-files)
- [Flask send_static_file](https://flask.palletsprojects.com/en/latest/api/#flask.Flask.send_static_file)
- [Flask send_from_directory](https://flask.palletsprojects.com/en/latest/api/#flask.send_from_directory)

---

*Previous: [[01-Flask-Core/Cookies]] | Next: [[02-Jinja2/Jinja2-Overview]]*