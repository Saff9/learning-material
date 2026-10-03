---
title: Flask-Limiter
tags:
  - flask
  - rate-limiting
  - security
  - redis
  - api
  - utilities
aliases:
  - FlaskLimiter
  - Flask Limiter
  - rate limiting in Flask
  - throttle
related:
  - "[[Flask-Login]]"
  - "[[Flask-JWT-Extended]]"
  - "[[Flask-Caching]]"
  - "[[Flask-RESTful]]"
  - "[[Security-Best-Practices]]"
created: 2024-01-15
updated: 2024-01-15
---

# Flask-Limiter

#flask #rate-limiting #security #redis #api #utilities

> [!info] The rate-limiting extension for Flask
> Flask-Limiter decorates Flask routes with per-endpoint, per-user, per-IP, or globally-shared request quotas. It is built on top of the [`limits`](https://limits.readthedocs.io/) library, which means it supports every common rate-limit strategy (fixed window, sliding window, token bucket, leaky bucket) and every common storage backend (memory, Redis, Memcached, MongoDB, etcd).
>
> If you ship an API without rate limiting, you are one angry script kiddie away from an outage. Flask-Limiter is the standard way to add it to a Flask app — usually a 5-line change to your extensions module plus a decorator per route.

Think of Flask-Limiter as the **bouncer at the club door**. The bouncer counts how many times each patron (client) walks in. If a patron exceeds the per-night quota, they're told to come back later — politely, with a `429 Too Many Requests` and a `Retry-After` header. The bouncer is per-club (per-route) or shared across multiple entrances (`shared_limit`), and remembers counts across nights if the storage is persistent.

---

## 1. Overview & Metaphor

### What problem does rate limiting solve?

Rate limiting caps how often a client can call an endpoint. The use cases:

1. **Protect the service from abuse** — brute-force login attacks, content scraping, denial-of-service.
2. **Enforce fair use** — free tier: 100 req/day; paid tier: 1000 req/min.
3. **Protect expensive operations** — password reset, file export, email send.
4. **Protect downstream systems** — your DB can do 1000 QPS; limit the API to 800 QPS so headroom exists.
5. **Cost control** — AI API endpoints where each call costs you money.

Without rate limiting, every endpoint is a public DoS surface. With it, you establish a contract: "be a good citizen, you get N requests per minute; abuse it and you get 429s".

### Strategies

| Strategy | Description | Pros | Cons |
|---|---|---|---|
| **Fixed window** | Count requests in `floor(now/window)` bucket | Simple, O(1) | Burst at window edges (2× traffic in 1 s at boundary) |
| **Sliding window** | Weighted average of current and previous window | Smooth, no edge bursts | More CPU; needs Redis `INCR`+`EXPIRE` combo |
| **Token bucket** | Bucket holds N tokens; refill rate R tokens/s; each request consumes 1 | Allows bounded bursts; classic for APIs | Stateful per-client |
| **Leaky bucket** | Queue of size N, drained at rate R; queue overflow = reject | Smooths traffic | Adds latency for queued requests |

Flask-Limiter selects the strategy via `RATELIMIT_STRATEGY`. The default is `fixed-window-elastic-expiry` (a hybrid — see §3).

#### Strategy Comparison Quadrant

```mermaid
quadrantChart
    title Rate-limit strategy tradeoffs
    x-axis Bursty --> Smooth
    y-axis Cheap --> Expensive
    quadrant-1 Smooth & costly
    quadrant-2 Smooth & cheap
    quadrant-3 Bursty & cheap
    quadrant-4 Bursty & costly
    "fixed-window": [0.20, 0.20]
    "fixed-window-elastic": [0.35, 0.30]
    "sliding-window-counter": [0.55, 0.45]
    "moving-window": [0.85, 0.80]
    "token-bucket": [0.50, 0.55]
    "leaky-bucket": [0.90, 0.85]
```

> [!tip] The metaphor
> Flask-Limiter is a **tollbooth that hands out punch cards**. Each card (key) starts with N punches free. Every request punches a hole. When the card is full, the booth raises the barrier and you wait until the window rolls over. Some booths refill punches gradually (token bucket); some reset all at once (fixed window at midnight). The booth can stamp the card with `X-RateLimit-Remaining` so drivers know how many punches they have left.

### Token bucket visualised

```mermaid
flowchart LR
    subgraph Bucket[Token Bucket — capacity 10, refill 1/s]
        T1[●]
        T2[●]
        T3[●]
        T4[●]
        T5[●]
        T6[●]
        T7[●]
    end
    R[Refiller<br/>+1 token/s] --> Bucket
    Bucket -->|Each request consumes 1 token| Q{Tokens left?}
    Q -->|Yes| OK[200 OK]
    Q -->|No| R429[429 Too Many Requests]
```

Bounded bursts: a client can fire 10 requests instantly (drain the bucket), then sustain 1 req/s indefinitely. If they pause, the bucket refills.

#### Token Bucket State Machine

```mermaid
stateDiagram-v2
    [*] --> Full: capacity=N tokens
    Full --> Draining: request consumes 1
    Draining --> Draining: more requests
    Draining --> Empty: last token consumed
    Empty --> Draining: refill tick (+1 token)
    Empty --> Blocked: request arrives<br/>no tokens
    Blocked --> Empty429: respond 429<br/>Retry-After: 1s
    Empty429 --> Empty: client waits
    Draining --> Full: idle long enough<br/>refill reaches capacity
    note right of Draining
        Token bucket allows bounded<br/>bursts up to N; sustained<br/>rate limited by refill.
    end note
```

---

## 2. Installation

```bash
(venv) $ pip install Flask-Limiter
```

For Redis/Memcached backends, install the client library:

```bash
(venv) $ pip install redis          # Redis backend
(venv) $ pip install pymemcache     # Memcached (recommended)
(venv) $ pip install python-memcached  # alternative
```

Versions referenced in this note:

- Flask-Limiter **3.5.x**
- `limits` **3.7.x**
- Flask **3.0.x**

---

## 3. Configuration

Flask-Limiter reads config from `app.config`. The most important keys:

| Key | Default | Description |
|---|---|---|
| `RATELIMIT_ENABLED` | `True` | Master switch; set `False` to disable |
| `RATELIMIT_DEFAULT` | `"200 per minute"` | Applied to any route with `@limiter.limit(...)` |
| `RATELIMIT_DEFAULTS_PER_METHOD` | `False` | Apply default limit per HTTP method |
| `RATELIMIT_STORAGE_URI` | `"memory://"` | Backend — `memory://`, `redis://host:port/db`, `memcached://host:port` |
| `RATELIMIT_STORAGE_OPTIONS` | `{}` | Backend-specific kwargs (e.g. SSL, socket timeouts) |
| `RATELIMIT_STRATEGY` | `"fixed-window-elastic-expiry"` | `fixed-window`, `fixed-window-elastic-expiry`, `sliding-window`, `moving-window`, or backend-specific |
| `RATELIMIT_HEADERS_ENABLED` | `False` | Emit `X-RateLimit-*` response headers |
| `RATELIMIT_HEADER_RESET` | `X-RateLimit-Reset` | Header name for reset time |
| `RATELIMIT_HEADER_REMAINING` | `X-RateLimit-Remaining` | Header name for remaining quota |
| `RATELIMIT_HEADER_LIMIT` | `X-RateLimit-Limit` | Header name for total quota |
| `RATELIMIT_HEADER_RETRY_AFTER` | `Retry-After` | Header name for retry-after seconds |
| `RATELIMIT_SWALLOW_ERRORS` | `False` | If `True`, errors from the storage backend don't propagate (rate limit becomes permissive) |
| `RATELIMIT_IN_MEMORY_FALLBACK_ENABLED` | `False` | Fall back to in-memory if backend unreachable |
| `RATELIMIT_IN_MEMORY_FALLBACK` | `["200 per minute"]` | Fallback limits list |
| `RATELIMIT_KEY_PREFIX` | `""` | Prefix for all keys (useful for shared Redis) |
| `RATELIMIT_FAIL_ON_FIRST_BREACH` | `True` | If `False`, allow the first breach to succeed (warning shot) |
| `RATELIMIT_BACKOFF` | `None` | Optional callable returning dynamic retry-after |

### Strategy comparison

| `RATELIMIT_STRATEGY` | Behaviour | When to use |
|---|---|---|
| `fixed-window` | Reset count at strict window boundary | When burst at boundary is acceptable; cheapest |
| `fixed-window-elastic-expiry` (default) | Window starts on first request, resets after interval | Smoother, no edge bursts; best default |
| `moving-window` (a.k.a. sliding window) | Count requests in the last N seconds | When you need exact "N per rolling 60s" semantics |
| `sliding-window-counter` | Weighted avg of current + previous window | Smoother than fixed, cheaper than moving |
| `token-bucket` (backend-dependent) | Token bucket | When you want bounded bursts |

> [!warning] Not all backends support all strategies
> `memory://` supports everything; `redis://` supports fixed/moving/sliding/token; `memcached://` supports fixed only (no native sliding window). Check the `limits` docs for your backend.

### Storage backends

```python
# Dev — in-memory (per-worker, NOT shared)
RATELIMIT_STORAGE_URI = "memory://"

# Production — Redis (shared across workers)
RATELIMIT_STORAGE_URI = "redis://localhost:6379/2"

# Redis with TLS and password
RATELIMIT_STORAGE_URI = "rediss://default:password@host:6380/0"

# Redis Cluster
RATELIMIT_STORAGE_URI = "redis+cluster://host1:7000,host2:7000,host3:7000/0"

# Memcached
RATELIMIT_STORAGE_URI = "memcached://localhost:11211"

# Memcached cluster
RATELIMIT_STORAGE_URI = "memcached://host1:11211,host2:11211,host3:11211"

# MongoDB (rare)
RATELIMIT_STORAGE_URI = "mongodb://localhost:27017/ratelimits"

# etcd (rare)
RATELIMIT_STORAGE_URI = "etcd://localhost:2379"
```

> [!danger] `memory://` is not shared across workers
> With Gunicorn + 4 workers, each worker has its own counter. A client rotating across workers gets 4× the limit. **Always use Redis or Memcached in production.**

### Initialising the extension

```python
# extensions.py
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

def init_app(app: Flask) -> None:
    limiter.init_app(app)
```

```python
# app.py
from flask import Flask
from config import ProductionConfig
from extensions import init_app

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(ProductionConfig)
    init_app(app)
    return app
```

`key_func` is the function that returns the "identity" of the caller — usually an IP address. See §5 for per-user key functions.

---

## 4. Basic usage

### `@limiter.limit()` — per-route limit

```python
from flask import Flask
from extensions import limiter

app = Flask(__name__)

@app.route("/api/expensive")
@limiter.limit("10 per minute")
def expensive():
    return {"result": compute()}

@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute; 20 per hour")
def login():
    ...
```

The string `"10 per minute"` is parsed by `limits` into `(count=10, per=60s)`. Multiple limits can be combined with `;`.

### Limit string syntax

| String | Meaning |
|---|---|
| `"10 per minute"` | 10 requests / 60s |
| `"1/second"` | 1 request / second |
| `"100 per hour"` | 100 requests / 3600s |
| `"5 per minute; 20 per hour"` | Both limits apply — most restrictive wins |
| `"10/minute; 100/hour; 1000/day"` | Tiered |
| `"10 per 30 seconds"` | Arbitrary window |

### Default limit

Set `RATELIMIT_DEFAULT` to apply a global default — every route gets it unless you explicitly exempt or override:

```python
RATELIMIT_DEFAULT = "200 per minute"
```

```python
@app.route("/health")         # inherits 200/min default
def health(): ...

@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")  # overrides default for this route
def login(): ...

@app.route("/api/internal")
@limiter.exempt               # exempt from default
def internal(): ...
```

### Multiple limits on one route

```python
@app.route("/api/transfer", methods=["POST"])
@limiter.limit("3 per minute")        # burst protection
@limiter.limit("100 per day")         # daily cap
def transfer():
    ...
```

Both apply. The first to trip returns 429.

### Limit on Flask-RESTful Resources

```python
from flask_restful import Resource

class LoginResource(Resource):
    decorators = [limiter.limit("5 per minute")]
    def post(self):
        ...
```

Or use `method_decorators`:

```python
class LoginResource(Resource):
    method_decorators = {"post": [limiter.limit("5 per minute")]}
    def post(self): ...
    def get(self): ...   # not limited
```

See [[Flask-RESTful]] for more.

---

## 5. Intermediate patterns

### Exempting routes

```python
@app.route("/healthz")
@limiter.exempt
def healthz():
    return "OK", 200
```

Or programmatically:

```python
limiter.exempt(blueprint)              # exempt an entire blueprint
limiter.exempt(some_view_function)
```

### Shared limits

A **shared limit** caps the aggregate request rate across multiple routes — useful for "any combination of these endpoints, max N per minute":

```python
api_limit = limiter.shared_limit("1000 per minute", scope="api")

@app.route("/api/users")
@api_limit
def users(): ...

@app.route("/api/articles")
@api_limit
def articles(): ...
```

`scope="api"` is the bucket name — all decorated routes draw from the same 1000/min quota. Use `scope=lambda: ...` for dynamic scopes (e.g. per-tenant).

```python
def tenant_scope():
    from flask import g
    return f"tenant:{g.tenant_id}"

tenant_limit = limiter.shared_limit("10000 per hour", scope=tenant_scope)
```

### Custom key functions

By default, Flask-Limiter uses `get_remote_address` (the client IP). For per-user limits, swap in a function that returns the user identity:

```python
from flask import request
from flask_login import current_user

def user_or_ip_key():
    if current_user.is_authenticated:
        return f"user:{current_user.id}"
    return f"ip:{get_remote_address()}"

limiter = Limiter(key_func=user_or_ip_key)
```

For an API keyed on a header:

```python
def api_key():
    return request.headers.get("X-API-Key") or get_remote_address()
```

> [!warning] Always fall back to IP
> If `key_func` returns `None`, all anonymous clients share one limit. Always provide a fallback (`or get_remote_address()`).

### Behind a reverse proxy

If your app sits behind Nginx/Cloudflare/AWS ALB, `request.remote_addr` is the proxy's IP, not the client's. Configure Werkzeug to trust `X-Forwarded-*` headers:

```python
from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
```

And set `RATELIMIT_HEADERS_ENABLED=True` so clients see their quotas.

### Rate limit response headers

```python
RATELIMIT_HEADERS_ENABLED = True
```

Response headers:

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1700000000
Retry-After: 23   # only on 429
```

Clients can read these to back off proactively.

### Error handler for 429

Flask-Limiter raises `RateLimitExceeded` (a subclass of `werkzeug.exceptions.TooManyRequests`). Register a custom handler:

```python
from flask import jsonify
from flask_limiter import RateLimitExceeded

@app.errorhandler(RateLimitExceeded)
def handle_429(e):
    return jsonify({
        "error": "rate_limit_exceeded",
        "message": f"Rate limit exceeded: {e.description}",
        "retry_after": e.description.split(" ")[-1] if " " in e.description else 60,
    }), 429
```

#### 429 Response Lifecycle

```mermaid
sequenceDiagram
    participant C as Client
    participant W as Flask view
    participant L as Limiter decorator
    participant S as Storage (Redis)
    C->>W: POST /api/login
    W->>L: before_request
    L->>S: INCR key + EXPIRE
    S-->>L: count=6
    L->>L: 6 > 5 → breach
    L->>C: 429 Too Many Requests<br/>Retry-After: 47<br/>X-RateLimit-Remaining: 0
    Note over L,C: view function never runs
    C->>C: backoff (retry-after)
    Note over C: After window resets:
    C->>W: POST /api/login (retry)
    W->>L: before_request
    L->>S: INCR key (new window)
    S-->>L: count=1
    L-->>W: pass-through
    W->>W: authenticate
    W-->>C: 200 OK<br/>X-RateLimit-Remaining: 4
```

You can also override the message:

```python
@limiter.limit("5 per minute",
               error_message="Slow down! Try again in a minute.",
               headers={"X-Help": "https://myapp.com/docs/rate-limits"})
def login(): ...
```

---

## 6. Advanced usage

### Conditional limiting

The `unless` parameter lets you skip the limit under conditions:

```python
def is_internal():
    return request.remote_addr in INTERNAL_IPS

@app.route("/api/users")
@limiter.limit("100 per minute", unless=is_internal)
def users(): ...
```

Or pass `exempt_when`:

```python
@limiter.limit("5 per minute", exempt_when=lambda: current_user.is_admin)
def expensive_endpoint(): ...
```

### Cost-weighted limits

Some requests are more expensive than others. Use the `cost` parameter:

```python
@app.route("/api/ai/generate")
@limiter.limit("100 per hour", cost=10)  # each call costs 10 of the 100/hour quota
def generate(): ...

@app.route("/api/ai/status")
@limiter.limit("100 per hour", cost=1)
def status(): ...
```

### On-breach callback

```python
def on_breach(limit):
    app.logger.warning("Rate limit breached: %s for key %s",
                       limit.limit, limit.key)

@limiter.limit("5 per minute", on_breach=on_breach)
def login(): ...
```

Useful for alerting (e.g. push to Slack when a specific endpoint is being abused).

### Dynamic limits via `override_defaults`

```python
def dynamic_limit():
    user = current_user
    if user.is_premium:
        return "10000 per hour"
    if user.is_authenticated:
        return "1000 per hour"
    return "100 per hour"

@app.route("/api/search")
@limiter.limit(dynamic_limit)
def search(): ...
```

The callable is invoked per-request — expensive but flexible.

### Multiple limit groups with separate scopes

```python
@limiter.limit("10 per second", scope="burst")
@limiter.limit("1000 per hour", scope="hourly")
@limiter.limit("10000 per day", scope="daily")
def api(): ...
```

Each `scope` is a separate counter; all must pass.

### Distributed storage with Redis Sentinel

```python
RATELIMIT_STORAGE_URI = "redis+sentinel://host1:26379,host2:26379,host3:26379/service_name"
RATELIMIT_STORAGE_OPTIONS = {"socket_timeout": 0.5}
```

### Backing off with `Retry-After` strategies

```python
import random

def jittered_retry_after(limit, *args):
    # Add 0–5 s jitter to the standard retry-after
    return limit.reset_at - int(time.time()) + random.randint(0, 5)

RATELIMIT_HEADER_RETRY_AFTER = "Retry-After"
RATELIMIT_BACKOFF = jittered_retry_after
```

### Fail-open vs fail-closed

If the Redis backend goes down, Flask-Limiter by default returns 500 errors on every request. Two safer options:

- `RATELIMIT_SWALLOW_ERRORS=True` — log and allow the request (fail open).
- `RATELIMIT_IN_MEMORY_FALLBACK_ENABLED=True` — fall back to per-worker in-memory limits (partial protection).

```python
RATELIMIT_SWALLOW_ERRORS = True
RATELIMIT_IN_MEMORY_FALLBACK_ENABLED = True
RATELIMIT_IN_MEMORY_FALLBACK = ["100 per minute"]
```

> [!tip] The right production setting
> Most teams want fail-open (a broken rate-limiter shouldn't take the site down). Combine with monitoring: alert if Redis is unreachable so you can fix it before attackers notice.

---

## 7. Common pitfalls & troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| 429 returned for everyone | `RATELIMIT_DEFAULT` too low; storage shared across environments | Use `RATELIMIT_KEY_PREFIX` per env; tune default |
| Limits seem 4× too high | 4 Gunicorn workers + `memory://` | Switch to Redis (`RATELIMIT_STORAGE_URI=redis://...`) |
| 429 for legit clients behind corp NAT | All office IPs share one limit | Use per-user key function instead of `get_remote_address` |
| `KeyError` on `current_user` in key_func | Limiter runs before `@login_required` | Make key_func defensive: `getattr(current_user, "is_authenticated", False)` |
| All requests succeed even when over limit | `RATELIMIT_ENABLED=False` or `SWALLOW_ERRORS=True` hiding backend failure | Check logs; verify `RATELIMIT_STORAGE_URI` is reachable |
| `redis.exceptions.AuthenticationError` | Wrong password or DB index | Verify with `redis-cli -u $URI ping` |
| 429 returned after deploy | New code uses different `key_prefix` or scope name | Audit `scope=` strings across deploys |
| Cloudflare shows real client IP but limiter uses CF IP | Missing `ProxyFix` | Add `ProxyFix(app.wsgi_app, x_for=1, ...)` |
| Burst at window edges | `fixed-window` strategy | Switch to `fixed-window-elastic-expiry` or `moving-window` |
| Token bucket drains instantly under load | Bucket capacity too small | Increase capacity (e.g. `"100 per minute; capacity=50"`) |
| 429 with no `Retry-After` | `RATELIMIT_HEADERS_ENABLED=False` | Enable headers |

### Verify the limit is working

```bash
$ for i in {1..10}; do
    curl -s -o /dev/null -w "%{http_code} %{header_json}\n" \
         -X POST http://localhost:5000/api/login \
         -H "Content-Type: application/json" \
         -d '{"username":"x","password":"y"}'
done
```

You should see `200 200 200 200 200 429 429 429 429 429`.

### Inspect the storage

```bash
$ redis-cli keys "LIMITER*"    # Flask-Limiter default key prefix
$ redis-cli get LIMITER:api_login:127.0.0.1
```

---

## 8. Best practices

1. **Always use Redis or Memcached in production** — never `memory://` with multiple workers.
2. **Fail open, monitor loudly** — `RATELIMIT_SWALLOW_ERRORS=True` plus an alert when storage is unreachable.
3. **Set `RATELIMIT_HEADERS_ENABLED=True`** — clients can self-throttle and you'll get fewer support tickets.
4. **Use per-user key functions for authenticated APIs.** IP-based limits misbehave behind NAT and 4G carriers.
5. **Apply stricter limits to write endpoints than reads.** `GET /api/users` 1000/min; `POST /api/users` 5/min.
6. **Apply brutal limits to auth endpoints.** `POST /api/login` 5/min per IP; `POST /api/forgot-password` 3/hour per IP — brute-force mitigation.
7. **Use `shared_limit` for cost-control groups.** All AI endpoints share one quota.
8. **Monitor 429 rates** — alert if >1% of requests hit the limit; you may need to raise it.
9. **Use `moving-window` if you need exact rolling semantics**; `fixed-window-elastic-expiry` otherwise.
10. **Don't share the Redis DB with cache.** Use `redis://...:6379/2` for limiter, `/0` for cache. See [[Flask-Caching]] §9.
11. **Use `cost=` for asymmetric endpoints** — a `/api/export` is 50× the cost of `/api/users`.
12. **Document your limits in the API spec** — OpenAPI extensions like `x-ratelimit` help clients understand.

---

## 9. Integration with other extensions

### [[Flask-Login]]

Per-user limits instead of per-IP:

```python
from flask_login import current_user

def user_or_ip():
    if getattr(current_user, "is_authenticated", False):
        return f"user:{current_user.id}"
    return f"ip:{get_remote_address()}"

limiter = Limiter(key_func=user_or_ip)
```

### [[Flask-JWT-Extended]]

Use the JWT identity as the key:

```python
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

def jwt_or_ip():
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            return f"user:{identity}"
    except Exception:
        pass
    return f"ip:{get_remote_address()}"

limiter = Limiter(key_func=jwt_or_ip)
```

### [[Flask-Caching]]

Cache expensive responses **and** rate-limit the endpoint:

```python
@app.route("/api/expensive")
@cache.cached(timeout=300, key_prefix="expensive")
@limiter.limit("60 per minute")
def expensive():
    return compute()
```

Decorators compose: the cache check happens before the limiter check (or vice versa depending on order — see the gotcha below).

> [!warning] Decorator order matters
> In Flask, decorators apply **bottom-up**. The decorator closest to the function runs first. For `@cache.cached` over `@limiter.limit`, a cache hit never reaches the limiter — every cached response is unlimited. For `@limiter.limit` over `@cache.cached`, every request hits the limiter but cache misses are limited. Pick the behaviour you want; for "limits apply even on cache hits", put `@limiter.limit` on top.

### [[Flask-RESTful]]

```python
class SearchResource(Resource):
    decorators = [limiter.limit("60 per minute")]
    def get(self): ...
```

### [[Flask-Mail]]

Hard-limit email-triggering endpoints (a forgotten-password endpoint is a classic abuse vector):

```python
@app.route("/auth/forgot", methods=["POST"])
@limiter.limit("3 per hour; 10 per day")
def forgot(): ...
```

---

## 10. Real-world example — tiered API rate limits

A complete, runnable single-file app demonstrating tiered rate limits (anonymous / user / premium), per-endpoint limits, headers, and a custom 429 handler.

```python
# app.py
import os
from flask import Flask, jsonify, request, g
from flask_limiter import Limiter, RateLimitExceeded
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config.update(
    RATELIMIT_STORAGE_URI=os.environ.get("REDIS_URL", "redis://localhost:6379/2"),
    RATELIMIT_HEADERS_ENABLED=True,
    RATELIMIT_DEFAULT="60 per minute",
    RATELIMIT_SWALLOW_ERRORS=True,
    RATELIMIT_IN_MEMORY_FALLBACK_ENABLED=True,
    RATELIMIT_IN_MEMORY_FALLBACK=["60 per minute"],
    RATELIMIT_KEY_PREFIX="myapp:",
)

# Mock auth: read X-User-Id and X-User-Tier headers (replace with real auth).
TIERS = {"anon": (60, "minute"), "user": (600, "minute"), "premium": (6000, "minute")}

def tier_key():
    tier = request.headers.get("X-User-Tier", "anon")
    uid = request.headers.get("X-User-Id") or get_remote_address()
    g.rate_tier = tier
    return f"{tier}:{uid}"

limiter = Limiter(key_func=tier_key, app=app)

def tiered_limit():
    """Return a limit string based on the user's tier."""
    tier = request.headers.get("X-User-Tier", "anon")
    count, window = TIERS.get(tier, TIERS["anon"])
    return f"{count} per {window}"

# ---------- Routes ----------
@app.errorhandler(RateLimitExceeded)
def handle_429(e):
    return jsonify({
        "error": "rate_limit_exceeded",
        "message": e.description,
        "tier": getattr(g, "rate_tier", "anon"),
    }), 429

@app.errorhandler(HTTPException)
def handle_http(e):
    return jsonify({"error": e.name.lower().replace(" ", "_"), "message": e.description}), e.code

@app.route("/api/search")
@limiter.limit(tiered_limit)
def search():
    return jsonify({"results": ["a", "b", "c"]})

@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")  # brutal — brute-force mitigation
def login():
    return jsonify({"token": "fake-jwt"})

@app.route("/api/ai/generate", methods=["POST"])
@limiter.limit(tiered_limit, cost=10)  # AI calls cost 10 quota units
def ai_generate():
    return jsonify({"text": "Once upon a time..."})

@app.route("/api/healthz")
@limiter.exempt
def healthz():
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
```

```bash
# Anonymous: 60/min
$ for i in {1..65}; do
    curl -s -o /dev/null -w "%{http_code} " http://localhost:5000/api/search
  done
# → 200 200 ... 200 429 429 ...

# Premium user: 6000/min — won't trip in normal testing
$ curl -H "X-User-Tier: premium" -H "X-User-Id: 42" http://localhost:5000/api/search

# AI cost: 10× quota per call
$ curl -X POST -H "X-User-Tier: user" -H "X-User-Id: 7" \
       http://localhost:5000/api/ai/generate
```

### End-to-end token bucket flow

```mermaid
sequenceDiagram
    participant Client
    participant Flask
    participant Limiter
    participant Redis

    Client->>Flask: POST /api/login (cred)
    Flask->>Limiter: check_limit("5/min", key="ip:1.2.3.4")
    Limiter->>Redis: GET limiter:api_login:ip:1.2.3.4
    Redis-->>Limiter: 3
    Note over Limiter: 3 < 5 → allow
    Limiter->>Redis: INCR + EXPIRE
    Limiter-->>Flask: allow
    Flask-->>Client: 200 OK + X-RateLimit-Remaining: 2

    Client->>Flask: POST /api/login (cred)
    Flask->>Limiter: check_limit(...)
    Limiter->>Redis: GET
    Redis-->>Limiter: 5
    Note over Limiter: 5 ≥ 5 → deny
    Limiter-->>Flask: RateLimitExceeded
    Flask-->>Client: 429 + Retry-After: 47
```

---

## 11. References

- **Flask-Limiter docs** — <https://flask-limiter.readthedocs.io/>
- **`limits` library docs** — <https://limits.readthedocs.io/>
- **RFC 6585 — Additional HTTP Status Codes (429)** — <https://www.rfc-editor.org/rfc/rfc6585>
- **RFC 7231 — Retry-After header** — <https://www.rfc-editor.org/rfc/rfc7231#section-7.1.3>
- **Token bucket algorithm** — <https://en.wikipedia.org/wiki/Token_bucket>
- **Sliding window algorithm** — <https://blog.cloudflare.com/counting-things-a-lot-of-different-things/>
- **Stripe API rate limiting** — <https://stripe.com/blog/rate-limiters>
- Related notes: [[Flask-Login]] · [[Flask-JWT-Extended]] · [[Flask-Caching]] · [[Flask-RESTful]] · [[Flask-Mail]] · [[Security-Best-Practices]]
