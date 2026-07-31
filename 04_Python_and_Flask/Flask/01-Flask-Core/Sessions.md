---
title: Sessions in Flask
description: How Flask manages user sessions — from signed cookies to security best practices
chapter: 01-Flask-Core
tags:
  - sessions
  - cookies
  - itsdangerous
  - security
  - state-management
  - core
difficulty: Beginner
prerequisites:
  - [[01-Flask-Core/Request-Context]]
  - [[00-Foundations/Cookies-Sessions]]
---

# Sessions in Flask

> Flask's session system allows you to store data across requests, solving HTTP's statelessness. Understanding how Flask's client-side sessions work — and their security implications — is essential for building authenticated applications.

## Learning Objectives

After completing this chapter, you will be able to:

- Explain how Flask's client-side sessions work using signed cookies
- Use the `session` object to store and retrieve data
- Configure session security settings (HttpOnly, Secure, SameSite)
- Understand the difference between client-side and server-side sessions
- Implement session expiration and cleanup
- Explain session security threats and countermeasures

## Flask's Session System

Flask uses **client-side sessions** by default. Session data is stored in a cookie on the client's browser, cryptographically signed to prevent tampering.

### How It Works

```mermaid
graph LR
    A[Python dict<br/>session['user_id'] = 123] --> B[JSON Serialization]
    B --> C[Base64 Encoding]
    C --> D[HMAC-SHA256 Signature]
    D --> E[Cookie: session=data.signature]
    E --> F[Browser Storage]
    F --> G[Sent with each request]
    G --> H[Signature Verified]
    H --> I[Data Extracted]
```

1. You store data in `session` (a dictionary-like object)
2. Flask serializes the data to JSON
3. Base64-encodes the JSON
4. Computes a signature using `SECRET_KEY`
5. Sends the `session` cookie: `base64_data.signature`
6. On the next request, Flask verifies the signature
7. If valid, decodes and deserializes the data
8. If invalid, the session is discarded (empty dict)

> [!WARNING]
> The session data is **signed** (tamper-proof) but **not encrypted** (readable by the client). Never store sensitive information (passwords, credit card numbers, personal data) in Flask's client-side session.

## Using the Session

### Storing Data

```python
from flask import session

@app.route('/login', methods=['POST'])
def login():
    # ... validate credentials ...
    session['user_id'] = user.id
    session['username'] = user.username
    session.permanent = True  # Use PERMANENT_SESSION_LIFETIME
    return redirect(url_for('dashboard'))
```

### Retrieving Data

```python
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login'))
    
    username = session.get('username', 'Anonymous')
    return f'Welcome, {username}!'
```

### Removing Data

```python
@app.route('/logout')
def logout():
    session.pop('user_id', None)      # Remove one key
    session.pop('username', None)
    # Or clear everything:
    session.clear()                    # Remove all session data
    return redirect(url_for('index'))
```

### Checking for Keys

```python
if 'user_id' in session:
    # User is logged in
    pass

# Or
user_id = session.get('user_id')
if user_id is not None:
    pass
```

## Session Configuration

| Key | Default | Description |
|-----|---------|-------------|
| `SECRET_KEY` | `None` | Key for signing session cookies (**required**) |
| `SESSION_COOKIE_NAME` | `'session'` | Name of the session cookie |
| `SESSION_COOKIE_DOMAIN` | `None` | Cookie domain |
| `SESSION_COOKIE_PATH` | `None` | Cookie path |
| `SESSION_COOKIE_HTTPONLY` | `True` | Prevent JavaScript access |
| `SESSION_COOKIE_SECURE` | `False` | HTTPS only |
| `SESSION_COOKIE_SAMESITE` | `'Lax'` | CSRF protection |
| `PERMANENT_SESSION_LIFETIME` | `timedelta(days=31)` | Session duration |
| `SESSION_REFRESH_EACH_REQUEST` | `True` | Refresh cookie on every request |

### Secure Session Configuration

```python
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY'),  # Generate: secrets.token_hex(32)
    
    # Cookie security
    SESSION_COOKIE_HTTPONLY=True,    # Prevent XSS theft
    SESSION_COOKIE_SECURE=True,      # HTTPS only (production)
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
    
    # Session lifetime
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
)
```

### Permanent Sessions

By default, session cookies are **session cookies** — they expire when the browser closes. To make them persistent:

```python
@app.route('/login')
def login():
    session['user_id'] = user.id
    session.permanent = True  # Cookie uses PERMANENT_SESSION_LIFETIME
    return redirect(url_for('dashboard'))
```

## Session Security

### The Signing Process

Flask uses **itsdangerous** to sign session data:

```python
# Simplified signing process
import json, base64, hmac, hashlib

data = json.dumps({'user_id': 123})
encoded = base64.b64encode(data.encode()).decode()
signature = hmac.new(secret_key.encode(), encoded.encode(), 'sha256').hexdigest()
cookie_value = f'{encoded}.{signature}'
```

The signature ensures:
- **Integrity**: Data has not been modified
- **Authenticity**: Data was signed by your server

But not:
- **Confidentiality**: Data is readable by the client

### Security Threats

| Threat | Description | Mitigation |
|--------|-------------|------------|
| **Session forgery** | Attacker creates fake session | Strong SECRET_KEY, keep it secret |
| **Session theft** | Attacker steals cookie via XSS | HttpOnly, Secure, SameSite |
| **Session fixation** | Attacker forces known session ID | Regenerate session on login |
| **Replay attack** | Reuse old signed data | Short session lifetime |

### Regenerating Session on Login

Prevent session fixation attacks by clearing the session on login:

```python
from flask import session

@app.route('/login', methods=['POST'])
def login():
    # Clear any existing session data
    session.clear()
    
    # ... validate credentials ...
    
    # Set new session data
    session['user_id'] = user.id
    session.permanent = True
    return redirect(url_for('dashboard'))
```

## Server-Side Sessions

For applications that need to store sensitive data or require session invalidation:

### Flask-Session Extension

```python
from flask import Flask
from flask_session import Session

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379/0')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'flask_session:'
Session(app)
```

Session types: `redis`, `memcached`, `filesystem`, `mongodb`, `sqlalchemy`

### Manual Server-Side Session

```python
import uuid
from flask import session
from database import SessionStore  # Your session storage

@app.route('/login')
def login():
    # ... validate credentials ...
    
    # Create server-side session
    session_id = str(uuid.uuid4())
    SessionStore.set(session_id, {
        'user_id': user.id,
        'username': user.username,
        'created_at': datetime.now(UTC).isoformat()
    }, ttl=3600)
    
    # Store only the session ID in the cookie
    session['sid'] = session_id
    return redirect(url_for('dashboard'))
```

## Session Internals

### Session Interface

Flask's session system is pluggable through the `session_interface` attribute:

```python
class SecureCookieSessionInterface:
    """Default session interface using signed cookies."""
    
    def open_session(self, app, request):
        # Read session cookie from request
        # Verify signature and deserialize
        # Return session dict
    
    def save_session(self, app, session, response):
        # Serialize session data
        # Sign with SECRET_KEY
        # Set session cookie on response
```

You can implement a custom session interface for server-side sessions, JWT-based sessions, or other mechanisms.

## Common Mistakes

**Mistake: Storing sensitive data in client-side sessions**
Session data is readable by the client. Never store passwords, API keys, or personal information.

**Mistake: Using a weak SECRET_KEY**
`SECRET_KEY = 'dev'` or `SECRET_KEY = 'change-me'` allows anyone to forge session cookies.

```python
import secrets
secret_key = secrets.token_hex(32)  # Generate a secure key
```

**Mistake: Not setting HttpOnly, Secure, SameSite**
These attributes prevent XSS, network sniffing, and CSRF attacks. Always set them in production.

**Mistake: Sessions that never expire**
Set `PERMANENT_SESSION_LIFETIME` to limit the window for session theft.

## Best Practices

- Generate a strong, random `SECRET_KEY` for each environment
- Never commit `SECRET_KEY` to version control
- Set `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SECURE=True` (production), `SESSION_COOKIE_SAMESITE='Lax'`
- Clear and regenerate session on login (prevent fixation)
- Set a reasonable session lifetime (hours, not months)
- Store only identifiers (user_id) in sessions, not full objects
- Use server-side sessions for sensitive applications
- Implement logout (clear session) on all authenticated apps

## Exercises

1. **Session Counter**: Create a route that counts how many times a user has visited it using session storage.

2. **Secure Login**: Implement a login/logout system with proper session handling — regenerate on login, clear on logout, secure cookie settings.

3. **Session Inspector**: Create a debug route (development only) that displays the current session contents.

4. **Server-Side Session**: Implement a simple server-side session using a dictionary (not Redis) with expiration.

## Quiz

**Question 1**: How does Flask's default session system work? What are its security properties?

**Question 2**: What is the difference between a signed session and an encrypted session?

**Question 3**: Why should you regenerate the session on login?

**Question 4**: What do the `HttpOnly`, `Secure`, and `SameSite` cookie attributes protect against?

**Question 5**: When would you use server-side sessions instead of client-side sessions?

## Interview Questions

1. "Explain how Flask's session system works. How is session data stored and secured?"

2. "What is the difference between client-side and server-side sessions? When would you use each?"

3. "A user reports that their session expires too quickly. How would you diagnose and fix this?"

4. "How would you implement 'log out all devices' functionality in Flask?"

5. "What security measures should you take when configuring Flask sessions for production?"

## Related Chapters

- Previous: [[01-Flask-Core/Configuration]]
- [[01-Flask-Core/Cookies]] — Cookie management details
- [[04-Authentication/Flask-Login]] — Production authentication system
- [[08-Security/Session-Security]] — Advanced session security
- [[Appendix/itsdangerous]] — The library behind session signing

## Official Documentation References

- [Flask Sessions](https://flask.palletsprojects.com/en/latest/quickstart/#sessions)
- [Flask Session Interface](https://flask.palletsprojects.com/en/latest/api/#session-interface)
- [Flask-Session Extension](https://flask-session.readthedocs.io/)
- [itsdangerous Documentation](https://itsdangerous.palletsprojects.com/)

---

*Previous: [[01-Flask-Core/Configuration]] | Next: [[01-Flask-Core/Cookies]]*