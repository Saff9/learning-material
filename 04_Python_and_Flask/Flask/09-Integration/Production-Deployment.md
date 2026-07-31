---
title: Production Deployment
tags:
  - flask
  - deployment
  - production
  - devops
  - docker
  - gunicorn
  - nginx
  - kubernetes
aliases:
  - Flask in Production
  - Deployment
  - Prod Flask
related:
  - "[[Full-Stack-Example]]"
  - "[[Common-Patterns]]"
  - "[[Security-Best-Practices]]"
  - "[[Performance-Optimization]]"
  - "[[Flask-SocketIO]]"
  - "[[Celery]]"
  - "[[Flask-Caching]]"
  - "[[Project-Structure]]"
created: 2024-01-15
updated: 2024-01-15
---

# Production Deployment

#flask #deployment #production #devops #gunicorn #nginx #docker

> [!info] From localhost to load balancer
> Running `flask run` on your laptop is fine for development. Running it in production is a one-way ticket to a 3 AM incident. This note covers the **whole stack**: WSGI servers, reverse proxies, TLS, Docker, secrets, databases, Redis, Celery, SocketIO at scale, logging, monitoring, and zero-downtime deploy strategies. It is the operations counterpart to the [[Full-Stack-Example]] capstone.

The Flask development server is single-threaded, doesn't auto-restart on crash, doesn't TLS-terminate, and prints stack traces to the browser. **Do not use it in production.** Pick one of: Gunicorn, uWSGI, or a managed runtime like App Runner.

---

## 1. The Mental Model

A production Flask stack has at least these layers, from the outside in:

```mermaid
flowchart LR
    DNS[DNS<br/>Route53 / Cloudflare] --> CDN[CDN<br/>Cloudflare / CloudFront]
    CDN --> LB[Load Balancer<br/>ALB / Nginx]
    LB --> TLS[TLS termination<br/>Let's Encrypt cert]
    TLS --> NGX[Nginx<br/>reverse proxy]
    NGX --> GUN[Gunicorn<br/>WSGI workers]
    GUN --> APP[Flask app<br/>create_app]
    APP --> PG[(PostgreSQL<br/>RDS / Aurora)]
    APP --> REDIS[(Redis<br/>ElastiCache)]
    APP --> CEL[Celery worker<br/>separate process]
    CEL --> REDIS
    BEAT[Celery beat] --> CEL
    APP --> SMTP[SMTP relay<br/>SES / Postmark]
```

Each layer has exactly one job. CDN caches static assets and shields you from DDoS. LB distributes traffic across instances. Nginx terminates TLS, sets headers, serves static files. Gunicorn runs your Python. PostgreSQL holds relational state. Redis is the cache/broker/queue. Celery processes run as their own services.

> [!tip] Why so many layers?
> Each layer absorbs a class of failure. If the CDN cache hits, Nginx never sees the request. If Nginx serves the static file, Gunicorn never sees it. If Gunicorn handles the request, Celery doesn't have to. Each layer you add means a layer you can scale and monitor independently.

---

## 2. WSGI Servers Compared

| Feature | **Gunicorn** | **uWSGI** |
|---|---|---|
| Config simplicity | High — one file or CLI flags | Medium — many knobs, INI/YAML |
| Performance | Very good | Excellent (esp. with C optimizations) |
| Worker types | sync, gevent, eventlet, threads | preforking, threads, async, mules |
| Async support | First-class (eventlet/gevent) | Built-in, more choices |
| Community | Largest in Flask world | Older, larger config surface |
| Documentation | Excellent | Voluminous, sometimes confusing |
| Recommendation | Default for most teams | Power users with specific needs |

> [!tip] Pick Gunicorn unless you have a reason not to
> Gunicorn is the de-facto standard for Flask/Django/FastAPI. The community is large, the bug surface is small, and every Flask tutorial assumes it. Reach for uWSGI when you have specific features it has that Gunicorn doesn't (e.g., mules for offloading work, advanced routing).

### Worker classes

| Worker class | When to use |
|---|---|
| `sync` (default) | CPU-bound request handlers, simple apps. One request at a time per worker. |
| `gthread` | Mixed workload with some I/O. Each worker has N threads. |
| `eventlet` / `gevent` | Long-polling, WebSockets (Flask-SocketIO), thousands of mostly-idle connections. |

> [!warning] Mixing async workers with SQLAlchemy
> `eventlet`/`gevent` monkey-patch the stdlib — including `psycopg2`. Either `monkey_patch()` very early in your `wsgi.py` (before importing anything that touches DB drivers) **or** use a thread-based worker. A half-patched process will silently deadlock.

---

## 3. Gunicorn Configuration

A production `gunicorn.conf.py` is more readable than 20 CLI flags:

```python
# deploy/gunicorn.conf.py
import multiprocessing
import os

# Sync workers, typically 2-4× CPU cores
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"             # use "eventlet" for Flask-SocketIO
threads = 2                       # only meaningful for gthread/sync
worker_connections = 1000         # only for async workers
max_requests = 1000               # recycle workers to fight memory leaks
max_requests_jitter = 50          # randomize so they don't all restart together
timeout = 30                      # kill stuck workers
graceful_timeout = 10             # give them 10s to finish before SIGKILL
keepalive = 5                     # seconds to keep client connection open

# Where to bind — Nginx will proxy to this
bind = "0.0.0.0:8000"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 8190         # max URL length
limit_request_fields = 100        # max headers
limit_request_field_size = 8190

# Process management
preload_app = True                # load app once before forking; saves RAM
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = "taskflow"
group = "taskflow"

# For Flask-SocketIO with eventlet:
# worker_class = "eventlet"
# workers = 1                     # SocketIO + multi-worker is tricky; see §10
```

Run it:

```bash
gunicorn -c deploy/gunicorn.conf.py wsgi:app
```

> [!tip] `preload_app = True` is double-edged
> It saves RAM (copy-on-write shares model definitions across workers) and reduces startup time. But if your app leaks file descriptors or has global state, **all workers** inherit it. If you see weird behavior on reload, try `False`.

### Choosing worker count

The old formula `(2 × CPU) + 1` is a starting point, not a law. Tune by measuring:

- **CPU-bound** (heavy compute, ML): fewer workers, equal to or slightly more than CPU count.
- **I/O-bound** (DB, external APIs): more workers, but watch DB connection pool size. Each worker opens up to `pool_size + max_overflow` DB connections.
- **Async (eventlet)**: 1 worker can serve thousands of concurrent connections, but CPU-bound endpoints will block the event loop.

---

## 4. Reverse Proxy: Nginx

Nginx sits in front of Gunicorn for three reasons: TLS termination, static file serving, and to absorb slow clients (so Gunicorn workers stay busy with fast ones).

```nginx
# /etc/nginx/sites-available/taskflow
upstream gunicorn_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name app.taskflow.app;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.taskflow.app;

    ssl_certificate     /etc/letsencrypt/live/app.taskflow.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.taskflow.app/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

    # Static files served directly by Nginx, never hit Gunicorn
    location /static/ {
        alias /var/taskflow/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # WebSocket upgrade for Flask-SocketIO
    location /socket.io/ {
        proxy_pass http://gunicorn_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;     # keep WS open for 24h max
    }

    # Everything else
    location / {
        proxy_pass http://gunicorn_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_read_timeout 30s;
        client_max_body_size 10M;
    }
}
```

> [!warning] `proxy_set_header Connection "upgrade"` is essential for WebSockets
> Without the `Upgrade` and `Connection: upgrade` headers, Nginx will treat the WebSocket request as a regular HTTP request, complete it, and close it. Your SocketIO client will see an immediate disconnect. This is the single most common production SocketIO bug.

---

## 5. TLS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d app.taskflow.app -d www.taskflow.app
# Auto-renews via systemd timer
sudo systemctl status certbot.timer
```

In Flask, set `PREFERRED_URL_SCHEME = "https"` and use `ProxyFix` so the app sees the original protocol:

```python
# wsgi.py
from werkzeug.middleware.proxy_fix import ProxyFix
from app import create_app

app = create_app("production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2, x_proto=1, x_host=1, x_prefix=1)
```

Without `ProxyFix`, `request.is_secure` returns `False` (because Nginx → Gunicorn is plain HTTP), which breaks any logic that branches on HTTPS.

---

## 6. Docker: Multi-Stage Dockerfile

```dockerfile
# deploy/Dockerfile
# ---- Builder stage ----
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# System deps for building (psycopg2 etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps into a virtualenv we can copy later
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install -e .

# ---- Runtime stage ----
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Only runtime libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 taskflow

# Copy the venv from the builder
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY . .

RUN chown -R taskflow:taskflow /app
USER taskflow

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["gunicorn", "-c", "deploy/gunicorn.conf.py", "wsgi:app"]
```

### docker-compose.yml (full stack)

```yaml
# deploy/docker-compose.yml
version: "3.9"

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: taskflow
      POSTGRES_USER: taskflow
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskflow"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: ["redis-server", "--appendonly", "yes", "--maxmemory", "256mb", "--maxmemory-policy", "allkeys-lru"]
    volumes:
      - redisdata:/data
    restart: unless-stopped

  web:
    build:
      context: ..
      dockerfile: deploy/Dockerfile
    env_file: ../.env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    expose: ["8000"]
    restart: unless-stopped

  worker:
    build:
      context: ..
      dockerfile: deploy/Dockerfile
    command: ["celery", "-A", "celery_app.celery", "worker", "--loglevel=info", "--concurrency=4"]
    env_file: ../.env
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  beat:
    build:
      context: ..
      dockerfile: deploy/Dockerfile
    command: ["celery", "-A", "celery_app.celery", "beat", "--loglevel=info"]
    env_file: ../.env
    depends_on:
      - redis
    restart: unless-stopped

  nginx:
    image: nginx:1.27-alpine
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./certs:/etc/letsencrypt:ro
      - ../app/static:/var/taskflow/app/static:ro
    ports: ["80:80", "443:443"]
    depends_on:
      - web
    restart: unless-stopped

volumes:
  pgdata:
  redisdata:
```

> [!tip] `--maxmemory-policy allkeys-lru` is the right Redis default
> Without a memory cap, Redis will eventually swap and become catastrophically slow. With `allkeys-lru`, Redis evicts the least-recently-used key when full. This is correct for a **cache** — but **do not use it for your Celery broker or SocketIO queue**, since losing a queued task or socket message is bad. Use a separate Redis instance (or DB index) for the broker.

---

## 7. Environment Variables & Secrets

The 12-factor rule: **config in env vars, never in code.** A single `.env` file is fine for development; in production use a secrets manager.

```bash
# .env (development)
FLASK_ENV=development
SECRET_KEY=dev-only-do-not-use-in-prod
DATABASE_URL=postgresql://taskflow:secret@localhost:5432/taskflow
JWT_SECRET_KEY=another-dev-only-secret
REDIS_URL=redis://localhost:6379/0
MAIL_SERVER=localhost
```

For production, three approaches:

| Approach | When | Tool |
|---|---|---|
| Plain env vars | Single-host Docker, simple VMs | `.env` loaded by `python-dotenv` |
| Secret manager | Cloud, multi-instance | AWS Secrets Manager, GCP Secret Manager, Doppler, HashiCorp Vault |
| Encrypted at rest in CI/CD | Kubernetes | sealed-secrets, External Secrets Operator |

A loader for AWS Secrets Manager:

```python
# app/secrets.py
import boto3, json, os

def load_secrets(secret_id: str):
    client = boto3.client("secretsmanager", region_name=os.environ.get("AWS_REGION"))
    response = client.get_secret_value(SecretId=secret_id)
    secrets = json.loads(response["SecretString"])
    os.environ.update(secrets)

# Call at the very top of wsgi.py, before importing the app.
```

> [!danger] Never commit `.env`
> Add `.env` to `.gitignore`. Rotate the secret immediately if it ever lands in git. Tools like `git-secrets` or `trufflehog` scan for accidental commits. See [[Security-Best-Practices]].

---

## 8. PostgreSQL in Production

### Connection pooling

In SQLAlchemy 2.0 / Flask-SQLAlchemy 3.x, the pool is configured via `SQLALCHEMY_ENGINE_OPTIONS`:

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 20,           # base connections per worker
    "max_overflow": 10,        # burst connections
    "pool_timeout": 30,        # wait at most 30s for a free conn
    "pool_recycle": 1800,      # recycle every 30 min (prevent stale conns)
    "pool_pre_ping": True,     # test conn liveness before use
}
```

The math: `pool_size + max_overflow` × `gunicorn workers` = max DB connections. With 4 workers, `pool_size=20`, `max_overflow=10`, you need **120 connections** capacity on Postgres. Set `max_connections` in `postgresql.conf` accordingly.

### PgBouncer for many workers

If you scale to many workers or many app instances, use [PgBouncer](https://www.pgbouncer.org/) in transaction-pooling mode. It multiplexes hundreds of app connections onto a smaller pool of real Postgres connections:

```
# pgbouncer.ini
[databases]
taskflow = host=10.0.0.5 port=5432 dbname=taskflow

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
pool_mode = transaction
max_client_conn = 500
default_pool_size = 25
```

Then point your app at `postgresql://taskflow:pass@pgbouncer:6432/taskflow`.

> [!warning] Transaction-mode PgBouncer breaks server-side cursors and prepared statements
> If you use `stream_results=True` for huge queries, or SQLAlchemy 2.0's prepared statement cache, set `pool_mode = session` (but you lose the multiplexing benefit). Choose your tradeoff.

### Backups

```bash
# Cron: nightly logical backup
pg_dump -Fc -U taskflow -h localhost taskflow | \
    aws s3 cp - s3://my-backups/taskflow/$(date +%F).dump

# And point-in-time recovery via WAL archiving — set up via RDS or wal-g.
```

Test restore quarterly. An untested backup is not a backup.

---

## 9. Redis in Production

You'll likely run **two** Redis instances in prod:

1. **Cache Redis** — `maxmemory-policy allkeys-lru`, can lose data, fast.
2. **Broker/queue Redis** — persistence on (`appendonly yes`), never evict, used by Celery + SocketIO.

```bash
# Cache instance (port 6379)
redis-server --port 6379 --maxmemory 512mb --maxmemory-policy allkeys-lru --save ""

# Broker instance (port 6380)
redis-server --port 6380 --appendonly yes --appendfsync everysec --save 60 1000
```

For HA, use Redis Sentinel or Redis Cluster. For most Flask apps, a single managed Redis (ElastiCache, Upstash, Redis Cloud) is enough.

---

## 10. SocketIO at Scale

The single-process SocketIO server is easy. Scaling it across multiple processes is the hard part.

### The problem

WebSocket connections are **stateful**. If user A's socket is on worker 1, and user B's socket is on worker 2, then a `socketio.emit()` from worker 1 won't reach user B.

### The solution: Redis message queue

Configure `message_queue` on every SocketIO instance (Flask + Celery + any process that emits):

```python
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="eventlet",
    message_queue=os.environ["REDIS_URL"],  # the magic
)
```

Now `socketio.emit(...)` publishes to Redis pub/sub; every SocketIO server that has the matching room delivers to its connected clients.

### Multi-worker Gunicorn

```python
# gunicorn.conf.py
workers = 4
worker_class = "eventlet"     # mandatory for SocketIO
threads = 1                   # eventlet is single-threaded per worker
worker_connections = 1000     # up to 1000 sockets per worker
```

With 4 workers × 1000 connections, you can hold 4000 concurrent WebSocket clients on one box. To go further, put Nginx in front of multiple Gunicorn instances on multiple VMs.

> [!tip] Don't preload with eventlet
> `preload_app = True` + `worker_class = "eventlet"` causes subtle issues with monkey-patching. Set `preload_app = False` when using eventlet. See [[Flask-SocketIO]] for the full discussion.

---

## 11. Celery Workers & Beat in Production

Celery runs as separate services, not inside Gunicorn.

```bash
# Worker
celery -A celery_app.celery worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --time-limit=300 \
    --soft-time-limit=240

# Beat (scheduler) — exactly ONE instance
celery -A celery_app.celery beat --loglevel=info

# Flower (monitoring UI) — optional
celery -A celery_app.celery flower --port=5555
```

| Flag | Why |
|---|---|
| `--max-tasks-per-child=1000` | Recycle child processes to fight memory leaks (especially with native libs like numpy). |
| `--time-limit=300` | Hard kill a task after 5 min. |
| `--soft-time-limit=240` | Raise `SoftTimeLimitExceeded` after 4 min — task can clean up. |
| `--concurrency=4` | Number of concurrent tasks. Match to CPU count for CPU-bound; raise for I/O-bound. |

> [!warning] Run **one** beat process
> If you launch multiple beat containers (e.g., by accident in Docker Swarm), every periodic task runs N times. Use a singleton pattern: a dedicated container with `replicas: 1`, or a leader-election sidecar.

### Beat in HA with `redbeat`

The `celery-redbeat` scheduler stores the schedule in Redis and uses a Redis lock so only one beat runs at a time — surviving a beat crash.

```python
celery.conf.beat_scheduler = "redbeat.RedBeatScheduler"
celery.conf.redbeat_redis_url = os.environ["REDIS_URL"]
```

---

## 12. Logging

### JSON logs for production

Plain text logs are fine in dev. In prod, ship **structured JSON logs** so Loggly/Datadog/Loki can search them.

```python
# app/logging.py
import logging, json, sys
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "props"):
            log.update(record.props)
        return json.dumps(log, default=str)

def configure_logging(app):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    app.logger.handlers = [handler]
    app.logger.setLevel(logging.INFO)
    # Make Werkzeug logs go through the same formatter
    logging.getLogger("werkzeug").handlers = [handler]
```

Use [structlog](https://www.structlog.org/) or [loguru](https://github.com/Delgan/loguru) for richer features (context vars, log levels as methods, colorized dev output).

### Request ID for tracing

```python
# app/__init__.py
import uuid
from flask import g, request

@app.before_request
def start_request():
    g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

@app.after_request
def end_request(response):
    response.headers["X-Request-ID"] = g.request_id
    app.logger.info("request", extra={"props": {
        "request_id": g.request_id,
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "duration_ms": int((time.time() - g.start) * 1000),
    }})
    return response
```

---

## 13. Monitoring

```mermaid
mindmap
  root((Observability stack))
    Errors
      Sentry SDK
      Flask / Celery / SQLAlchemy integrations
      Release tagging
      PII scrubbing
    Metrics
      prometheus_flask_exporter
      http_request_duration_seconds
      http_requests_total
      sqlalchemy_pool_checkedout
      celery_queue_length (custom)
      Grafana dashboards
    Logs
      JSON formatter (structlog / loguru)
      stdout -> Loki / CloudWatch / Datadog
      X-Request-ID tracing
      before_request / after_request hooks
    Health
      /health (liveness)
      /ready (readiness)
      LB uses /ready to drain
      Container restart on /health 5xx
    Tracing
      OpenTelemetry SDK
      Sentry Performance
      RUM (browser p75/p95)
    Alerting
      queue depth > N
      error rate > 1pct
      p99 latency > 500ms
      worker offline
```

### Sentry for exceptions

```bash
pip install sentry-sdk[flask]
```

```python
# app/__init__.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def init_sentry(app):
    if dsn := app.config.get("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=dsn,
            environment=app.config["ENV"],
            release=app.config.get("RELEASE_ID"),
            send_default_pii=False,
            traces_sample_rate=0.1,   # 10% of transactions for performance
            integrations=[FlaskIntegration(), CeleryIntegration(), SqlalchemyIntegration()],
        )
```

### Prometheus metrics

```bash
pip install prometheus-flask-exporter
```

```python
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)

# Custom business metrics
task_created = metrics.counter(
    "tasks_created_total",
    "Number of tasks created",
    labels={"project_id": lambda: g.project_id},
)
```

Scrape `/metrics` from a Prometheus instance; visualize in Grafana. Track:

- `flask_http_request_duration_seconds` — request latency histogram
- `flask_http_request_total` — request count by status
- DB pool stats: `sqlalchemy_pool_checkedout`, `sqlalchemy_pool_size`
- Celery queue length: `celery_queue_length` (custom collector)

### Health checks

Two endpoints:

```python
@app.route("/health")
def health():
    """Liveness — is the process up?"""
    return {"status": "ok"}, 200

@app.route("/ready")
def ready():
    """Readiness — can I serve traffic?"""
    try:
        db.session.execute(text("SELECT 1"))
        cache.get("__ready_probe__")  # raises if Redis is down
    except Exception as e:
        app.logger.exception("Readiness check failed")
        return {"status": "not_ready", "error": str(e)}, 503
    return {"status": "ready"}, 200
```

- Load balancer pings `/health` — if 5xx, restart the container.
- Load balancer pings `/ready` — if 5xx, drain traffic from this instance.

---

## 14. Zero-Downtime Deployment

```mermaid
gantt
    title Blue-green deploy timeline (~10 min)
    dateFormat HH:mm
    axisFormat %H:%M
    section Build
    CI green on main            :a1, 00:00, 3m
    Build green Docker image    :a2, after a1, 4m
    Push to registry            :a3, after a2, 1m
    section Deploy
    Pull image on green fleet   :b1, after a3, 1m
    Run migrations (forward-only) :crit, b2, after b1, 1m
    Warm green (run /ready)     :b3, after b2, 2m
    Smoke test green            :b4, after b3, 1m
    section Cutover
    Switch LB target blue->green :crit, c1, after b4, 0m
    Drain blue (in-flight reqs) :c2, after c1, 2m
    Terminate blue              :c3, after c2, 1m
    section Verify
    Watch error rate + p99      :d1, after c3, 5m
    Rollback if degraded       :d2, after d1, 1m
```

### Blue-green

```mermaid
flowchart LR
    LB[Load Balancer] --> |100%| BLUE[Blue v1.4.2]
    GREEN[Green v1.4.3] --> WAIT[Drain & warm]
    LB -.-> |0%| GREEN
    style GREEN fill:#dfd
    WAIT --> SWITCH[Switch LB]
    SWITCH --> LB
```

Steps:
1. Deploy new version to "green" environment, no traffic.
2. Run migrations (`flask db upgrade`) against the shared DB.
3. Run smoke tests against green.
4. Switch LB target from blue to green.
5. Wait for blue to drain (no in-flight requests).
6. Terminate blue. Keep image around for fast rollback.

### Rolling (Kubernetes default)

Update pods one at a time: `maxUnavailable: 0`, `maxSurge: 1`. The new pod must pass `/ready` before the next one starts. Slower than blue-green but uses less capacity.

### Canary

Route 5% of traffic to the new version, watch error rate and latency, then 25%, 50%, 100%. Tools: Flagger, Argo Rollouts, Istio.

> [!tip] Migrations must be backward-compatible
> A migration that removes a column will crash the old version still running during rollout. Split it: deploy v2 (which ignores the column), then deploy v3 (which removes it). Same for renames: add new column, dual-write, backfill, switch reads, drop old.

---

## 15. Static Files & CDNs

Three options:

| Strategy | When | How |
|---|---|---|
| Nginx serves static | Single-host | `location /static/ { alias ...; }` |
| CDN in front of Nginx | Multi-instance | Cloudflare/CloudFront origin = Nginx |
| CDN + S3, no Nginx | Large or global | Upload static to S3 at build time, set `app.static_url_path` to the CDN URL |

```python
# In production
app.config["PREFERRED_URL_SCHEME"] = "https"
app.static_url_path = "https://cdn.taskflow.app/static"  # if serving from CDN
```

For dynamic asset versioning, use [Flask-Assets](https://flask-assets.readthedocs.io/) or a build tool (Vite, esbuild) that hashes filenames — so the CDN URL changes per deploy and clients refetch.

---

## 16. Deployment Platform Comparison

```mermaid
quadrantChart
    title Hosting options: ops burden vs cost-at-scale
    x-axis Cheap at scale --> Expensive at scale
    y-axis Low ops burden --> High ops burden
    quadrant-1 Managed PaaS (easy + pricey)
    quadrant-2 Cloud-native (cheap + hands-off)
    quadrant-3 DIY containers (cheap + ops)
    quadrant-4 Bare metal (pricey + ops)
    "Cloud Run": [0.3, 0.2]
    "App Runner": [0.4, 0.25]
    "Heroku": [0.8, 0.2]
    "Render/Railway": [0.55, 0.3]
    "Kubernetes (EKS/GKE)": [0.7, 0.85]
    "Docker on VM": [0.35, 0.7]
    "Bare metal VM": [0.25, 0.9]
```

| Platform | Best for | Cold start | Scaling | Cost model |
|---|---|---|---|---|
| **Bare metal** (single VM) | Hobby, low traffic | None | Vertical only | Fixed monthly |
| **Docker on a VM** | Small teams, full control | None | Vertical only | Fixed + ops time |
| **Kubernetes** | Large orgs, microservices | None | HPA, fast | Higher base cost |
| **Heroku** | MVPs, small teams | None (dynos always up) | Easy dyno scaling | Per-dyno-hour, expensive at scale |
| **Render / Railway** | Modern Heroku alternatives | None | Easy | Per-service, cheaper than Heroku |
| **AWS App Runner** | AWS-native, containerized | ~30s on scale-to-zero | Auto | Per-vCPU-second |
| **Google Cloud Run** | Serverless containers | ~1-5s on cold start | Auto, scale-to-zero | Per-request, very cheap at low traffic |

### When to pick what

- **Hobby project / portfolio**: Render or Railway. Free tier, zero ops.
- **Startup MVP**: Heroku or Render. One `git push`, sleep at night.
- **Real production, team < 10**: Docker on 2 VMs + Cloudflare. ~$50/mo, full control.
- **Real production, team > 10**: Kubernetes (EKS/GKE) or PaaS with managed Postgres/Redis.
- **Spiky / event-driven**: Cloud Run or App Runner. Pay per request, scale to zero.

> [!tip] Don't K8s your side project
> Kubernetes is the right tool for "15 microservices, 3 teams, 4 environments." For a single Flask app, the operational overhead is 5× the value. Start with Docker Compose; migrate when you feel the pain.

---

## 17. A Production Launch Checklist

```markdown
- [ ] `FLASK_ENV=production`, `DEBUG=False`
- [ ] Strong `SECRET_KEY` and `JWT_SECRET_KEY` from secrets manager
- [ ] `HTTPS` only, HSTS header set, TLS 1.2+ only
- [ ] Gunicorn with `worker_class` matching your workload (eventlet for SocketIO)
- [ ] Nginx with `proxy_set_header` for `X-Forwarded-*`
- [ ] `ProxyFix` applied to `app.wsgi_app`
- [ ] Postgres `pool_pre_ping=True`, `pool_recycle` set
- [ ] Redis with persistence for broker, eviction for cache
- [ ] Celery worker + beat as separate services, beat is singleton
- [ ] Sentry SDK initialized with release tag
- [ ] Prometheus metrics scraped, Grafana dashboard exists
- [ ] `/health` and `/ready` endpoints, LB configured to use them
- [ ] Log shipping to Loki/CloudWatch/Datadog
- [ ] DB backups automated + tested restore
- [ ] Migrations are backward-compatible for rolling deploys
- [ ] Rate limits configured on auth endpoints
- [ ] CSP, HSTS, X-Frame-Options, X-Content-Type-Options headers set
- [ ] Dependency scan (pip-audit) in CI
- [ ] Runbook written for: DB failover, Redis loss, worker backlog
- [ ] Load test (locust/k6) before launch; latency p99 < 500ms
```

---

## 18. Where To Go Next

- [[Full-Stack-Example]] — the app this note deploys.
- [[Common-Patterns]] — the patterns (factory, error handlers, health checks) used above.
- [[Security-Best-Practices]] — every checklist item above, explained in depth.
- [[Performance-Optimization]] — squeeze more requests per second out of the same hardware.

---

## 19. References

- [Gunicorn docs](https://docs.gunicorn.org/) — official, well-written.
- [uWSGI docs](https://uwsgi-docs.readthedocs.io/) — comprehensive but dense.
- [12-Factor App](https://12factor.net/) — Heroku's principles for app config.
- [Nginx as reverse proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) — official guide.
- [Deploying Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/deployment.html) — official deployment guide.
- [Celery in production](https://docs.celeryq.dev/en/stable/userguide/optimization.html) — official optimization guide.
- [The Twelve-Factor App](https://12factor.net/) — read it before your first prod deploy.
- [Awesome Flask Deployment](https://github.com/humiaozuzu/awesome-flask#deployment) — community list.
