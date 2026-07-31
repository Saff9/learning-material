---
title: HTTP - HyperText Transfer Protocol
description: The protocol that powers the World Wide Web and that every Flask application speaks
chapter: 00-Foundations
tags:
  - http
  - protocol
  - request-response
  - methods
  - status-codes
  - headers
  - foundations
difficulty: Beginner
prerequisites:
  - [[00-Foundations/TCP-UDP]]
  - [[00-Foundations/TLS-HTTPS]]
---

# HTTP — HyperText Transfer Protocol

> HTTP is the language of the web. Every Flask application you build will spend its entire life speaking HTTP — receiving requests, processing them, and sending responses. Understanding HTTP deeply is not optional. It is the single most important prerequisite for web development.

## Learning Objectives

After completing this chapter, you will be able to:

- Explain HTTP's request-response model and stateless nature
- Construct and parse HTTP requests and responses manually
- Use all HTTP methods appropriately (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
- Interpret every major HTTP status code and choose the correct one for your Flask endpoints
- Use request and response headers effectively
- Explain content negotiation, caching headers, and authentication schemes
- Debug HTTP communication using browser DevTools and command-line tools

## What Is HTTP?

**HTTP (HyperText Transfer Protocol)** is an application-layer protocol for transmitting documents, such as HTML. It is the foundation of data communication on the World Wide Web.

HTTP was invented by **Tim Berners-Lee** at CERN in 1989 as part of the World Wide Web project. The first version, HTTP/0.9, was incredibly simple — just a single line requesting a document. Today's HTTP/1.1 and HTTP/2 are far more capable but still follow the same fundamental model.

### Key Characteristics

| Characteristic | Description |
|---------------|-------------|
| **Request-Response** | Client sends a request; server sends a response |
| **Stateless** | Each request is independent — the server remembers nothing between requests |
| **Text-based** | HTTP/1.1 messages are human-readable text |
| **Connection-oriented** | Runs over TCP (port 80 for HTTP, 443 for HTTPS) |
| **Extensible** | Headers allow custom metadata; new methods and status codes can be defined |

The **stateless** nature is crucial. The server treats every request as if it were the first. It does not know if the same client made a previous request. This simplicity makes HTTP scalable but requires cookies and sessions to maintain state (covered in [[00-Foundations/Cookies-Sessions]]).

## The HTTP Request

An HTTP request consists of:

```
METHOD PATH HTTP/VERSION
Header-Name: Header-Value
Header-Name: Header-Value

Request Body (optional)
```

### Request Line

The first line contains three elements:

```
GET /users/123 HTTP/1.1
```

1. **Method**: What action to perform (`GET`, `POST`, etc.)
2. **Path**: The resource location (`/users/123`)
3. **Version**: The HTTP protocol version (`HTTP/1.1`)

### Headers

Headers provide metadata about the request:

```
Host: api.example.com
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15)
Accept: application/json
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json
Content-Length: 45
```

Common request headers:

| Header | Purpose |
|--------|---------|
| `Host` | Required in HTTP/1.1. Specifies the target domain. Enables virtual hosting. |
| `User-Agent` | Identifies the client software |
| `Accept` | What content types the client can handle |
| `Accept-Language` | Preferred language for the response |
| `Accept-Encoding` | Compression algorithms the client supports (gzip, br) |
| `Authorization` | Credentials for authentication |
| `Content-Type` | Media type of the request body |
| `Content-Length` | Size of the request body in bytes |
| `Cookie` | Previously set cookies sent back to the server |
| `Referer` | The URL of the page that linked to this resource |

### Request Body

The body carries data for POST, PUT, and PATCH requests. Common formats:

**Form data (`application/x-www-form-urlencoded`):**
```
name=John+Doe&email=john%40example.com&age=30
```

**Multipart form data (`multipart/form-data`)** — for file uploads:
```
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="photo.jpg"
Content-Type: image/jpeg

[binary file data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**JSON (`application/json`):**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
}
```

## The HTTP Response

An HTTP response follows the same structure:

```
HTTP/VERSION STATUS_CODE REASON_PHRASE
Header-Name: Header-Value
Header-Name: Header-Value

Response Body (optional)
```

### Status Line

```
HTTP/1.1 200 OK
HTTP/1.1 404 Not Found
HTTP/1.1 500 Internal Server Error
```

### Status Codes

HTTP status codes are three-digit numbers grouped by their first digit:

#### 1xx — Informational

| Code | Name | Meaning |
|------|------|---------|
| 100 | Continue | Client should continue with the request body |
| 101 | Switching Protocols | Server is switching to a different protocol (e.g., WebSocket) |
| 103 | Early Hints | Preload hints for resources (used with HTTP/2 push) |

#### 2xx — Success

| Code | Name | Meaning | Flask Usage |
|------|------|---------|-------------|
| 200 | OK | Request succeeded | Standard successful GET, PUT, PATCH |
| 201 | Created | Resource was created | Successful POST that creates a resource |
| 204 | No Content | Success, no body to return | Successful DELETE, or update with no response needed |

#### 3xx — Redirection

| Code | Name | Meaning | Flask Usage |
|------|------|---------|-------------|
| 301 | Moved Permanently | Resource relocated permanently | Changed URL structure — SEO-friendly redirect |
| 302 | Found | Temporary redirect | `redirect(url, code=302)` — default in Flask |
| 304 | Not Modified | Resource unchanged (use cached version) | Response to conditional GET with If-None-Match |
| 307 | Temporary Redirect | Temporary redirect, method preserved | Preferred over 302 for POST preservation |
| 308 | Permanent Redirect | Permanent redirect, method preserved | Preferred over 301 for POST preservation |

#### 4xx — Client Error

| Code | Name | Meaning | Flask Usage |
|------|------|---------|-------------|
| 400 | Bad Request | Malformed request syntax | Invalid JSON, missing required field |
| 401 | Unauthorized | Authentication required | User not logged in |
| 403 | Forbidden | Authenticated but not authorized | Logged in but no permission |
| 404 | Not Found | Resource does not exist | Wrong URL, deleted resource |
| 405 | Method Not Allowed | HTTP method not supported for this resource | `GET` on a `POST`-only endpoint |
| 409 | Conflict | Request conflicts with current state | Duplicate resource, optimistic locking failure |
| 422 | Unprocessable Entity | Valid syntax but semantic errors | Validation errors in form/API |
| 429 | Too Many Requests | Rate limit exceeded | Implement rate limiting |

#### 5xx — Server Error

| Code | Name | Meaning | Flask Usage |
|------|------|---------|-------------|
| 500 | Internal Server Error | Unexpected server error | Unhandled exception — always log these |
| 502 | Bad Gateway | Upstream server returned invalid response | Nginx cannot reach Gunicorn |
| 503 | Service Unavailable | Server temporarily unavailable | Maintenance mode, overload |
| 504 | Gateway Timeout | Upstream server did not respond in time | Database query timeout |

> [!TIP]
> Choose status codes carefully. They are the primary way your API communicates outcome to clients. A `403` tells the client "you need different permissions" while a `401` tells them "you need to log in." These are actionable differences.

### Response Headers

| Header | Purpose |
|--------|---------|
| `Content-Type` | Media type of the response body |
| `Content-Length` | Size of the response body in bytes |
| `Content-Encoding` | Compression applied (gzip, br) |
| `Date` | When the response was generated |
| `Server` | Server software information (often omitted for security) |
| `Set-Cookie` | Instructs the browser to store a cookie |
| `Cache-Control` | Caching directives |
| `ETag` | Entity tag for cache validation |
| `Location` | Redirect target URL (used with 3xx status) |
| `X-Frame-Options` | Clickjacking protection |
| `Content-Security-Policy` | XSS protection |

## HTTP Methods

HTTP methods (also called verbs) indicate the desired action on a resource.

### GET

Retrieves a resource. GET requests should have **no side effects** — they should not modify server state.

```http
GET /users/123 HTTP/1.1
Host: api.example.com
```

**Characteristics:**
- Safe: Does not modify state
- Idempotent: Multiple identical requests produce the same result
- Cacheable: Responses can be cached
- No body: GET requests should not have a body (though some servers accept it)

In Flask:

```python
@app.get('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())
```

### POST

Creates a new resource or triggers a process.

```http
POST /users HTTP/1.1
Host: api.example.com
Content-Type: application/json
Content-Length: 45

{"name": "John Doe", "email": "john@example.com"}
```

**Characteristics:**
- Not safe: Modifies state
- Not idempotent: Submitting twice creates two resources
- Body required: Carries the resource representation

In Flask:

```python
@app.post('/users')
def create_user():
    data = request.get_json()
    user = User(name=data['name'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201
```

### PUT

Replaces a resource entirely with the provided representation.

```http
PUT /users/123 HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"name": "Jane Doe", "email": "jane@example.com", "age": 25}
```

**Characteristics:**
- Not safe: Modifies state
- Idempotent: PUTting the same data multiple times produces the same result
- Full replacement: Missing fields are typically set to null/default

In Flask:

```python
@app.put('/users/<int:user_id>')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.name = data['name']
    user.email = data['email']
    user.age = data.get('age')
    db.session.commit()
    return jsonify(user.to_dict())
```

### PATCH

Partially modifies a resource.

```http
PATCH /users/123 HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"email": "newemail@example.com"}
```

**Characteristics:**
- Not safe: Modifies state
- Not necessarily idempotent (depends on the patch operation)
- Partial update: Only specified fields change

In Flask:

```python
@app.patch('/users/<int:user_id>')
def patch_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if 'email' in data:
        user.email = data['email']
    if 'name' in data:
        user.name = data['name']
    db.session.commit()
    return jsonify(user.to_dict())
```

### DELETE

Removes a resource.

```http
DELETE /users/123 HTTP/1.1
Host: api.example.com
```

**Characteristics:**
- Not safe: Modifies state
- Idempotent: Deleting the same resource twice has the same result (the resource is gone)
- Response: Usually 204 No Content on success

In Flask:

```python
@app.delete('/users/<int:user_id>')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204
```

### HEAD

Identical to GET but returns only headers, no body. Used to check if a resource exists, get its metadata, or validate cache freshness without downloading the full content.

In Flask, HEAD is handled automatically for GET routes.

### OPTIONS

Returns the HTTP methods supported for a resource. Used for CORS preflight requests.

```python
@app.route('/users', methods=['GET', 'POST', 'OPTIONS'])
def users():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST')
        return response
    # ...
```

### Method Comparison

| Method | Safe | Idempotent | Body | Purpose |
|--------|------|-----------|------|---------|
| GET | Yes | Yes | No | Retrieve |
| POST | No | No | Yes | Create/Process |
| PUT | No | Yes | Yes | Full update |
| PATCH | No | No* | Yes | Partial update |
| DELETE | No | Yes | No | Remove |
| HEAD | Yes | Yes | No | Metadata |
| OPTIONS | Yes | Yes | No | Capabilities |

## HTTP in Flask

Flask abstracts HTTP into Python objects:

### The Request Object

```python
from flask import request

@app.route('/example', methods=['GET', 'POST'])
def example():
    # Request line
    method = request.method           # 'GET' or 'POST'
    path = request.path               # '/example'
    url = request.url                 # Full URL
    
    # Headers
    user_agent = request.headers.get('User-Agent')
    content_type = request.content_type
    
    # Query parameters: ?key=value&foo=bar
    key = request.args.get('key')
    
    # Form data (POST, application/x-www-form-urlencoded)
    name = request.form.get('name')
    
    # JSON body
    data = request.get_json()         # Parsed JSON dict
    
    # Raw body
    raw = request.data                # Raw bytes
    
    # Cookies
    session_id = request.cookies.get('session_id')
    
    # File uploads
    file = request.files.get('upload')
```

### The Response Object

```python
from flask import Flask, make_response, jsonify

@app.route('/custom-response')
def custom_response():
    response = make_response('Hello', 200)
    response.headers['X-Custom-Header'] = 'value'
    response.content_type = 'text/plain'
    return response

# JSON response (with correct Content-Type)
@app.route('/api/data')
def api_data():
    return jsonify({'key': 'value'}), 200
```

## Debugging HTTP

### curl

```bash
# Simple GET
curl https://api.example.com/users

# With headers
curl -i https://api.example.com/users

# POST with JSON
curl -X POST https://api.example.com/users \
     -H "Content-Type: application/json" \
     -d '{"name": "John", "email": "john@example.com"}'

# Custom headers
curl -H "Authorization: Bearer TOKEN" \
     https://api.example.com/protected

# Follow redirects
curl -L https://bit.ly/some-short-url

# Save response to file
curl -o output.json https://api.example.com/data

# Verbose (shows request headers, response headers, TLS info)
curl -v https://example.com
```

### httpie

A more user-friendly HTTP client:

```bash
# GET
http GET api.example.com/users

# POST with JSON
http POST api.example.com/users name=John email=john@example.com

# With headers
http GET api.example.com/protected Authorization:"Bearer TOKEN"

# Form data
http --form POST api.example.com/upload file@photo.jpg
```

### Browser DevTools

Open DevTools (F12) → Network tab:
- See every HTTP request and response
- Inspect headers, cookies, query parameters
- View timing breakdown (DNS, TCP handshake, TLS, TTFB)
- Export requests as curl commands
- Throttle connection speed to simulate slow networks

## Common Mistakes

**Mistake: Using GET for state-changing operations**
GET should never modify data. A web crawler or browser prefetch could trigger destructive actions.

**Mistake: Returning 200 for errors**
A 200 OK with an error message in the body confuses clients. Use appropriate error status codes.

**Mistake: Ignoring HTTP caching**
Without proper caching headers, browsers re-request static assets on every page load. Use `Cache-Control`, `ETag`, and `Last-Modified`.

**Mistake: Not handling content negotiation**
Return the content type the client requested (via `Accept` header) or respond with 406 Not Acceptable.

## Best Practices

- Use appropriate HTTP methods for each operation
- Return correct status codes — they communicate outcome to clients
- Set proper `Content-Type` headers on all responses
- Use `Location` headers with 201 Created responses
- Implement proper error responses with consistent JSON structures
- Use caching headers for static and semi-static content
- Log all 5xx errors for investigation

## Exercises

1. **Raw HTTP**: Use `telnet example.com 80` (or `nc example.com 80`) to send a raw HTTP request:
   ```
   GET / HTTP/1.1
   Host: example.com
   
   ```
   Observe the raw response.

2. **curl Mastery**: Use curl to test a Flask endpoint with different methods, headers, and body content.

3. **Status Code Practice**: For each scenario, choose the correct status code:
   - User submits a form with invalid email format
   - User tries to access admin page without logging in
   - User tries to access admin page while logged in as regular user
   - Resource creation succeeds
   - Resource already exists on duplicate creation attempt

4. **Inspect Real Traffic**: Visit a complex website with DevTools open. Count the number of HTTP requests. How many are cached (304 responses)? What is the largest response?

## Quiz

**Question 1**: What does it mean that HTTP is stateless? How do web applications maintain user sessions despite this?

**Question 2**: What is the difference between PUT and PATCH? When would you use each?

**Question 3**: A POST request is not idempotent. Why does this matter in practice?

**Question 4**: What information does the `Host` header provide, and why is it required in HTTP/1.1?

**Question 5**: A server returns 302 Found. What happens in the browser? How does this differ from 307?

## Interview Questions

1. "Explain HTTP's request-response cycle. What makes HTTP stateless?"

2. "What is the difference between PUT, PATCH, and POST? Give examples."

3. "A user submits a form twice by accident. How does using the right HTTP method prevent duplicate data?"

4. "What status code would you return for each scenario: successful creation, authentication required, validation error, server crash?"

5. "Explain how HTTP caching works. What headers are involved?"

6. "What is the purpose of the Accept header? How should a server respond if it cannot provide the requested format?"

## Related Chapters

- Previous: [[00-Foundations/TLS-HTTPS]]
- Next: [[00-Foundations/HTTP2-HTTP3]]
- [[00-Foundations/Cookies-Sessions]] — State management over stateless HTTP
- [[00-Foundations/REST-APIs]] — RESTful design using HTTP
- [[01-Flask-Core/Request-Response]] — Flask's HTTP abstraction

## Official Documentation References

- [RFC 7231 - HTTP/1.1 Semantics and Content](https://datatracker.ietf.org/doc/html/rfc7231)
- [RFC 7230 - HTTP/1.1 Message Syntax and Routing](https://datatracker.ietf.org/doc/html/rfc7230)
- [RFC 5789 - PATCH Method for HTTP](https://datatracker.ietf.org/doc/html/rfc5789)
- [MDN - HTTP Overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [MDN - HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)

---

*Previous: [[00-Foundations/TLS-HTTPS]] | Next: [[00-Foundations/HTTP2-HTTP3]]*