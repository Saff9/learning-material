---
title: Flask-JWT-Extended
tags:
  - flask
  - authentication
  - jwt
  - api
  - security
  - tokens
aliases:
  - Flask JWT Extended
  - FJE
  - JWT in Flask
  - Token-based auth in Flask
related:
  - "[[Flask-Login]]"
  - "[[Flask-SQLAlchemy]]"
  - "[[Marshmallow]]"
  - "[[Flask-CORS]]"
  - "[[Security-Best-Practices]]"
created: 2024-01-15
updated: 2024-01-15
---

# Flask-JWT-Extended

#flask #authentication #jwt #api #security #tokens

> [!info] The de facto JWT library for Flask
> Flask-JWT-Extended (FJE) adds JWT-based authentication to Flask. It provides `@jwt_required` decorators, `create_access_token` / `create_refresh_token` helpers, custom claims, blocklist support, and a clean API for handling both header-based and cookie-based tokens. If you're building a JSON API in Flask and need token auth, this is the package you reach for.

Where [[Flask-Login]] is for **session-based** auth (the server stores state and issues an opaque cookie), Flask-JWT-Extended is for **token-based** auth: the server issues a self-contained signed token, the client stores it (in `localStorage`, `sessionStorage`, or an HttpOnly cookie), and sends it with every request. The server verifies the signature and reads the user identity from the token itself — no session lookup needed.

---

## 1. Overview & Metaphor

### What is a JWT?

A **JSON Web Token** is a compact, URL-safe string that carries a JSON payload, signed by the issuer so the recipient can verify it hasn't been tampered with. It has three Base64URL-encoded parts separated by dots:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
|_________________HEADER________________|.________________PAYLOAD_______________|.____SIGNATURE____.
```

#### Header

```json
{ "alg": "HS256", "typ": "JWT" }
```

Tells the verifier which algorithm was used. **The `alg` field is also the source of the classic "alg confusion" attack** — see §7.

#### Payload

```json
{
  "sub": "1234567890",      // subject = user id
  "name": "Alice",
  "iat": 1516239022,         // issued at
  "exp": 1516242622,         // expiration
  "fresh": true              // FJE custom claim
}
```

Claims come in three flavors:
- **Registered** — defined by RFC 7519 (`sub`, `iat`, `exp`, `nbf`, `iss`, `aud`).
- **Private** — your app's own keys (`role`, `permissions`).
- **Public** — registered in the [IANA JWT registry](https://www.iana.org/assignments/jwt/jwt.xhtml).

#### Signature

```
HMACSHA256(base64url(header) + "." + base64url(payload), secret)
```

Anyone holding the secret can sign tokens; anyone holding the secret can verify them. (Asymmetric algorithms like RS256 use a private key to sign and a public key to verify.)

> [!tip] The metaphor
> A JWT is like a **paper passport**: it carries the holder's identity, an issuing authority's stamp (the signature), and an expiry date. Anyone who can read English can read it — JWTs are not encrypted by default, only signed. Anyone who has the issuing authority's stamp secret can forge a passport. Whoever holds the passport can present it anywhere that accepts it, until it expires or is revoked (which is the hard part — see §6).

### When to use JWT vs sessions

```mermaid
quadrantChart
    title Auth strategies: where each shines
    x-axis "Same-origin browser" --> "Cross-origin / mobile"
    y-axis "Stateful (server store)" --> "Stateless (token)"
    quadrant-1 "Mobile / API / stateless"
    quadrant-2 "Browser / stateless"
    quadrant-3 "Browser / stateful"
    quadrant-4 "Mobile / stateful"
    "Flask-Login sessions": [0.2, 0.25]
    "Flask-JWT-Extended (headers)": [0.7, 0.78]
    "Flask-JWT-Extended (HttpOnly cookies + CSRF)": [0.35, 0.75]
    "ItsDangerous signed tokens (DIY)": [0.6, 0.7]
    "OAuth2 / OIDC (Authlib)": [0.85, 0.85]
    "HTTP Basic Auth": [0.55, 0.6]
```

| Question | If yes, prefer |
|---|---|
| Server-rendered HTML templates? | Sessions ([[Flask-Login]]) |
| Single-page app on a different origin? | JWT (FJE) |
| Mobile client? | JWT (FJE) |
| Multiple backend services sharing one auth? | JWT (FJE) |
| Need to revoke sessions instantly? | Sessions ([[Flask-Login]]) |
| Want to scale horizontally without session store? | JWT (FJE) |
| Browser app, same-origin, mostly pages? | Sessions ([[Flask-Login]]) |

> [!warning] JWTs are NOT more secure than sessions
> JWTs trade statelessness for difficulty of revocation. If your threat model includes "user clicks logout and we need to immediately invalidate all outstanding tokens," you'll end up building a blocklist anyway — at which point you've reinvented sessions with extra steps. Pick JWTs because they fit your architecture, not because they're "more secure".

### What Flask-JWT-Extended adds

Raw `PyJWT` lets you `jwt.encode(...)` and `jwt.decode(...)` — but you have to wire the parsing, error handling, and `current_user` plumbing yourself. FJE gives you:

- `@jwt_required()` decorator for protected endpoints
- `create_access_token(identity, fresh=..., additional_claims=...)`
- `create_refresh_token(identity)`
- `current_user` proxy (via `get_current_user()`)
- `get_jwt()`, `get_jwt_identity()`, `get_jwt_request_location()`
- A `JWTManager` object with hooks for: expired tokens, revoked tokens, invalid tokens, custom user lookups, custom claims
- Built-in support for tokens in headers, cookies, query string, or JSON body
- CSRF protection when using cookies (double-submit pattern)

### What Flask-JWT-Extended does NOT do

| Concern | Who handles it |
|---|---|
| Password hashing | `werkzeug.security` |
| User storage | [[Flask-SQLAlchemy]] |
| Input validation / serialization | [[Marshmallow]] or `pydantic` |
| Rate limiting | [[Flask-Limiter]] |
| CORS (so the SPA can call you) | [[Flask-CORS]] |
| OAuth 2.0 / OIDC | `authlib` |

---

## 2. Installation

```bash
(venv) $ pip install Flask-JWT-Extended
```

Versions referenced in this note:

| Package | Version |
|---|---|
| Flask | 3.0.x |
| Flask-JWT-Extended | 4.6.x |
| PyJWT | 2.8.x (dependency) |

> [!warning] Flask-JWT-Extended 4.x breaking changes
> 4.0 dropped `user_identity_loader` and `user_claims_loader` callbacks — they're replaced by `additional_claims` as a function argument to `create_access_token` and a `@jwt.user_lookup_loader` callback. 4.5+ requires Python 3.8+. 4.6 added support for asymmetric algorithms (RS256, ES256, PS256, EdDSA) without custom configuration.

No native deps — `PyJWT` is pure Python for HMAC algorithms. For RS256/ES256, `cryptography` is required (auto-installed).

---

## 3. Configuration

### Minimal setup

```python
# app/extensions.py
from flask_jwt_extended import JWTManager

jwt = JWTManager()
```

```python
# app/__init__.py
from datetime import timedelta
from flask import Flask
from app.extensions import db, jwt

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "change-me-in-production"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]

    db.init_app(app)
    jwt.init_app(app)

    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
```

### All configuration options

| Option | Default | Description |
|---|---|---|
| `JWT_SECRET_KEY` | `None` | **Required.** Secret for HMAC algorithms. |
| `JWT_PUBLIC_KEY` | `None` | PEM-encoded public key for RS/ES/EdDSA. |
| `JWT_PRIVATE_KEY` | `None` | PEM-encoded private key for signing. |
| `JWT_ALGORITHM` | `"HS256"` | Signing algorithm. |
| `JWT_DECODE_ALGORITHMS` | `["HS256"]` | List of algorithms accepted on decode. **Do not include `"none"`.** |
| `JWT_TOKEN_LOCATION` | `["headers"]` | List of: `"headers"`, `"cookies"`, `"query_string"`, `"json"`. |
| `JWT_HEADER_NAME` | `"Authorization"` | Header name. |
| `JWT_HEADER_TYPE` | `"Bearer"` | Header prefix. Empty string for no prefix. |
| `JWT_ACCESS_TOKEN_EXPIRES` | `timedelta(minutes=15)` | Access token TTL. `False` for never-expiring. |
| `JWT_REFRESH_TOKEN_EXPIRES` | `timedelta(days=30)` | Refresh token TTL. `False` for never-expiring. |
| `JWT_IDENTITY_CLAIM` | `"sub"` | Claim name for the identity. Change if you need to interop with a system that uses a different claim. |
| `JWT_ERROR_MESSAGE_KEY` | `"msg"` | Key for error messages in JSON responses. |
| `JWT_COOKIE_NAME` | `"access_token_cookie"` | Cookie name for access tokens. |
| `JWT_REFRESH_COOKIE_NAME` | `"refresh_token_cookie"` | Cookie name for refresh tokens. |
| `JWT_COOKIE_SECURE` | `False` | If `True`, cookies only sent over HTTPS. **Set True in prod.** |
| `JWT_COOKIE_HTTPONLY` | `True` | If `True`, JS can't read the cookie. **Leave True.** |
| `JWT_COOKIE_DOMAIN` | `None` | Cookie domain. |
| `JWT_COOKIE_SAMESITE` | `"Lax"` | `"Strict"`, `"Lax"`, or `None`. |
| `JWT_CSRF_PROTECTION` | `False` | If `True`, enable CSRF for cookie-based tokens. **Recommended for cookies.** |
| `JWT_CSRF_METHODS` | `["POST", "PUT", "PATCH", "DELETE"]` | Methods that require CSRF check. |
| `JWT_CSRF_HEADER_NAME` | `"X-CSRF-Token"` | Header name for the CSRF token. |
| `JWT_CSRF_IN_COOKIES` | `True` | If `True`, set a separate CSRF cookie. |
| `JWT_CSRF_FIELD_NAME` | `"csrf_token"` | Form field name (if using forms). |
| `JWT_QUERY_STRING_NAME` | `"jwt"` | Query string parameter name. |
| `JWT_QUERY_STRING_VALUE_PREFIX` | `""` | Optional prefix for query string tokens. |
| `JWT_JSON_KEY` | `"access_token"` | JSON body key for access token. |
| `JWT_REFRESH_JSON_KEY` | `"refresh_token"` | JSON body key for refresh token. |
| `JWT_DECODE_AUDIENCE` | `None` | Expected `aud` claim. |
| `JWT_ENCODE_AUDIENCE` | `None` | `aud` claim to encode. |
| `JWT_ENCODE_ISSUER` | `None` | `iss` claim to encode. |
| `JWT_DECODE_ISSUER` | `None` | Expected `iss` claim on decode. |
| `JWT_ENCODE_NBF` | `True` | If `True`, encode a `nbf` (not-before) claim. |
| `JWT_LEEWAY` | `0` | Seconds of leeway for time-based claims (clock skew). |
| `JWT_SECRET_KEY_FALLBACKS` | `[]` | List of old secrets, for rotation. |

> [!danger] Never set `JWT_DECODE_ALGORITHMS` to include `"none"`
> The "alg: none" attack is the most famous JWT vulnerability: an attacker takes a valid token, sets `alg` to `none`, removes the signature, and the server accepts it. PyJWT refuses `none` by default — do **not** override this by adding it to `JWT_DECODE_ALGORITHMS`. Also: never let the client choose the algorithm.

### Production config

```python
# app/config.py
import os
from datetime import timedelta

class Config:
    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_CSRF_PROTECTION = True
    JWT_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
```

### Algorithm choice

| Algorithm | Key type | Use when |
|---|---|---|
| `HS256` / `HS384` / `HS512` | Symmetric (shared secret) | Single service. Simplest. |
| `RS256` / `RS384` / `RS512` | RSA public/private | Multi-service: one issuer signs, many verifiers check with the public key. |
| `ES256` / `ES384` | ECDSA | Same as RS256 but smaller signatures. |
| `EdDSA` | Ed25519 | Modern, fast, small signatures. |
| `PS256` | RSASSA-PSS | More secure RSA variant. |

```python
# Asymmetric example (RS256)
app.config["JWT_ALGORITHM"] = "RS256"
with open("private.pem") as f:
    app.config["JWT_PRIVATE_KEY"] = f.read()
with open("public.pem") as f:
    app.config["JWT_PUBLIC_KEY"] = f.read()
```

---

## 4. Basic Usage

### The three primitives

| Function | Purpose |
|---|---|
| `create_access_token(identity, fresh=False, additional_claims=None)` | Returns a short-lived access token string. |
| `create_refresh_token(identity, additional_claims=None)` | Returns a long-lived refresh token. Use once per access-token expiry. |
| `@jwt_required()` | Decorator that 401s if no valid token is present. |
| `get_jwt_identity()` | Returns the `sub` claim from the current token. |
| `get_jwt()` | Returns the full decoded claims dict. |
| `current_user` | Object returned by your `user_lookup_loader` — see §5. |

### A minimal login endpoint

```python
# app/api/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity,
)
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify(msg="missing credentials"), 400

    user = db.session.scalar(db.select(User).where(User.email == email))
    if not user or not user.check_password(password):
        return jsonify(msg="bad credentials"), 401

    access = create_access_token(identity=str(user.id), fresh=True)
    refresh = create_refresh_token(identity=str(user.id))
    return jsonify(access_token=access, refresh_token=refresh), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity, fresh=False)
    return jsonify(access_token=access), 200


@auth_bp.post("/logout")
@jwt_required()
def logout():
    return jsonify(msg="logged out"), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    return jsonify(id=user.id, email=user.email, username=user.username), 200
```

### Client-side usage

```bash
# Login
$ curl -X POST http://localhost:5000/api/login \
    -H "Content-Type: application/json" \
    -d '{"email":"alice@example.com","password":"password123"}'

# Response:
# {"access_token":"eyJ...","refresh_token":"eyJ..."}

# Call protected endpoint
$ curl http://localhost:5000/api/me \
    -H "Authorization: Bearer eyJ..."
```

### Token in cookies

Switch to cookies when you want to protect against XSS stealing tokens from `localStorage`:

```python
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_COOKIE_HTTPONLY"] = True
app.config["JWT_CSRF_PROTECTION"] = True
```

```python
from flask import jsonify, make_response
from flask_jwt_extended import set_access_cookies, set_refresh_cookies, unset_jwt_cookies

@auth_bp.post("/login")
def login():
    # ... validate user ...
    access = create_access_token(identity=str(user.id), fresh=True)
    refresh = create_refresh_token(identity=str(user.id))
    resp = jsonify(msg="logged in")
    set_access_cookies(resp, access)
    set_refresh_cookies(resp, refresh)
    return resp


@auth_bp.post("/logout")
def logout():
    resp = jsonify(msg="logged out")
    unset_jwt_cookies(resp)
    return resp
```

CSRF tokens are now automatically generated and verified for state-changing requests. The frontend must read the CSRF cookie and send its value as `X-CSRF-Token` on POST/PUT/PATCH/DELETE.

### The access/refresh flow

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant DB as Database

    C->>S: POST /login {email, password}
    S->>DB: verify password
    DB-->>S: ok
    S->>S: create_access_token(fresh=True, 15m)
    S->>S: create_refresh_token(30d)
    S-->>C: {access_token, refresh_token}

    Note over C: ... 15 min later, access token expires ...

    C->>S: GET /me (expired access token)
    S-->>C: 401 token expired

    C->>S: POST /refresh (refresh token)
    S->>S: verify refresh token
    S->>S: create_access_token(fresh=False, 15m)
    S-->>C: {access_token}

    C->>S: GET /me (new access token)
    S-->>C: 200 {user data}

    Note over C: ... user logs out ...

    C->>S: POST /logout (access token)
    S->>S: add token jti to blocklist
    S-->>C: 200 logged out
```

---

## 5. Intermediate Patterns

### `current_user` via `user_lookup_loader`

Instead of doing `db.session.get(User, int(get_jwt_identity()))` in every endpoint, register a loader:

```python
# app/extensions.py
from flask_jwt_extended import JWTManager
from app.models.user import User
from app.extensions import db

jwt = JWTManager()


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.session.get(User, int(identity))


@jwt.token_in_blocklist_loader
def check_if_token_revoked(_jwt_header, jwt_data):
    jti = jwt_data["jti"]
    return TokenBlocklist.is_revoked(jti)   # see §6
```

Now in your views:

```python
from flask_jwt_extended import current_user

@auth_bp.get("/profile")
@jwt_required()
def profile():
    return jsonify(username=current_user.username, email=current_user.email)
```

If the loader returns `None`, FJE returns 401 with `"user not found"`.

### Custom claims

Add extra data to a token without a DB lookup later:

```python
def make_admin_claims(user):
    return {"role": user.role, "permissions": user.permissions_list()}

@auth_bp.post("/login")
def login():
    # ... verify ...
    additional = make_admin_claims(user)
    access = create_access_token(
        identity=str(user.id),
        fresh=True,
        additional_claims=additional,
    )
    return jsonify(access_token=access)
```

Read them back:

```python
from flask_jwt_extended import get_jwt

@app.get("/admin")
@jwt_required()
def admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify(msg="forbidden"), 403
    ...
```

> [!warning] Claims are not for sensitive data
> JWTs are **base64-encoded, not encrypted**. Anyone who can read the token (e.g., browser devtools, network proxy) can read the claims. Never put passwords, secrets, or PII in claims.

### Custom decorators

Build role-checking on top of `@jwt_required()`:

```python
# app/api/decorators.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify(msg="admins only"), 403
        return fn(*args, **kwargs)
    return wrapper


def permission_required(*perms: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_perms = set(claims.get("permissions", []))
            if not user_perms.issuperset(perms):
                return jsonify(msg=f"missing permissions: {set(perms) - user_perms}"), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# usage
@api_bp.delete("/users/<int:user_id>")
@admin_required
def delete_user(user_id):
    ...
```

### Multiple token locations

Accept tokens from headers *or* query string (useful for SSE / WebSocket URLs that can't set headers):

```python
app.config["JWT_TOKEN_LOCATION"] = ["headers", "query_string"]
app.config["JWT_QUERY_STRING_NAME"] = "access_token"

# Frontend:
# const url = `/stream?access_token=${token}`;
# const es = new EventSource(url);
```

> [!warning] Tokens in query strings get logged
> Web server access logs, browser history, and proxy logs all record query strings. Only use this when you must (e.g., EventSource), and use short-lived tokens. Rotate secrets if logs leak.

### Custom error responses

```python
@jwt.expired_token_loader
def expired_token_callback(_jwt_header, _jwt_data):
    return jsonify(msg="token expired", code="token_expired"), 401


@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify(msg="invalid token", reason=reason, code="token_invalid"), 401


@jwt.unauthorized_loader
def missing_token_callback(reason):
    return jsonify(msg="missing token", reason=reason, code="token_missing"), 401


@jwt.revoked_token_loader
def revoked_token_callback(_jwt_header, _jwt_data):
    return jsonify(msg="token revoked", code="token_revoked"), 401


@jwt.needs_fresh_token_loader
def needs_fresh_callback(_jwt_header, _jwt_data):
    return jsonify(msg="fresh token required", code="token_not_fresh"), 401
```

These let you return machine-readable error codes your frontend can branch on.

---

## 6. Advanced Usage

### Fresh vs non-fresh tokens

A **fresh** token is one issued directly from `/login` (user typed credentials). A **non-fresh** token is one issued from `/refresh`. Sensitive endpoints can require freshness:

```python
@auth_bp.post("/change-password")
@jwt_required(fresh=True)
def change_password():
    ...
```

If the token is non-fresh, FJE calls your `needs_fresh_token_loader` and returns 401. The client should:

1. Detect the `token_not_fresh` code.
2. Prompt the user for their password.
3. POST `/login` (with password) to get a fresh access token.
4. Retry the original request.

### Blocklist (token revocation)

JWTs can't be "un-issued" — once signed, they're valid until `exp`. To support logout / force-logout, maintain a **blocklist** of revoked `jti` claims. The `jti` (JWT ID) is a unique identifier FJE adds to every token.

```mermaid
classDiagram
    class JWT_Token {
        +str header  base64\(alg, typ\)
        +str payload  base64\(claims\)
        +str signature
        +str sub
        +str jti
        +datetime iat
        +datetime exp
        +bool fresh
        +dict additional_claims
        +is_expired\(\) bool
    }
    class AccessToken {
        TTL: 15 min
        fresh: bool
        +used_by @jwt_required\(\)
        +used_by @jwt_required\(fresh=True\)
    }
    class RefreshToken {
        TTL: 7-30 days
        fresh: false
        +used_by @jwt_required\(refresh=True\)
        +rotated_on_use
    }
    class TokenBlocklist {
        +str jti PK
        +datetime expires_at
        +datetime created_at
        +is_revoked\(jti\) bool
        +prune\(\) int
    }
    class User {
        +int id
        +str email
        +str role
        +int token_version
        +check_password\(pw\) bool
    }

    JWT_Token <|-- AccessToken
    JWT_Token <|-- RefreshToken
    AccessToken "1" --> "0..*" TokenBlocklist : revoked via jti
    RefreshToken "1" --> "0..*" TokenBlocklist : revoked via jti\n(on rotation / logout)
    User "1" --> "0..*" AccessToken : sub claim
    User "1" --> "0..*" RefreshToken : sub claim

    note for TokenBlocklist "Redis SETEX jti <ttl> 1\nis the ideal backing store:\nO\(1\) lookup, auto-expire."
    note for User "Bumping token_version invalidates\nALL outstanding tokens for that user\n(logout-everywhere)."
```

```python
# app/models/token_blocklist.py
from datetime import datetime
from app.extensions import db


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)

    @classmethod
    def is_revoked(cls, jti: str) -> bool:
        row = db.session.scalar(
            db.select(cls).where(cls.jti == jti)
        )
        return row is not None

    @classmethod
    def prune(cls) -> int:
        """Delete expired entries. Run via a cron / Celery beat."""
        result = db.session.execute(
            db.delete(cls).where(cls.expires_at < datetime.utcnow())
        )
        db.session.commit()
        return result.rowcount
```

```python
# app/extensions.py
from datetime import datetime, timezone
from flask_jwt_extended import JWTManager
from app.models.token_blocklist import TokenBlocklist

jwt = JWTManager()


@jwt.token_in_blocklist_loader
def is_token_revoked(jwt_header, jwt_data):
    jti = jwt_data["jti"]
    return TokenBlocklist.is_revoked(jti)


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_data):
    return jsonify(msg="token revoked"), 401
```

```python
# app/api/auth.py
from datetime import datetime, timezone
from flask_jwt_extended import get_jwt

@auth_bp.post("/logout")
@jwt_required()
def logout():
    jwt_data = get_jwt()
    jti = jwt_data["jti"]
    exp = datetime.fromtimestamp(jwt_data["exp"], tz=timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, expires_at=exp))
    db.session.commit()
    return jsonify(msg="logged out"), 200


@auth_bp.post("/logout-refresh")
@jwt_required(refresh=True)
def logout_refresh():
    jwt_data = get_jwt()
    db.session.add(TokenBlocklist(
        jti=jwt_data["jti"],
        expires_at=datetime.fromtimestamp(jwt_data["exp"], tz=timezone.utc),
    ))
    db.session.commit()
    return jsonify(msg="refresh token revoked"), 200
```

> [!tip] Use Redis for the blocklist in production
> Each request hits the blocklist once. If you use Postgres, that's an extra DB round-trip per API call. Redis with `SETEX jti <ttl> 1` is ideal: lookup is O(1), entries auto-expire when the token would have expired anyway.

### "Log out everywhere"

```python
@auth_bp.post("/logout-all")
@jwt_required()
def logout_all():
    # Revoke ALL tokens for this user by tracking a "token version" on the user.
    user = current_user
    user.token_version = (user.token_version or 0) + 1
    db.session.commit()
    return jsonify(msg="all sessions revoked"), 200
```

Then include `ver` in claims:

```python
@jwt.additional_claims_loader
def add_claims(identity):
    user = db.session.get(User, int(identity))
    return {"ver": user.token_version}


@jwt.user_lookup_loader
def user_lookup(_h, jwt_data):
    user = db.session.get(User, int(jwt_data["sub"]))
    if not user or user.token_version != jwt_data.get("ver"):
        return None     # 401
    return user
```

Now bumping `token_version` invalidates every outstanding token instantly, without a blocklist lookup on every request.

### Custom claims via `additional_claims_loader`

If you want claims added to *every* token automatically:

```python
@jwt.additional_claims_loader
def make_claims(identity):
    user = db.session.get(User, int(identity))
    return {
        "role": user.role,
        "ver": user.token_version,
        "iss": "myapp",
    }
```

> [!warning] Don't use this for data that changes
> Claims are baked into the token at issue time. If `user.role` changes, outstanding tokens still have the old role until they expire. For dynamic permissions, look up `current_user` in the view and check against the DB.

### Asymmetric algorithms (RS256)

For multi-service setups where service A issues tokens and services B/C/D verify them:

```python
# Issuer (service A)
app.config["JWT_ALGORITHM"] = "RS256"
app.config["JWT_PRIVATE_KEY"] = open("/etc/secrets/jwt-private.pem").read()
app.config["JWT_PUBLIC_KEY"] = open("/etc/secrets/jwt-public.pem").read()  # for self-test

# Verifier (services B/C/D)
app.config["JWT_ALGORITHM"] = "RS256"
app.config["JWT_PUBLIC_KEY"] = open("/etc/secrets/jwt-public.pem").read()
# No private key — they only verify, never issue.
```

Distribute the public key widely; keep the private key on the issuer only.

### Refresh token rotation

To limit the damage if a refresh token is stolen, **rotate** it: each `/refresh` call returns a new refresh token and revokes the old one.

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant S as Server
    participant BL as Blocklist (Redis)
    participant DB as Database
    Note over C,S: Initial login hands out pair\n(access_a, refresh_a)
    Note over C: ... 15 min later ...
    C->>S: POST /refresh  Authorization: Bearer refresh_a
    S->>BL: is refresh_a.jti revoked?
    BL-->>S: no
    S->>DB: lookup user (sub)
    DB-->>S: User\ntoken_version=5
    S->>S: issue access_b (fresh=False, 15m)\nissue refresh_b (30d)
    S->>BL: SETEX refresh_a.jti <ttl> 1\n(revoke old refresh)
    S-->>C: { access_token: access_b, refresh_token: refresh_b }
    Note over C: Client stores refresh_b,\ndiscards refresh_a
    Note over C: Attacker replaying refresh_a:
    C->>S: POST /refresh  Authorization: Bearer refresh_a
    S->>BL: is refresh_a.jti revoked?
    BL-->>S: YES
    S->>S: REUSE DETECTED!\nRevoke entire chain for this user.
    S->>DB: user.token_version += 1\n(Invalidates refresh_b too.)
    S-->>C: 401 token_revoked\nPlease log in fresh.
```

```python
@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    jwt_data = get_jwt()
    # Revoke the old refresh token
    db.session.add(TokenBlocklist(
        jti=jwt_data["jti"],
        expires_at=datetime.fromtimestamp(jwt_data["exp"], tz=timezone.utc),
    ))

    identity = get_jwt_identity()
    new_access = create_access_token(identity=identity, fresh=False)
    new_refresh = create_refresh_token(identity=identity)
    db.session.commit()
    return jsonify(access_token=new_access, refresh_token=new_refresh), 200
```

Pair with **automatic reuse detection**: if a revoked refresh token is presented, that means an attacker stole it before the legitimate client used it. Revoke the entire chain (all refresh tokens for that user) and force a fresh login.

### Testing JWT-protected endpoints

```python
# tests/conftest.py
import pytest
from flask_jwt_extended import create_access_token
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app()
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="1", fresh=True)
    return {"Authorization": f"Bearer {token}"}


# tests/test_api.py
def test_me_requires_auth(client):
    assert client.get("/api/me").status_code == 401


def test_me_works_with_token(client, auth_headers):
    resp = client.get("/api/me", headers=auth_headers)
    assert resp.status_code == 200
```

> [!tip] Use short tokens in tests
> If tests create thousands of tokens, they slow down. You can monkeypatch `JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=1)` in test config so they don't pile up in your blocklist.

```mermaid
stateDiagram-v2
    [*] --> Issued: create_access_token / create_refresh_token
    Issued --> Valid: client presents token<br/>signature OK, not expired
    Valid --> Valid: each request<br/>blocklist checked
    Valid --> Used: logout -> jti added to blocklist
    Valid --> Expired: exp claim reached<br/>(no DB needed)
    Valid --> Rotated: /refresh returns new pair<br/>old refresh jti blocklisted
    Valid --> GloballyRevoked: user.token_version++<br/>ver claim mismatch -> 401
    Used --> [*]: expires_at reached<br/>prune job deletes row
    Expired --> [*]: client calls /refresh<br/>with refresh token
    Rotated --> Issued: new pair issued
    GloballyRevoked --> [*]: client must re-login
    Issued --> Rejected: bad signature<br/>or alg:none attack
    Rejected --> [*]: 401 token_invalid

    note right of Used
        Blocklist entries should auto-expire<br/>when the underlying token would have.<br/>Redis SETEX handles this for free.
    end note
    note right of GloballyRevoked
        "Logout everywhere" path.<br/>No per-token DB lookup needed —<br/>ver mismatch in user_lookup_loader.
    end note
```

---

## 7. Common Pitfalls & Troubleshooting

### Pitfall 1: "alg confusion" attack

**Symptom**: An attacker submits a token with `alg: none` and no signature, and the server accepts it.

**Cause**: Including `"none"` in `JWT_DECODE_ALGORITHMS`, or letting the client choose the algorithm.

**Fix**: PyJWT refuses `none` by default. Never override this. Always specify `JWT_ALGORITHM` server-side.

### Pitfall 2: Weak secret

If `JWT_SECRET_KEY` is `"secret"` or `"changeme"`, an attacker can forge tokens. Use:

```bash
$ python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Store in env var / secrets manager. Rotate yearly.

### Pitfall 3: Storing tokens in `localStorage` (XSS)

`localStorage` is readable by JavaScript — including any XSS payload that slips into your app. If you must store tokens client-side, prefer:
1. **HttpOnly cookies** with CSRF protection (FJE's built-in pattern).
2. **In-memory** (JS variable) — survives only until page reload, but immune to XSS theft.

`sessionStorage` is also vulnerable to XSS.

### Pitfall 4: Refresh tokens never expire

`JWT_REFRESH_TOKEN_EXPIRES = False` means a stolen refresh token works forever. Don't. Use 7-30 days max, with rotation.

### Pitfall 5: `get_jwt_identity()` returns a string

`identity` is whatever you passed to `create_access_token`. If you passed an `int`, you get back an `int`. If you passed a `str` (recommended for safety), you get a `str` — and need to cast it back:

```python
user_id = int(get_jwt_identity())  # if you stored str(user.id)
```

### Pitfall 6: Blocklist lookup on every request is slow

Each request does a DB query. Solutions:
- Use Redis with `SETEX` so entries auto-expire.
- Use the "token version" pattern (§6) for instant global revocation without per-request DB lookups.
- Cache negative results in `flask_caching`.

### Pitfall 7: CORS blocks the JWT header

If your SPA is on `app.example.com` and the API is on `api.example.com`, the browser won't send `Authorization` headers unless CORS allows them:

```python
from flask_cors import CORS
CORS(app, origins=["https://app.example.com"], supports_credentials=True)
```

`supports_credentials=True` is required if you use cookie-based tokens. See [[Flask-CORS]].

### Pitfall 8: CSRF cookie-based tokens fail with cross-origin

The double-submit CSRF pattern requires the frontend to read a CSRF cookie and send its value as a header. Cookies aren't readable cross-origin unless `Access-Control-Allow-Credentials: true` AND the cookie's domain matches. The simplest fix is to serve the SPA and the API on the same origin (e.g., via a reverse proxy).

### Pitfall 9: Tokens valid after password change

JWTs are stateless — changing the password doesn't invalidate outstanding tokens. Use the "token version" pattern (§6) or blocklist all tokens for the user on password change.

### Pitfall 10: `JWT_SECRET_KEY` rotation logs everyone out

Rotating the secret invalidates every outstanding token. Use `JWT_SECRET_KEY_FALLBACKS` (FJE 4.6+) to support old tokens during the transition window:

```python
app.config["JWT_SECRET_KEY"] = new_secret
app.config["JWT_SECRET_KEY_FALLBACKS"] = [old_secret_1, old_secret_2]
```

### Troubleshooting flowchart

```mermaid
flowchart TD
    A[401 from /api endpoint] --> B{Response code?}
    B -- token_missing --> C[Frontend not sending Authorization header]
    B -- token_invalid --> D[Signature wrong: SECRET_KEY mismatch?<br/>alg mismatch?]
    B -- token_expired --> E[Access token expired; call /refresh]
    B -- token_revoked --> F[Token on blocklist; user logged out]
    B -- token_not_fresh --> G[Hit a fresh-required endpoint;<br/>re-auth with password]
    B -- user_not_found --> H[user_lookup_loader returned None]
```

---

## 8. Best Practices

### Token lifetime

| Token type | Recommended TTL |
|---|---|
| Access token | 5–15 minutes |
| Refresh token | 7–30 days |
| "Remember me" refresh | 30–90 days |

Short access tokens limit the damage if one is stolen. Long refresh tokens avoid annoying re-logins.

### Storage

| Storage | XSS-safe | CSRF-safe | Verdict |
|---|---|---|---|
| `localStorage` | ❌ | ✅ | Use only if XSS surface is minimal |
| `sessionStorage` | ❌ | ✅ | Same as localStorage; cleared on tab close |
| HttpOnly cookie | ✅ | ❌ (needs CSRF) | **Recommended for web SPAs** |
| In-memory JS variable | ✅ | ✅ | Best for very sensitive apps; lost on refresh |

### Blocklist

- Always use one for logout to work.
- Redis > Postgres for performance.
- Auto-expire entries when the underlying token would have expired (`SETEX`).
- Add a periodic prune job (`TokenBlocklist.prune()`).

### Algorithm

- Single-service: HS256 with a strong secret.
- Multi-service: RS256 or EdDSA. Keep the private key on the issuer only.
- Never `none`. Never let the client pick the algorithm.

### Identity

- Use a stable, opaque ID (the user's PK as a string is fine).
- Don't use email — it can change.
- Don't put sensitive data in the payload.

### Claims

- Put authorization-relevant, slow-changing data in claims (e.g., `role`, `tenant_id`).
- Put fast-changing data in the DB (e.g., `balance`, `is_active`).
- Always look up `current_user` from DB for the latest state.

### Logging out

- Always revoke the access token's `jti` in the blocklist (even though it expires in 15 min — the user expects logout to be immediate).
- Always revoke the refresh token's `jti` separately.
- Support "logout everywhere" via token versioning.

### Security headers

Set on all responses:

```
Strict-Transport-Security: max-age=63072000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: <restrictive policy>
```

See [[Security-Best-Practices]].

---

## 9. Integration with Other Flask Extensions

### With [[Flask-SQLAlchemy]]

The user model and blocklist model are both `db.Model`s. See §6.

### With [[Marshmallow]]

Validate login input and serialize output:

```python
from marshmallow import Schema, fields, validates, ValidationError

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda p: len(p) >= 8)


@auth_bp.post("/login")
def login():
    try:
        data = LoginSchema().load(request.get_json() or {})
    except ValidationError as e:
        return jsonify(errors=e.messages), 400
    # ... verify ...
```

### With [[Flask-CORS]]

If your API is on a different origin from your SPA:

```python
from flask_cors import CORS
CORS(app, origins=["https://app.example.com"], supports_credentials=True)
```

`supports_credentials=True` is **required** for cookie-based JWTs. See [[Flask-CORS]].

### With [[Flask-Limiter]]

Rate-limit login attempts to prevent brute force:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@auth_bp.post("/login")
@limiter.limit("5/minute;20/hour")
def login():
    ...
```

### With [[Flask-Login]]

You can run both: sessions for the web UI, JWTs for the API. Use [[Flask-Login]] for `/` routes and `@jwt_required()` for `/api/*`. Don't try to share auth state.

### With [[Celery]]

Pass the JWT to a background task and re-verify it there:

```python
@shared_task
def send_report(user_id: int):
    # Background tasks usually don't need the JWT — just the user_id.
    # But if you need to call another API on behalf of the user:
    token = create_access_token(identity=str(user_id), fresh=False)
    requests.post("https://api.internal/...", headers={"Authorization": f"Bearer {token}"})
```

### With [[Flask-SocketIO]]

For WebSocket auth, you can't set headers on the initial connection. Use query string:

```python
app.config["JWT_TOKEN_LOCATION"] = ["headers", "query_string"]

@socketio.on("connect")
@jwt_required(locations=["query_string"])
def on_connect():
    user = current_user
    join_room(f"user-{user.id}")
```

---

## 10. Real-World Example

A complete auth system: register, login, refresh, logout (with blocklist), protected route, admin route, password change requiring fresh token.

```python
# app.py  — single-file runnable example
import os
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt, get_jwt_identity, current_user,
    verify_jwt_in_request,
)
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
jwt = JWTManager()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), default="user", nullable=False)
    token_version = db.Column(db.Integer, default=0, nullable=False)

    def set_password(self, p): self.password_hash = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password_hash, p)


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)

    @classmethod
    def is_revoked(cls, jti):
        return db.session.scalar(db.select(cls).where(cls.jti == jti)) is not None


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]

    db.init_app(app)
    jwt.init_app(app)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return str(user)

    @jwt.user_lookup_loader
    def user_lookup(_h, jwt_data):
        user = db.session.get(User, int(jwt_data["sub"]))
        if not user or user.token_version != jwt_data.get("ver", 0):
            return None
        return user

    @jwt.additional_claims_loader
    def add_claims(identity):
        user = db.session.get(User, int(identity))
        return {"role": user.role, "ver": user.token_version}

    @jwt.token_in_blocklist_loader
    def is_revoked(_h, jwt_data):
        return TokenBlocklist.is_revoked(jwt_data["jti"])

    # ---------- routes ----------

    @app.post("/register")
    def register():
        data = request.get_json() or {}
        if not data.get("email") or not data.get("password"):
            return jsonify(msg="email and password required"), 400
        if User.query.filter_by(email=data["email"]).first():
            return jsonify(msg="email already registered"), 409
        u = User(email=data["email"], role=data.get("role", "user"))
        u.set_password(data["password"])
        db.session.add(u)
        db.session.commit()
        return jsonify(id=u.id, email=u.email), 201

    @app.post("/login")
    def login():
        data = request.get_json() or {}
        u = User.query.filter_by(email=data.get("email")).first()
        if not u or not u.check_password(data.get("password", "")):
            return jsonify(msg="bad credentials"), 401
        access = create_access_token(identity=u.id, fresh=True)
        refresh = create_refresh_token(identity=u.id)
        return jsonify(access_token=access, refresh_token=refresh)

    @app.post("/refresh")
    @jwt_required(refresh=True)
    def refresh():
        # Rotate: revoke the old refresh token, issue a new pair.
        jwt_data = get_jwt()
        db.session.add(TokenBlocklist(
            jti=jwt_data["jti"],
            expires_at=datetime.fromtimestamp(jwt_data["exp"], tz=timezone.utc),
        ))
        identity = get_jwt_identity()
        new_access = create_access_token(identity=identity, fresh=False)
        new_refresh = create_refresh_token(identity=identity)
        db.session.commit()
        return jsonify(access_token=new_access, refresh_token=new_refresh)

    @app.post("/logout")
    @jwt_required()
    def logout():
        jwt_data = get_jwt()
        db.session.add(TokenBlocklist(
            jti=jwt_data["jti"],
            expires_at=datetime.fromtimestamp(jwt_data["exp"], tz=timezone.utc),
        ))
        db.session.commit()
        return jsonify(msg="access token revoked")

    @app.post("/logout-all")
    @jwt_required()
    def logout_all():
        u = current_user
        u.token_version += 1
        db.session.commit()
        return jsonify(msg=f"all tokens for user {u.id} revoked")

    @app.get("/me")
    @jwt_required()
    def me():
        return jsonify(id=current_user.id, email=current_user.email, role=current_user.role)

    @app.post("/change-password")
    @jwt_required(fresh=True)
    def change_password():
        data = request.get_json() or {}
        if not current_user.check_password(data.get("old", "")):
            return jsonify(msg="current password is wrong"), 403
        current_user.set_password(data["new"])
        current_user.token_version += 1   # invalidate all old tokens
        db.session.commit()
        return jsonify(msg="password changed; please log in again")

    # ---------- admin ----------

    from functools import wraps
    def admin_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            if get_jwt().get("role") != "admin":
                return jsonify(msg="admin only"), 403
            return fn(*args, **kwargs)
        return wrapper

    @app.get("/admin/users")
    @admin_required
    def list_users():
        return jsonify(users=[{"id": u.id, "email": u.email, "role": u.role}
                              for u in User.query.all()])

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
```

```bash
$ python app.py
# In another terminal:
$ http POST :5000/register email=alice@example.com password=password123
$ http POST :5000/register email=bob@example.com password=password123 role=admin
$ http POST :5000/login email=alice@example.com password=password123
# Copy access_token and refresh_token from response
$ http :5000/me "Authorization: Bearer <access_token>"
$ http POST :5000/refresh "Authorization: Bearer <refresh_token>"
$ http POST :5000/logout "Authorization: Bearer <access_token>"
# Now /me returns 401 token_revoked
```

This example demonstrates:

- `additional_claims_loader` for `role` and `ver`
- `user_lookup_loader` that rejects mismatched `ver` (global revocation via logout-all)
- `token_in_blocklist_loader` for per-token revocation
- Refresh token rotation
- `@jwt_required(fresh=True)` for password change
- Custom `admin_required` decorator
- Token version bump on password change (invalidates all old tokens)

---

## 11. References & Further Reading

- **Official docs**: <https://flask-jwt-extended.readthedocs.io/>
- **Source code**: <https://github.com/vimalloc/flask-jwt-extended>
- **PyPI**: <https://pypi.org/project/Flask-JWT-Extended/>
- **RFC 7519 (JWT)**: <https://datatracker.ietf.org/doc/html/rfc7519>
- **RFC 7515 (JWS — signatures)**: <https://datatracker.ietf.org/doc/html/rfc7515>
- **RFC 8725 (JWT Best Current Practices)**: <https://datatracker.ietf.org/doc/html/rfc8725> — **mandatory reading**
- **jwt.io debugger**: <https://jwt.io/> (don't paste production secrets!)
- **OWASP JSON Web Token Cheat Sheet**: <https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html>
- **PyJWT docs**: <https://pyjwt.readthedocs.io/>

### Critical security reading

- **"Critical vulnerabilities in JSON Web Token libraries"** (alg confusion): <https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/>
- **"JWT, JWS and JWT toolkit"** (Attacking JWT): <https://github.com/ticarpi/jwt_tool>

### Related notes in this vault

- [[Flask-Login]] — session-based alternative for server-rendered apps
- [[Flask-SQLAlchemy]] — user & blocklist models
- [[Marshmallow]] — input validation and output serialization
- [[Flask-CORS]] — enabling cross-origin requests with credentials
- [[Flask-Limiter]] — rate-limiting `/login`
- [[Celery]] — background tasks that act on behalf of users
- [[Flask-SocketIO]] — authenticating WebSocket connections
- [[Security-Best-Practices]] — top-level security checklist

### Decision tree: JWT vs sessions

```mermaid
flowchart TD
    A[Need authentication] --> B{Server-rendered HTML?}
    B -- Yes --> C[Flask-Login]
    B -- No --> D{Mobile or third-party client?}
    D -- Yes --> E[Flask-JWT-Extended]
    D -- No --> F{SPA on different origin from API?}
    F -- Yes --> G[Flask-JWT-Extended<br/>with CORS + CSRF]
    F -- No --> H{Need instant logout?}
    H -- Yes --> I[Flask-Login<br/>sessions are easier to revoke]
    H -- No --> J[Flask-JWT-Extended<br/>stateless scales better]
```

> [!tip] The bottom line
> For most new projects: **Flask-Login** if you serve HTML, **Flask-JWT-Extended** if you serve JSON. Both can coexist if you serve both. The choice is architectural, not security-driven — both can be made secure, both can be made insecure.
