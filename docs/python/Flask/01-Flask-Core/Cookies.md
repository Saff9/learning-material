---
title: Cookies
description: Managing HTTP cookies in Flask — setting, reading, and securing cookies
chapter: 01-Flask-Core
tags:
  - cookies
  - http
  - session
  - security
  - core
difficulty: Beginner
prerequisites:
  - [[01-Flask-Core/Sessions]]
---

# Cookies

> Cookies are the HTTP mechanism for storing small amounts of data on the client's browser. Flask provides simple APIs for setting and reading cookies, but using them securely requires understanding their attributes and vulnerabilities.

## Learning Objectives

After completing this chapter, you will be able to:

- Set and read cookies in Flask requests and responses
- Configure all cookie attributes (expires, path, domain, secure, httponly, samesite)
- Understand cookie size limitations and best practices
- Implement secure cookie handling for production applications
- Distinguish between Flask's session cookies and custom cookies

## Setting Cookies

Cookies are set via the `Set-Cookie` HTTP response header. In Flask, use `response.set_cookie()`:

```python
from flask import make_response

@app.route('/set-cookie')
def set_cookie():
    response = make_response('Cookie set!')
    response.set_cookie(
        'theme',              # Cookie name
        'dark',               # Cookie value
        max_age=3600,         # Expiration in seconds (1 hour)
        path='/',             # Available on all paths
        domain=None,          # Current domain only
        secure=True,          # HTTPS only
        httponly=True,        # Not accessible via JavaScript
        samesite='Lax'        # CSRF protection
    )
    return response
```

### Cookie Attributes

| Attribute | Description | Security Impact |
|-----------|-------------|-----------------|
| `max_age` | Lifetime in seconds | Shorter = more secure |
| `expires` | Specific expiration datetime | Alternative to max_age |
| `path` | URL path restriction | Limit scope |
| `domain` | Domain restriction | Prevent subdomain leakage |
| `secure` | HTTPS only | Prevent network sniffing |
| `httponly` | No JavaScript access | Prevent XSS theft |
| `samesite` | Cross-site behavior | Prevent CSRF |

### Setting Multiple Cookies

```python
@app.route('/set-preferences')
def set_preferences():
    response = make_response('Preferences saved!')
    response.set_cookie('theme', 'dark', max_age=2592000)
    response.set_cookie('language', 'en', max_age=2592000)
    response.set_cookie('font_size', '16', max_age=2592000)
    return response
```

## Reading Cookies

Read cookies from the request:

```python
from flask import request

@app.route('/get-cookie')
def get_cookie():
    theme = request.cookies.get('theme', 'light')  # Default to 'light'
    return f'Current theme: {theme}'
```

### Checking Cookie Existence

```python
@app.route('/check-cookie')
def check_cookie():
    if 'theme' in request.cookies:
        return f"Theme: {request.cookies['theme']}"
    return "No theme set"
```

## Deleting Cookies

```python
@app.route('/delete-cookie')
def delete_cookie():
    response = make_response('Cookie deleted!')
    response.delete_cookie('theme')
    return response
```

`delete_cookie()` sets the cookie with an expiration in the past, causing the browser to remove it.

### Complete Cookie Cleanup on Logout

```python
@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('index')))
    
    # Clear session
    session.clear()
    
    # Delete all custom cookies
    for cookie_name in ['theme', 'language', 'preferences']:
        response.delete_cookie(cookie_name)
    
    return response
```

## Cookie Limitations

| Limit | Value |
|-------|-------|
| Maximum size per cookie | 4 KB (4096 bytes) |
| Maximum cookies per domain | ~50 (varies by browser) |
| Total cookie size per domain | ~4 KB (sent with every request) |
| Characters allowed | Limited ASCII subset |

> [!WARNING]
> Cookies are sent with every HTTP request to the domain. Large cookies slow down every page load. Keep cookie data minimal — store only identifiers, not full objects.

## Signed Cookies

For cookies that must not be tampered with, use Werkzeug's secure cookie:

```python
from werkzeug.secure_cookie import SecureCookie

# Or use Flask's session (which is already signed)
# For custom signed data:
from itsdangerous import URLSafeTimedSerializer

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@app.route('/set-signed')
def set_signed():
    token = serializer.dumps({'user_id': 123, 'role': 'admin'})
    response = make_response('Signed cookie set!')
    response.set_cookie('auth_token', token, httponly=True, secure=True)
    return response

@app.route('/read-signed')
def read_signed():
    token = request.cookies.get('auth_token')
    if token:
        try:
            data = serializer.loads(token, max_age=3600)  # 1 hour max
            return f"User: {data['user_id']}, Role: {data['role']}"
        except:
            return "Invalid or expired token"
    return "No token"
```

## Cookie Security Checklist

For production applications:

```python
# All custom cookies should use:
response.set_cookie(
    'cookie_name',
    'value',
    secure=True,        # HTTPS only
    httponly=True,      # No JavaScript access
    samesite='Lax',     # CSRF protection
    max_age=3600        # Reasonable lifetime
)
```

## Custom Cookies vs. Session

| Aspect | Custom Cookies | Flask Session |
|--------|---------------|---------------|
| API | `set_cookie()` / `request.cookies` | `session['key']` |
| Signing | Manual (itsdangerous) | Automatic |
| Size limit | 4 KB per cookie | 4 KB total |
| Expiration | Manual control | `PERMANENT_SESSION_LIFETIME` |
| Use case | Preferences, tracking | Authentication state |

Use the session for authentication and user state. Use custom cookies for user preferences that do not need signing.

## Common Mistakes

**Mistake: Storing sensitive data in unsigned cookies**
Always sign cookies that contain trusted data, or use Flask's session.

**Mistake: Not setting Secure in production**
Cookies without `Secure` are sent over HTTP, exposing them to network sniffing.

**Mistake: Large cookies**
Cookies over 4KB are dropped by browsers. Store large data server-side.

**Mistake: Trusting cookie data without validation**
Always validate and sanitize cookie values before using them.

## Best Practices

- Keep cookie data minimal (identifiers, not objects)
- Always set `httponly=True` and `secure=True` in production
- Use `samesite='Lax'` for all cookies
- Set reasonable `max_age` values
- Use Flask's session for authentication data
- Sign custom cookies with itsdangerous
- Validate all cookie data before use

## Exercises

1. **Theme Cookie**: Create routes to set, read, and delete a "theme" cookie (light/dark mode).

2. **Secure Cookie**: Implement a signed cookie that stores a user preference and verifies it has not been tampered with.

3. **Cookie Manager**: Build a simple admin interface that lists all cookies and allows deleting them.

4. **Cookie Size Test**: Try to set a cookie with a 5KB value. What happens? How does the browser handle it?

## Quiz

**Question 1**: How do you set a cookie in Flask? What parameters control its behavior?

**Question 2**: What do the `httonly`, `secure`, and `samesite` attributes do?

**Question 3**: What is the maximum size of a cookie? What happens if you exceed it?

**Question 4**: What is the difference between Flask's session and a custom cookie?

**Question 5**: How do you delete a cookie in Flask?

## Interview Questions

1. "How do cookies work in HTTP? How does Flask set and read them?"

2. "What security attributes should be set on cookies in production? Why?"

3. "What is the difference between a session cookie and a persistent cookie?"

4. "How would you securely store a user preference in a cookie?"

5. "What are the limitations of cookies, and how do you work around them?"

## Related Chapters

- Previous: [[01-Flask-Core/Sessions]]
- Next: [[01-Flask-Core/Static-Files]]
- [[08-Security/CSRF-Protection]] — CSRF and SameSite cookies
- [[Appendix/itsdangerous]] — Data signing library

## Official Documentation References

- [Flask Response set_cookie](https://flask.palletsprojects.com/en/latest/api/#flask.Response.set_cookie)
- [MDN HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [OWASP Cookie Attributes](https://cheatsheetseries.owasp.org/cheatsheets/Cookie_Attributes_Cheat_Sheet.html)

---

*Previous: [[01-Flask-Core/Sessions]] | Next: [[01-Flask-Core/Static-Files]]*