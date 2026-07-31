---
title: JWT Authentication
description: Token-based authentication for Flask APIs using JSON Web Tokens
chapter: 10-Advanced
tags:
  - jwt
  - authentication
  - tokens
  - api-security
  - flask-jwt-extended
difficulty: Advanced
prerequisites:
  - [[10-Advanced/REST-API-Development]]
  - [[04-Authentication/Authentication-Overview]]
---

# JWT Authentication

> JSON Web Tokens (JWT) provide a stateless authentication mechanism ideal for APIs and single-page applications. Unlike session-based authentication, JWT tokens are self-contained and do not require server-side storage. This chapter covers implementing JWT authentication in Flask applications.

## Learning Objectives

After completing this chapter, you will be able to:

- Explain JWT structure and how token-based authentication works
- Implement JWT authentication using Flask-JWT-Extended
- Configure token expiration, refresh, and blacklisting
- Protect API routes with JWT required decorators
- Implement refresh token rotation for enhanced security
- Understand JWT security considerations and best practices

## What Is JWT?

A JSON Web Token is a compact, self-contained way of transmitting information between parties as a JSON object. JWTs are digitally signed using a secret or public/private key pair.

### JWT Structure

```
header.payload.signature

Example:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ
.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Header:** Contains algorithm and token type
```json
{"alg": "HS256", "typ": "JWT"}
```

**Payload:** Contains claims (user data, expiration, etc.)
```json
{"sub": "user_id", "name": "John", "iat": 1516239022, "exp": 1516242622}
```

**Signature:** Ensures token integrity
```
HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)
```

## Flask-JWT-Extended

Flask-JWT-Extended is the recommended JWT library for Flask.

### Installation and Setup

```bash
pip install flask-jwt-extended
```

```python
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change in production!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

jwt = JWTManager(app)
```

### Login and Token Creation

```python
from flask import request, jsonify
from werkzeug.security import check_password_hash

@app.route('/api/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    })
```

### Protecting Routes

```python
@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({'user': user.username})

@app.route('/api/admin-only', methods=['GET'])
@jwt_required()
def admin_only():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    return jsonify({'message': 'Admin data'})
```

### Token Refresh

```python
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token

@app.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': new_token})
```

### Revoking Tokens (Logout)

```python
from flask_jwt_extended import get_jwt

# Store revoked tokens in Redis or database
revoked_tokens = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in revoked_tokens

@app.route('/api/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    revoked_tokens.add(jti)
    return jsonify({'message': 'Successfully logged out'})
```

## Token Storage in Clients

### Web Applications (SPAs)

Store tokens in `memory` (not localStorage due to XSS risk):

```javascript
// Store in memory (lost on page refresh)
let accessToken = null;

function login(email, password) {
    return fetch('/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
    })
    .then(res => res.json())
    .then(data => {
        accessToken = data.access_token;
        // Store refresh token in httpOnly cookie
    });
}

function apiRequest(url, options = {}) {
    return fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${accessToken}`
        }
    });
}
```

### Mobile Applications

Use secure storage (Keychain on iOS, Keystore on Android).

## JWT Security Best Practices

### 1. Use Strong Secrets

```python
import secrets
app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
```

### 2. Short Token Lifetimes

```python
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
```

### 3. HTTPS Only

```python
app.config['JWT_COOKIE_SECURE'] = True  # HTTPS only
```

### 4. Token Blacklisting

Implement token revocation for logout and account security.

### 5. Include Minimal Data in Token

```python
# Good: Store only user ID
access_token = create_access_token(identity=user.id)

# Bad: Don't store sensitive data
create_access_token(identity={'id': user.id, 'role': user.role})  # Keep it simple
```

### 6. Use Appropriate Algorithms

```python
# Use HS256 for symmetric (single server) or RS256 for asymmetric (multiple servers)
app.config['JWT_ALGORITHM'] = 'HS256'
```

## Common Mistakes

**Mistake: Storing JWT in localStorage**
Vulnerable to XSS attacks. Use httpOnly cookies or memory storage.

**Mistake: Long-lived access tokens**
If stolen, attacker has extended access. Use short-lived tokens with refresh.

**Mistake: Not validating tokens server-side**
Always use `@jwt_required()` on protected routes.

**Mistake: Storing sensitive data in JWT payload**
JWT payload is base64 encoded but not encrypted. Anyone can read it.

## Exercises

1. **Basic JWT**: Implement login with JWT tokens using Flask-JWT-Extended.

2. **Refresh Tokens**: Add refresh token functionality to your API.

3. **Token Blacklist**: Implement token revocation using Redis.

4. **Role-Based Access**: Add role-based access control using JWT claims.

5. **Frontend Integration**: Build a simple SPA that authenticates with your JWT API.

## Quiz

**Question 1**: What are the three parts of a JWT? What does each contain?

**Question 2**: What is the difference between an access token and a refresh token?

**Question 3**: Why should you not store JWTs in localStorage?

**Question 4**: How do you revoke a JWT before it expires?

**Question 5**: What is the purpose of the `jti` claim in JWT?

## Interview Questions

1. "Explain JWT authentication. How does it differ from session-based authentication?"

2. "What are the security considerations when using JWT?"

3. "How would you implement token refresh in a Flask application?"

4. "How do you handle JWT revocation (logout)?"

5. "Where should JWTs be stored in a web application? Why?"

## Related Chapters

- [[10-Advanced/REST-API-Development]] — API design
- [[04-Authentication/Flask-Login]] — Session-based authentication
- [[08-Security/Security-Overview]] — Security fundamentals

## Official Documentation References

- [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)
- [JWT.io](https://jwt.io/)
- [RFC 7519 - JSON Web Token](https://datatracker.ietf.org/doc/html/rfc7519)

---

*Previous: [[10-Advanced/REST-API-Development]] | Next: [[10-Advanced/WebSockets]]*