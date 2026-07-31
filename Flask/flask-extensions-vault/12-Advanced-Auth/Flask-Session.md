---
title: Flask-Session
tags:
  - flask
  - sessions
  - server-side
  - redis
  - memcached
  - mongodb
  - security
  - cookies
aliases:
  - FlaskSession
  - Flask Session
  - Server-side sessions Flask
  - Redis sessions Flask
  - Session storage backends
related:
  - "[[Flask-Login]]"
  - "[[Flask-Dance]]"
  - "[[Flask-Authlib]]"
  - "[[Security-Best-Practices]]"
  - "[[Performance-Optimization]]"
created: 2024-01-15
updated: 2024-01-15
---

# Flask-Session

#flask #sessions #server-side #redis #memcached #mongodb #security #cookies

> [!info] Server-side session storage for Flask
> **Flask-Session** replaces Flask's default **client-side** session (a signed cookie containing the entire session dict) with **server-side** storage backed by Redis, Memcached, MongoDB, filesystem, or SQLAlchemy. The cookie sent to the browser contains only a small session ID; the actual session data lives on your server. This unlocks large sessions, immediate revocation, and multi-process consistency — at the cost of an extra storage lookup per request.

Think of Flask-Session as a **cloakroom**. Flask's default session is like a **wristband with the entire schedule printed on it**: the user wears everything they need, you just sign the band so they can't tamper with it. Cheap and stateless, but the wristband can only hold so much text, and you can't recall it once issued. Flask-Session is a **cloakroom with numbered tags**: you hand the user a tiny tag with a random number, and the actual session data hangs on a hanger in your back room (Redis / filesystem / DB). To revoke, you just throw away the hanger.

---

## 1. Overview & Metaphor

### Why server-side sessions?

Flask's default `session` is a **signed cookie**. The entire `session` dict is serialised to JSON, base64-encoded, signed with HMAC(`SECRET_KEY`), and sent in a cookie. On the next request, the browser sends it back; Flask verifies the signature and deserialises.

This is elegant but has hard limits:

| Problem | Why it bites |
|---|---|
| **4 KB cookie size limit** | Browsers reject cookies >4 KB. A session holding OAuth tokens + user prefs + flash messages can easily exceed that. |
| **Cookie sent on every request** | Even for static assets. 4 KB × 50 requests = 200 KB of overhead per page load on mobile. |
| **No immediate revocation** | A logged-out user with a stolen cookie can still forge requests until the cookie expires. Signing ≠ encryption. |
| **Cookie readable by client JS** | Unless `HTTPONLY` is set, JS can read session contents. Even with HTTPONLY, the *size* of the session is leaked. |
| **Cross-server inconsistency** | Sessions live in the browser, so multi-server "just works" — but you can't *invalidate* a specific user's session across all servers without server-side state. |
| **No partial updates** | Updating one key resends the entire session. |

Server-side sessions fix all of these: the cookie is a tiny random ID, the data lives in a shared store, and revoking is "delete row X".

### What Flask-Session does NOT do

| Concern | Who handles it |
|---|---|
| Authentication (login/logout) | [[Flask-Login]] |
| OAuth token storage | [[Flask-Dance]] (with `SQLAlchemyStorage`) or [[Flask-Authlib]] |
| Cookie transport security | Flask `SESSION_COOKIE_*` config (still applies) |
| CSRF protection | [[Flask-WTF]] |
| Cookie signing | Flask itself (`SECRET_KEY`) + `SESSION_USE_SIGNER` |
| Rate limiting | [[Flask-Limiter]] |

### Server-side vs client-side: tradeoffs

| Feature | Default Flask (cookie) | Flask-Session (server-side) |
|---|---|---|
| Cookie size | Up to 4 KB | ~32 bytes (just the ID) |
| Storage | Browser | Redis / DB / filesystem |
| Latency per request | 0 ms (data in cookie) | 1–5 ms (one storage read) |
| Revocation | Impossible until expiry | Instant (delete the key) |
| Multi-server | ✅ (stateless) | ✅ (shared store) |
| Cross-domain | Tricky (CORS / SameSite) | Easier (small cookie) |
| Best for | Small sessions, stateless APIs | Auth sessions, OAuth tokens, large carts |

> [!tip] The metaphor
> Flask-Session is a **cloakroom**. The default Flask session is a wristband with all your data printed on it. Flask-Session gives you a tiny numbered ticket instead, and hangs your data on a hanger in a back room. Ticket = small cookie (just a session ID). Hanger = Redis key or DB row. To revoke access, throw away the hanger; the ticket becomes useless. The tradeoff: every visit to the cloakroom now requires the attendant to walk to the back room (one extra network hop), so each request costs a few extra milliseconds.

---

## 2. Installation

```bash
(venv) $ pip install Flask-Session
```

With Redis:

```bash
(venv) $ pip install Flask-Session[redis]
```

With MongoDB:

```bash
(venv) $ pip install Flask-Session[mongodb]
```

All extras at once:

```bash
(venv) $ pip install "Flask-Session[redis,mongodb,memcached]"
```

Versions referenced in this note:

| Package | Version |
|---|---|
| Flask | 3.0.x |
| Flask-Session | 0.8.x |
| redis | 5.0.x |
| pymongo | 4.6.x |
| pymemcache | 4.0.x |

> [!warning] Flask-Session 0.8 vs 0.5/0.6
> 0.7+ reorganised the package into `flask_session` (lowercase, underscore) — older docs may reference `flask.ext.session`. The public API (`Session(app)`, `SESSION_TYPE`, etc.) is unchanged. 0.8 added support for `SESSION_TYPE="redis"` cluster mode and async Redis via `redis.asyncio`.

---

## 3. Configuration

### Minimal setup

```python
# app/__init__.py
from flask import Flask
from flask_session import Session

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "change-me"
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = "/var/flask_sessions/"
    Session(app)
    return app
```

That's it. `from flask import session` now reads/writes to `/var/flask_sessions/` instead of the cookie.

### All configuration options

| `app.config` key | Default | Description |
|---|---|---|
| `SESSION_TYPE` | `"null"` | One of: `null`, `redis`, `memcached`, `filesystem`, `mongodb`, `sqlalchemy`. |
| `SESSION_PERMANENT` | `True` | If True, sessions use `PERMANENT_SESSION_LIFETIME`. If False, sessions are deleted when the browser closes. |
| `SESSION_USE_SIGNER` | `False` | If True, sign the session ID cookie with `SECRET_KEY` (defence against ID tampering). Recommended in production. |
| `SESSION_PERMANENT_LIFETIME` | `PERMANENT_SESSION_LIFETIME` | Lifetime for permanent sessions. Defaults to Flask's `timedelta(days=31)`. |
| `SESSION_KEY_PREFIX` | `"session:"` | Prefix prepended to the storage key (Redis/Memcached/MongoDB). |
| `SESSION_COOKIE_NAME` | `"session"` | Cookie name. Inherited from Flask. |
| `SESSION_FILE_DIR` | `flask_session/` | Filesystem: directory to store session files. |
| `SESSION_FILE_THRESHOLD` | `500` | Filesystem: max number of session files. Oldest evicted when exceeded. |
| `SESSION_FILE_MODE` | `384` (0600) | Filesystem: file mode for created session files. |
| `SESSION_REDIS` | `redis.from_url("redis://127.0.0.1:6379")` | Redis: a `redis.Redis` instance. |
| `SESSION_MEMCACHED` | `memcache.Client(...)` | Memcached: a client instance. |
| `SESSION_MONGODB` | `MongoClient(...)` | MongoDB: a `pymongo.MongoClient`. |
| `SESSION_MONGODB_DB` | `"flask_session"` | MongoDB: database name. |
| `SESSION_MONGODB_COLLECT` | `"sessions"` | MongoDB: collection name. |
| `SESSION_SQLALCHEMY` | `db` | SQLAlchemy: a `flask_sqlalchemy.SQLAlchemy` instance. |
| `SESSION_SQLALCHEMY_TABLE` | `"sessions"` | SQLAlchemy: table name. |
| `SESSION_SQLALCHEMY_SEQUENCE` | `None` | SQLAlchemy: sequence name (Oracle/Postgres). |

### Redis config example

```python
import redis
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_REDIS"] = redis.from_url(
    os.environ["REDIS_URL"],   # e.g. "rediss://user:pass@host:6379/0"
    decode_responses=False,
)
app.config["SESSION_KEY_PREFIX"] = "myapp:session:"
Session(app)
```

### SQLAlchemy config example

```python
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db
app.config["SESSION_SQLALCHEMY_TABLE"] = "user_sessions"
db.init_app(app)
Session(app)
with app.app_context():
    db.create_all()
```

> [!warning] Initialise order matters
> If you use `SESSION_TYPE="sqlalchemy"`, you must `db.init_app(app)` **before** `Session(app)`. Otherwise Flask-Session can't introspect the engine and `db.create_all()` won't create the sessions table.

---

## 4. Basic Usage

### 4.1 Reading and writing the session

The interface is identical to Flask's default — `from flask import session`:

```python
from flask import Flask, session, redirect, url_for, request, jsonify

@app.route("/login", methods=["POST"])
def login():
    user = verify_credentials(request.json)
    if not user:
        return jsonify({"error": "invalid"}), 401
    session["user_id"] = user.id
    session["roles"]  = [r.name for r in user.roles]
    session["cart"]   = session.get("cart", [])   # survives across requests
    return jsonify({"ok": True})

@app.route("/me")
def me():
    if "user_id" not in session:
        return jsonify({"error": "anonymous"}), 401
    return jsonify({"user_id": session["user_id"], "roles": session["roles"]})

@app.route("/logout")
def logout():
    session.clear()   # deletes the row from Redis / DB
    return redirect(url_for("index"))
```

### 4.2 Permanent vs non-permanent sessions

```python
from datetime import timedelta
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=14)

@app.route("/login")
def login():
    session.permanent = True   # for this session only
    session["user_id"] = 42
    ...
```

`session.permanent = True` overrides `SESSION_PERMANENT=False` for this session. The cookie's `Max-Age` matches `PERMANENT_SESSION_LIFETIME`, and the storage backend sets a TTL.

### 4.3 Session lifecycle (sequence diagram)

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser
    participant F as Flask
    participant FS as Flask-Session
    participant S as Storage (Redis)
    B->>F: GET /me (Cookie: session=abc123)
    F->>FS: before_request: open_session
    FS->>FS: parse session ID from cookie
    alt SESSION_USE_SIGNER
        FS->>FS: verify signature
    end
    FS->>S: GET session:abc123
    S-->>FS: {user_id: 42, roles: ["editor"]}
    FS->>F: session dict loaded
    F->>F: view runs (modifies session["cart"])
    F->>FS: after_request: save_session
    FS->>S: SET session:abc123 ... EX 86400
    FS-->>B: Set-Cookie: session=abc123 (if modified)
```

### 4.4 Storage backend comparison

| Backend | Latency | Persistence | Multi-server | Best for |
|---|---|---|---|---|
| `null` | 0 ms | ❌ | n/a | Tests — sessions vanish between requests |
| `filesystem` | <1 ms | ✅ | ❌ (no shared FS) | Single-server dev, low-traffic prod |
| `redis` | 0.5–2 ms | ✅ (with RDB/AOF) | ✅ | **Production default**. Fast, TTL-aware. |
| `memcached` | 0.5–2 ms | ❌ (volatile) | ✅ | Cache-only sessions, ultra-low-latency |
| `mongodb` | 5–20 ms | ✅ | ✅ | If you already run MongoDB, no extra infra |
| `sqlalchemy` | 5–50 ms | ✅ | ✅ | If you already run Postgres/MySQL, no extra infra |

### 4.5 Backend selection mindmap

```mermaid
mindmap
  root((SESSION_TYPE))
    null
      tests
      no persistence
    filesystem
      dev only
      single-server
      easy backup
    redis
      production default
      TTL native
      cluster support
      sub-millisecond
    memcached
      cache-only
      volatile
      no persistence
      maximum throughput
    mongodb
      existing Mongo
      TTL collections
      document model fits
    sqlalchemy
      existing Postgres/MySQL
      transactional
      slowest
      good for compliance
```

---

## 5. Intermediate Patterns

### 5.1 Combining with [[Flask-Login]]

The standard pattern: Flask-Session stores the session, Flask-Login stores `user_id` in it.

```python
# app/__init__.py
from flask import Flask
from flask_session import Session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
session_store = Session()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_REDIS"] = redis.from_url(os.environ["REDIS_URL"])
    app.config["SESSION_USE_SIGNER"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

    db.init_app(app)
    login_manager.init_app(app)
    session_store.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    return app
```

### 5.2 Session storage flow with Redis

```mermaid
flowchart LR
    A[Request in] --> B[Parse session cookie]
    B --> C{Cookie present?}
    C -->|No| D[Create empty session]
    C -->|Yes| E[Verify signature]
    E --> F{Valid?}
    F -->|No| D
    F -->|Yes| G[GET redis session:ID]
    G --> H{Key exists?}
    H -->|No| D
    H -->|Yes| I[Deserialise JSON]
    I --> J[Load into g.session]
    D --> J
    J --> K[View runs]
    K --> L{Modified?}
    L -->|No| M[No-op]
    L -->|Yes| N[SET redis session:ID value EX ttl]
    N --> O[Set-Cookie if ID changed]
    M --> P[Response out]
    O --> P
```

### 5.3 Custom session ID generator

By default Flask-Session uses `uuid.uuid4().hex`. For higher entropy or to bind session IDs to a server-side secret:

```python
import secrets
from flask_session import Session

class CustomSession(Session):
    def _get_session_id(self):
        return secrets.token_urlsafe(32)

# Or simpler: override _generate_id
app.config["SESSION_ID_GENERATOR"] = lambda: secrets.token_urlsafe(32)
```

### 5.4 Flash messages across requests

`flash()` stores messages in the session. With server-side storage, large flash payloads don't blow up the cookie:

```python
from flask import flash, redirect, url_for

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    flash(f"Uploaded {file.filename} ({file.content_length} bytes)", "success")
    return redirect(url_for("dashboard"))
```

### 5.5 Storing OAuth tokens in the session

After OAuth (with [[Flask-Dance]] or [[Flask-Authlib]]), the access token lives in the session:

```python
@app.route("/login/google/authorized")
def google_authorized():
    token = oauth.google.authorize_access_token()
    session["oauth_google_token"] = token   # safe — session is server-side
    session["oauth_google_expires_at"] = time.time() + token["expires_in"]
    return redirect(url_for("dashboard"))
```

> [!warning] Don't store OAuth tokens in the default cookie session
> Flask's signed cookie is *readable* by the client (it's only signed, not encrypted). An attacker who steals the cookie has the access token. With server-side sessions, the cookie is just an ID; the token stays on your server.

### 5.6 Backing up / inspecting sessions

```python
# Admin endpoint: list active sessions (Redis)
@app.route("/admin/sessions")
@admin_required
def list_sessions():
    r = app.config["SESSION_REDIS"]
    keys = r.keys(f"{app.config['SESSION_KEY_PREFIX']}*")
    return jsonify({
        k: r.ttl(k) for k in keys[:100]   # {session_id: ttl_seconds}
    })

@app.route("/admin/sessions/<sid>/revoke", methods=["POST"])
@admin_required
def revoke_session(sid):
    r = app.config["SESSION_REDIS"]
    r.delete(f"{app.config['SESSION_KEY_PREFIX']}{sid}")
    return "", 204
```

---

## 6. Advanced Usage

### 6.1 Class diagram: backend inheritance

```mermaid
classDiagram
    class SessionInterface {
        <<flask SessionInterface>>
        +open_session(app, request)
        +save_session(app, session, response)
        +get_cookie_secure(app)
    }
    class NullSessionInterface
    class FileSystemSessionInterface {
        +_get_full_path(sid)
        +threshold: int
    }
    class RedisSessionInterface {
        +redis: Redis
        +key_prefix: str
        +use_signer: bool
    }
    class MemcachedSessionInterface
    class MongoDBSessionInterface {
        +db: Database
        +collection: str
    }
    class SqlAlchemySessionInterface {
        +sqlalchemy: SQLAlchemy
        +table: str
        +sequence: str?
    }
    SessionInterface <|-- NullSessionInterface
    SessionInterface <|-- FileSystemSessionInterface
    SessionInterface <|-- RedisSessionInterface
    SessionInterface <|-- MemcachedSessionInterface
    SessionInterface <|-- MongoDBSessionInterface
    SessionInterface <|-- SqlAlchemySessionInterface
```

### 6.2 Class diagram: session model

```mermaid
classDiagram
    class SecureCookieSession {
        +dict data
        +modified: bool
        +accessed: bool
        +permanent: bool
    }
    class ServerSideSession {
        +sid: str
        +backend
    }
    class SessionMixin {
        +permanent: bool
        +new: bool
        +modified: bool
    }
    class TaggedJSONSerializer {
        +dumps(obj) str
        +loads(payload) obj
    }
    SessionMixin <|-- SecureCookieSession
    SessionMixin <|-- ServerSideSession
    ServerSideSession ..> TaggedJSONSerializer : serialises values
```

### 6.3 State machine: session lifecycle

```mermaid
stateDiagram-v2
    [*] --> Anonymous: no cookie
    Anonymous --> Created: view sets session[k]=v
    Created --> Stored: save_session writes to backend
    Stored --> Loaded: next request reads cookie
    Loaded --> Modified: view mutates session
    Modified --> Stored: save_session writes
    Loaded --> Expired: TTL passes
    Expired --> Anonymous: backend evicts
    Stored --> Revoked: admin deletes key
    Revoked --> Anonymous: next request fails to find
    Loaded --> Cleared: session.clear()
    Cleared --> Anonymous: cookie deleted
    Anonymous --> [*]: response sent
```

### 6.4 Custom backend

Subclass `SessionBase` (or `NullSessionInterface`) to implement a new backend — e.g., DynamoDB:

```python
from flask_session import SessionInterface
from flask_session.base import ServerSideSession
import boto3

class DynamoDBSessionInterface(SessionInterface):
    session_class = ServerSideSession
    def __init__(self, table_name: str, prefix: str = "session:",
                 use_signer: bool = False, permanent: bool = True):
        self.table = boto3.resource("dynamodb").Table(table_name)
        self.prefix = prefix
        self.use_signer = use_signer
        self.permanent = permanent

    def _generate_sid(self):
        return secrets.token_urlsafe(32)

    def open_session(self, app, request):
        cookie_val = request.cookies.get(app.config["SESSION_COOKIE_NAME"])
        if not cookie_val:
            return self.session_class(sid=self._generate_sid(), permanent=self.permanent)
        if self.use_signer:
            try:
                sid = self._signer(app).unsign(cookie_val).decode()
            except BadSignature:
                return self.session_class(sid=self._generate_sid(), permanent=self.permanent)
        else:
            sid = cookie_val
        resp = self.table.get_item(Key={"id": f"{self.prefix}{sid}"})
        if "Item" not in resp:
            return self.session_class(sid=sid, permanent=self.permanent)
        return self.session_class(
            sid=sid, initial=resp["Item"]["data"],
            permanent=self.permanent,
        )

    def save_session(self, app, session, response):
        if not session:
            self.table.delete_item(Key={"id": f"{self.prefix}{session.sid}"})
            response.delete_cookie(app.config["SESSION_COOKIE_NAME"])
            return
        self.table.put_item(Item={
            "id": f"{self.prefix}{session.sid}",
            "data": dict(session),
            "expires_at": int(time.time()) + app.config["PERMANENT_SESSION_LIFETIME"].total_seconds(),
        })
        cookie_val = session.sid
        if self.use_signer:
            cookie_val = self._signer(app).sign(session.sid.encode()).decode()
        response.set_cookie(
            app.config["SESSION_COOKIE_NAME"], cookie_val,
            max_age=app.config["PERMANENT_SESSION_LIFETIME"].total_seconds(),
            httponly=True, secure=app.config["SESSION_COOKIE_SECURE"],
            samesite=app.config["SESSION_COOKIE_SAMESITE"],
        )

class DynamoDBSession(Session):
    def __init__(self, app=None, **kwargs):
        super().__init__(app, **kwargs)
    def _get_interface(self, app):
        return DynamoDBSessionInterface(**app.config["SESSION_DYNAMODB"])

app.config["SESSION_TYPE"] = "dynamodb"
app.config["SESSION_DYNAMODB"] = {"table_name": "flask_sessions", "use_signer": True}
```

### 6.5 Multi-region Redis with cluster mode

```python
import redis
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.cluster.RedisCluster(
    host="redis-cluster.example.com", port=6379,
    ssl=True, ssl_cert_reqs="required",
    decode_responses=False,
)
```

### 6.6 Sticky-session avoidance

With server-side sessions, you don't need sticky sessions at the load balancer — any server can read any session. This is the main operational win for horizontally scaled Flask apps.

```mermaid
flowchart LR
    LB[Load balancer] -->|request 1| S1[Server 1]
    LB -->|request 2| S2[Server 2]
    LB -->|request 3| S3[Server 3]
    S1 --> R[(Redis cluster)]
    S2 --> R
    S3 --> R
    R -.->|shard 1| R1[(Redis node 1)]
    R -.->|shard 2| R2[(Redis node 2)]
    R -.->|shard 3| R3[(Redis node 3)]
```

---

## 7. Common Pitfalls & Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `session` data doesn't persist between requests | `SESSION_TYPE="null"` (default if not set) — sessions vanish after each request. | Set `SESSION_TYPE="filesystem"` or `"redis"`. |
| `KeyError: 'url'` on Redis init | `SESSION_REDIS` not set and no default URL works. | Pass `SESSION_REDIS = redis.from_url("redis://...")`. |
| Sessions work locally but not in Docker | Filesystem path `/var/flask_sessions/` doesn't exist or isn't writable. | Create the dir with `mkdir -p` in the Dockerfile and `chmod 777`. |
| Sessions vanish on Redis restart | Redis without persistence (`save ""` config). | Enable RDB (`save 60 1000`) or AOF (`appendonly yes`) in `redis.conf`. |
| Cookie sent on every response, even without changes | `SESSION_REFRESH_EACH_REQUEST=True` (Flask default). | Set to `False` if you want cookies only when the session changes. |
| Cookie too large even with Flask-Session | `SESSION_USE_SIGNER=True` adds a signature, but the ID itself is tiny — so this shouldn't happen. Check if you're accidentally also using Flask's default session. | Ensure `Session(app)` is called *after* `app.config` is fully set. |
| Login works but session is immediately empty | Two `Session(app)` calls (e.g., once in `extensions.py`, once in `__init__.py`). | Call `Session(app)` exactly once. |
| Memcached sessions expire randomly | Memcached evicts entries under memory pressure (LRU). | Use Redis (persistent) or increase Memcached memory. |
| MongoDB sessions slow | No TTL index; full-collection scans on cleanup. | Create a TTL index: `db.sessions.createIndex({"expires_at": 1}, {expireAfterSeconds: 0})`. |
| SQLAlchemy `sessions` table grows unbounded | No cleanup job. Deleted sessions aren't auto-evicted. | Run a cron job: `DELETE FROM sessions WHERE expires_at < NOW()`. |
| 401s after deploying a new version | `SECRET_KEY` changed, so `SESSION_USE_SIGNER` signatures fail. | Rotate the key by accepting both old and new keys for a transition period. |
| `redis.exceptions.DataError: Invalid input of type: dict` | Passing `decode_responses=True` and storing dict values that redis-py can't serialise. | Keep `decode_responses=False`; Flask-Session handles JSON serialisation. |

### Troubleshooting decision tree

```mermaid
flowchart TD
    A[Session issue] --> B{Type?}
    B -->|Won't save| C[Check SESSION_TYPE]
    B -->|Won't load| D[Check SESSION_USE_SIGNER + SECRET_KEY]
    B -->|Too large| E[Switch to server-side]
    B -->|Vanishes| F[Check backend TTL/persistence]
    B -->|Cross-server mismatch| G[Backend not shared]
    C --> H{Resolved?}
    D --> H
    E --> H
    F --> H
    G --> H
    H -->|No| I[Enable Flask debug<br/>app.config DEBUG True]
    I --> J[Check session.sid in each request]
    J --> K[Verify backend key exists]
    K --> L[Check cookie is being set in response]
```

> [!danger] Don't forget to set `SESSION_USE_SIGNER = True` in production
> Without it, a session cookie is just a UUID. An attacker who guesses or steals a UUID can hijack the session. With `SESSION_USE_SIGNER`, the cookie is `HMAC(SECRET_KEY, sid)` — unforgeable without the secret. The cost is one HMAC operation per request, which is microseconds.

---

## 8. Best Practices

1. **Use Redis in production.** It's the right tradeoff: sub-millisecond reads, native TTL, persistence, clustering. Filesystem fails the moment you add a second server.
2. **Always set `SESSION_USE_SIGNER = True`** so the session ID cookie can't be tampered with.
3. **Set a sensible `PERMANENT_SESSION_LIFETIME`.** 7–30 days for consumer apps; 1 hour for banking.
4. **Use `SESSION_COOKIE_SECURE = True`** in production (HTTPS-only). Combine with HSTS.
5. **Use `SESSION_COOKIE_SAMESITE = "Lax"`** (default in modern Flask) to mitigate CSRF. Use `"Strict"` if your app doesn't need cross-site navigation.
6. **Keep `SESSION_COOKIE_HTTPONLY = True`.** Always. JavaScript should never read the session ID.
7. **Don't store large blobs in the session.** Even with server-side storage, each request pays deserialisation cost. Store blobs in S3 and put the URL in the session.
8. **Don't store sensitive data without encryption.** Server-side storage protects against cookie theft, not against DB/Redis compromise. Use Fernet for PII.
9. **Evict expired sessions proactively.** Redis does this via TTL; for SQLAlchemy, run a cleanup cron.
10. **Monitor session count.** A spike in active sessions can indicate a botnet or a session-fixation attack.
11. **Rotate `SECRET_KEY` carefully.** With `SESSION_USE_SIGNER=True`, all sessions are invalidated on rotation. Implement dual-key acceptance during the transition.
12. **Use a separate Redis DB number** (e.g., `redis://host/1`) so session keys don't collide with cache keys.

---

## 9. Integration with Other Extensions

### [[Flask-Login]]

The classic pairing. Flask-Session stores the session; Flask-Login stores `user_id` in it. See §5.1.

### [[Flask-Dance]]

Use `SESSION_TYPE="redis"` so OAuth tokens stored in the session don't blow up the cookie. Or use Flask-Dance's `SQLAlchemyStorage` for token storage (recommended for production).

### [[Flask-Authlib]]

When using Authlib's OAuth client with the default `fetch_token` callback reading from the Flask session, server-side storage is essential — the OAuth token + refresh + userinfo often exceeds 2 KB.

### [[Flask-SQLAlchemy]]

`SESSION_TYPE="sqlalchemy"` reuses your existing DB connection. Note: this couples session reads to your DB, which can become a bottleneck under high load.

### [[Flask-Limiter]]

Rate-limit session-creation endpoints to prevent session-fixation attacks:

```python
@app.route("/login", methods=["POST"])
@limiter.limit("10/minute")
def login():
    ...
```

### [[Flask-WTF]]

CSRF tokens are stored in the session. Server-side storage prevents the cookie from growing when CSRF + flash + cart all coexist.

### [[Flask-Caching]]

Don't confuse Flask-Session with [[Flask-Caching]]. They share storage backends (Redis, Memcached) but serve different purposes: sessions are per-user stateful data; caching is per-data memoisation. Use different Redis DB numbers (`SESSION_REDIS` → DB 1, `CACHE_REDIS_URL` → DB 0).

---

## 10. Real-World Example: Multi-Server Flask App with Redis Sessions

```python
# app/__init__.py
import os, redis
from datetime import timedelta
from flask import Flask
from flask_session import Session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
session_store = Session()

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ["SECRET_KEY"],
        SESSION_TYPE="redis",
        SESSION_PERMANENT=True,
        SESSION_USE_SIGNER=True,
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SESSION_REDIS=redis.from_url(os.environ["REDIS_URL"], ssl_cert_reqs=None),
        SESSION_KEY_PREFIX="myapp:session:",
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SQLALCHEMY_DATABASE_URI=os.environ["DATABASE_URL"],
        WTF_CSRF_TIME_LIMIT=timedelta(hours=1),
    )

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    session_store.init_app(app)

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.auth import auth_bp
    from app.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    return app
```

```python
# app/auth/views.py
from flask import Blueprint, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    user = db.session.scalar(db.select(User).where(User.email == email))
    if not user or not user.check_password(password):
        flash("Invalid email or password.", "danger")
        return redirect(url_for("auth.login_form"))

    # Rotate session ID on login to prevent session fixation
    session.clear()
    login_user(user)
    session.permanent = True
    # Optionally store a "logged_in_at" timestamp
    session["logged_in_at"] = int(time.time())
    flash(f"Welcome back, {user.name}!", "success")
    return redirect(url_for("main.dashboard"))

@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()    # deletes the Redis key
    logout_user()
    flash("Signed out.", "info")
    return redirect(url_for("main.index"))
```

```python
# app/admin/views.py
from flask import Blueprint, jsonify, current_app
from app.permissions import AdminPermission

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/sessions")
@AdminPermission().require(http_exception=403)
def list_active_sessions():
    """List active session IDs and their TTLs — useful for security audits."""
    r = current_app.config["SESSION_REDIS"]
    prefix = current_app.config["SESSION_KEY_PREFIX"]
    keys = r.scan_iter(f"{prefix}*", count=100)
    sessions = []
    for key in keys:
        ttl = r.ttl(key)
        sessions.append({"id": key.decode().replace(prefix, ""), "ttl_seconds": ttl})
    return jsonify({"count": len(sessions), "sessions": sessions[:100]})

@admin_bp.route("/admin/sessions/<sid>/revoke", methods=["POST"])
@AdminPermission().require(http_exception=403)
def revoke_session(sid):
    r = current_app.config["SESSION_REDIS"]
    r.delete(f"{current_app.config['SESSION_KEY_PREFIX']}{sid}")
    return "", 204
```

### Full sequence

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant LB as Load balancer
    participant S1 as Server 1
    participant S2 as Server 2
    participant R as Redis cluster
    participant DB as PostgreSQL
    U->>LB: POST /login (email, password)
    LB->>S1: route to server 1
    S1->>DB: SELECT user WHERE email=...
    DB-->>S1: user row
    S1->>S1: session.clear() (rotate ID)
    S1->>R: SET myapp:session:NEW_ID {user_id: 42} EX 604800
    R-->>S1: OK
    S1-->>U: 302 /dashboard (Set-Cookie: session=SIGNED_NEW_ID)
    U->>LB: GET /dashboard
    LB->>S2: route to server 2 (different server!)
    S2->>S2: verify signature, extract sid
    S2->>R: GET myapp:session:NEW_ID
    R-->>S2: {user_id: 42}
    S2->>DB: SELECT user WHERE id=42
    DB-->>S2: user row
    S2-->>U: 200 dashboard HTML
    Note over U,R: Same session works on any server — no stickiness needed
```

---

## 11. References

- **Official docs**: <https://flask-session.readthedocs.io/>
- **GitHub**: <https://github.com/fengsp/flask-session>
- **PyPI**: <https://pypi.org/project/Flask-Session/>
- **Flask docs on sessions**: <https://flask.palletsprojects.com/en/latest/api/#flask.session>
- **Specifications / patterns**:
  - RFC 6265bis — HTTP State Management Mechanism (cookies)
  - OWASP Session Management Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html>
- **Backends**:
  - redis-py — <https://redis-py.readthedocs.io/>
  - pymemcache — <https://pymemcache.readthedocs.io/>
  - PyMongo — <https://pymongo.readthedocs.io/>
- **Related notes**: [[Flask-Login]] · [[Flask-Dance]] · [[Flask-Authlib]] · [[Flask-WTF]] · [[Flask-Caching]] · [[Flask-Limiter]] · [[Security-Best-Practices]] · [[Performance-Optimization]]
