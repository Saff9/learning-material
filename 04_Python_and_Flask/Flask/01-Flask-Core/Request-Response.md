---
title: Request and Response
description: How Flask processes incoming HTTP requests and constructs outgoing responses
chapter: 01-Flask-Core
tags:
  - request
  - response
  - http
  - werkzeug
  - json
  - forms
  - core
difficulty: Beginner
prerequisites:
  - [[01-Flask-Core/Routing]]
  - [[00-Foundations/HTTP]]
---

# Request and Response

> Every Flask application exists to receive requests and return responses. The `Request` object encapsulates everything the client sends; the `Response` object encapsulates everything you send back. Understanding these objects completely is essential for building Flask applications.

## Learning Objectives

After completing this chapter, you will be able to:

- Access all components of an HTTP request through Flask's `request` object
- Construct and customize HTTP responses using `Response`, `make_response()`, and `jsonify()`
- Handle different content types: JSON, form data, file uploads
- Manage cookies in requests and responses
- Implement redirects correctly
- Stream large responses efficiently

## The Request Object

Flask's `request` object (actually Werkzeug's `Request` class) contains everything about the current HTTP request. It is a **context-local proxy** — it appears global but is actually bound to the current request thread.

```python
from flask import request

@app.route('/example')
def example():
    # request is available only within a request context
    print(request.method)      # 'GET'
    print(request.path)        # '/example'
    return 'OK'
```

### Request Attributes

#### URL Components

```python
request.url           # Full URL: 'http://localhost:5000/search?q=hello'
request.base_url      # Without query string: 'http://localhost:5000/search'
request.url_root      # 'http://localhost:5000/'
request.host_url      # 'http://localhost:5000/'
request.host          # 'localhost:5000'
request.path          # '/search'
request.full_path     # '/search?q=hello'
request.query_string  # b'q=hello' (raw bytes)
request.script_root   # '' (application root path)
```

#### HTTP Method and Headers

```python
request.method        # 'GET', 'POST', 'PUT', etc.
request.headers       # Headers MultiDict
request.content_type  # 'application/json', 'text/html', etc.
request.content_length # Body size in bytes
request.user_agent    # UserAgent object (browser, platform info)
request.remote_addr   # Client IP address
request.scheme        # 'http' or 'https'
request.is_secure     # True if HTTPS
request.is_json       # True if Content-Type is application/json
```

#### Query Parameters

```python
# URL: /search?q=flask&page=2

request.args                    # ImmutableMultiDict([('q', 'flask'), ('page', '2')])
request.args['q']              # 'flask'
request.args.get('q')          # 'flask' (safer, returns None if missing)
request.args.get('page', 1)    # '2' (with default)
request.args.get('missing', 'default')  # 'default'

# Type conversion
request.args.get('page', 1, type=int)   # 2 (as integer)

# Multiple values
request.args.getlist('tag')    # ['python', 'flask'] for ?tag=python&tag=flask

# All parameters
request.args.to_dict()         # {'q': 'flask', 'page': '2'}
```

> [!TIP]
> Always use `.get()` instead of `[]` access for query parameters. Missing parameters with `[]` raise a 400 Bad Request error. With `.get()`, you get `None` or a default value.

#### Form Data

```python
# POST with Content-Type: application/x-www-form-urlencoded

request.form           # ImmutableMultiDict([('name', 'John'), ('email', 'john@example.com')])
request.form['name']   # 'John'
request.form.get('name')
request.form.getlist('checkbox_name')  # Multiple checkboxes with same name
```

#### JSON Data

```python
request.get_json()              # Parsed JSON dict, or None if invalid
request.get_json(force=True)    # Parse even if Content-Type is not JSON
request.get_json(silent=True)   # Return None instead of raising on error

# Common pattern with validation
data = request.get_json()
if not data or 'required_field' not in data:
    return jsonify({'error': 'Missing required_field'}), 400
```

#### File Uploads

```python
request.files           # ImmutableMultiDict of uploaded files
uploaded_file = request.files['document']

# File object attributes
uploaded_file.filename      # Original filename
uploaded_file.content_type  # MIME type
uploaded_file.content_length # Size in bytes
uploaded_file.mimetype      # Same as content_type

# Save to disk
uploaded_file.save('/path/to/uploads/document.pdf')

# Read into memory
content = uploaded_file.read()

# Secure the filename (prevent path traversal)
from werkzeug.utils import secure_filename
safe_name = secure_filename(uploaded_file.filename)
uploaded_file.save(f'uploads/{safe_name}')
```

> [!WARNING]
> Always use `secure_filename()` on uploaded filenames. Malicious users can upload files with names like `../../../etc/passwd` to overwrite system files.

#### Cookies

```python
request.cookies          # Dict of cookies
request.cookies.get('session_id')
```

#### Other Data Sources

```python
request.data            # Raw request body (bytes)
request.stream          # Body as a stream (for large uploads)
request.values          # Combined args + form (don't use — confusing)
```

### Request Methods Example

```python
from flask import request, jsonify

@app.route('/api/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        # GET /api/items?page=2&limit=10
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        return jsonify(get_items(page=page, limit=limit))
    
    # POST /api/items
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'name is required'}), 400
    
    item = create_item(name=data['name'], description=data.get('description'))
    return jsonify(item), 201
```

## The Response Object

A Flask view function can return several types:

| Return Type | Behavior |
|-------------|----------|
| `str` | Converted to Response with `text/html` content type |
| `dict` | Converted to JSON response (Flask 1.1+) |
| `tuple` | `(body, status)` or `(body, status, headers)` |
| `Response` | Used directly |
| Generator | Streaming response |

### Creating Responses

#### Simple String Response

```python
@app.route('/hello')
def hello():
    return 'Hello, World!'  # Content-Type: text/html; charset=utf-8
```

#### JSON Response

```python
from flask import jsonify

@app.route('/api/user')
def user():
    return jsonify({
        'id': 1,
        'name': 'John Doe',
        'email': 'john@example.com'
    })
```

`jsonify()` automatically:
- Serializes the dict to JSON
- Sets `Content-Type: application/json`
- Returns a `Response` object

#### Tuple Response (Status Code and Headers)

```python
@app.route('/created')
def created():
    return 'Created!', 201  # Body + status code

@app.route('/redirect-me')
def redirect_me():
    return '', 302, {'Location': '/new-location'}  # Body + status + headers
```

#### Using make_response()

For full control over the response:

```python
from flask import make_response

@app.route('/custom')
def custom_response():
    response = make_response('Custom response', 200)
    response.headers['X-Custom-Header'] = 'value'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.set_cookie('preference', 'dark_mode')
    return response
```

#### Response Class

Direct `Response` object construction:

```python
from flask import Response

@app.route('/text')
def text_response():
    return Response('Plain text', mimetype='text/plain')

@app.route('/csv')
def csv_response():
    csv_data = 'name,email\nJohn,john@example.com'
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=data.csv'}
    )
```

### Response Methods and Attributes

```python
response = make_response('Hello')

response.status_code = 200
response.status = '200 OK'           # String form
response.headers['X-Custom'] = 'val'
response.content_type = 'text/plain'
response.set_cookie('key', 'value', max_age=3600, httponly=True, secure=True)
response.delete_cookie('key')        # Expire the cookie
response.data                        # Response body (bytes)
```

## Redirects

```python
from flask import redirect, url_for

@app.route('/old-page')
def old_page():
    return redirect('/new-page', code=301)  # Permanent redirect

@app.route('/login-required')
def login_required():
    return redirect(url_for('login', next=request.path))  # Login + redirect back
```

Common redirect codes:
- **302 Found** (default): Temporary redirect. Browser uses GET for the next request.
- **301 Moved Permanently**: Permanent redirect. Cached by browsers and search engines.
- **307 Temporary Redirect**: Temporary redirect. Preserves the HTTP method (POST stays POST).
- **308 Permanent Redirect**: Permanent redirect. Preserves the HTTP method.

> [!TIP]
> Use `url_for()` with redirects, never hardcoded paths. If you change a route, all redirects update automatically.

## Setting Cookies

```python
from flask import make_response

@app.route('/set-cookie')
def set_cookie():
    response = make_response('Cookie set')
    response.set_cookie(
        'username',           # Cookie name
        'john_doe',           # Cookie value
        max_age=3600,         # Expires in 1 hour (seconds)
        httponly=True,        # Not accessible via JavaScript
        secure=True,          # HTTPS only
        samesite='Lax'        # CSRF protection
    )
    return response
```

## Deleting Cookies

```python
@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))
    response.delete_cookie('username')
    response.delete_cookie('session_id')
    return response
```

## File Downloads

```python
from flask import send_file, send_from_directory
import io

@app.route('/download')
def download():
    # Send a file from disk
    return send_file('reports/monthly.pdf', as_attachment=True)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # Serve files from a directory (with security)
    return send_from_directory('uploads', filename)

@app.route('/download-csv')
def download_csv():
    # Generate and send file from memory
    csv_data = 'id,name\n1,Alice\n2,Bob'
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=data.csv'}
    )
```

## Streaming Responses

For large responses that should not be buffered entirely in memory:

```python
from flask import stream_with_context, Response

def generate_large_csv():
    yield 'id,name,email\n'
    for user in User.query.yield_per(100):  # Stream from database
        yield f'{user.id},{user.name},{user.email}\n'

@app.route('/large-export')
def large_export():
    return Response(
        stream_with_context(generate_large_csv()),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=users.csv'}
    )
```

## Common Mistakes

**Mistake: Using `request.data` instead of `request.get_json()`**
`request.data` returns raw bytes. `request.get_json()` parses JSON into a Python dict.

**Mistake: Not checking if JSON data is None**
`request.get_json()` returns `None` for invalid or missing JSON. Always check before accessing.

**Mistake: Returning dicts without `jsonify()` in older Flask**
In Flask < 1.1, returning a dict raises an error. Use `jsonify()` explicitly.

**Mistake: Using 302 for POST redirects that should preserve method**
After form submission, redirect with 303 (GET) or 307 (preserve method), not 302.

## Best Practices

- Use `request.get_json(silent=True)` and validate the result
- Always use `secure_filename()` for uploaded files
- Use `url_for()` in redirects, never hardcoded paths
- Set appropriate `Content-Type` headers
- Use `make_response()` when you need headers or cookies
- Stream large responses to avoid memory issues

## Exercises

1. **Request Inspector**: Create a route that returns all information about the current request as JSON (method, URL, headers, args, form, cookies).

2. **File Upload Handler**: Create a route that accepts image uploads, validates the file type, and saves it securely.

3. **CSV Export**: Create a route that streams a large CSV file from a database query without loading all data into memory.

4. **Cookie Manager**: Create routes to set, read, and delete cookies with all security attributes.

## Quiz

**Question 1**: What is the difference between `request.args` and `request.form`?

**Question 2**: How do you safely access a query parameter that might not exist?

**Question 3**: What does `jsonify()` do that returning a plain dict does not?

**Question 4**: What is the difference between a 301 and 302 redirect?

**Question 5**: Why should you use `secure_filename()` on uploaded files?

## Interview Questions

1. "Explain Flask's request object. How do you access query parameters, form data, and JSON?"

2. "What are the different ways to create a response in Flask? When would you use each?"

3. "How would you handle a file upload in Flask? What security considerations apply?"

4. "Explain streaming responses in Flask. When are they useful?"

5. "A client sends JSON but `request.get_json()` returns None. What could be wrong?"

## Related Chapters

- Previous: [[01-Flask-Core/URL-Converters]]
- Next: [[01-Flask-Core/Request-Context]]
- [[01-Flask-Core/Cookies]] — Deep dive into cookie management
- [[04-Authentication/Flask-WTF]] — Form handling with Flask-WTF

## Official Documentation References

- [Flask Request Object](https://flask.palletsprojects.com/en/latest/api/#incoming-request-data)
- [Flask Response Object](https://flask.palletsprojects.com/en/latest/api/#response-objects)
- [Werkzeug Request/Response Documentation](https://werkzeug.palletsprojects.com/en/latest/wrappers/)

---

*Previous: [[01-Flask-Core/URL-Converters]] | Next: [[01-Flask-Core/Request-Context]]*