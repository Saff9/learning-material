---
title: Performance Optimization
tags:
  - flask
  - performance
  - optimization
  - profiling
  - caching
  - scaling
aliases:
  - Flask Performance
  - Optimizing Flask
  - Flask Profiling
related:
  - "[[Full-Stack-Example]]"
  - "[[Common-Patterns]]"
  - "[[Production-Deployment]]"
  - "[[Security-Best-Practices]]"
  - "[[Flask-SQLAlchemy]]"
  - "[[Flask-Caching]]"
  - "[[Flask-Limiter]]"
  - "[[Celery]]"
  - "[[Flask-SocketIO]]"
  - "[[Marshmallow]]"
created: 2024-01-15
updated: 2024-01-15
---

# Performance Optimization

#flask #performance #optimization #profiling #caching #scaling

> [!info] Faster, or just fast enough?
> Premature optimization is the root of much evil; **measured** optimization is the root of well-run systems. This note is structured as a workflow: **measure → diagnose → fix → re-measure**. Every section ends with a "how to verify this helped" note. Without measurement, you're just guessing — and most guesses about performance are wrong.

Most Flask performance problems fall into one of four buckets:

1. **Database** — N+1 queries, missing indexes, unbounded result sets.
2. **I/O** — blocking calls inside request handlers (sync HTTP, file reads).
3. **Computation** — heavy loops, serialization, template rendering.
4. **Concurrency** — too few workers, GIL contention, blocked event loops.

The fixes are usually small. The wins come from finding the right thing to fix.

---

## 1. The Optimization Workflow

```mermaid
flowchart TD
    SLOW[Slow endpoint] --> MEASURE[Measure: p50, p95, p99 latency]
    MEASURE --> PROFILE[Profile: where is time spent?]
    PROFILE --> DB?[DB > 50%?]
    DB? -->|Yes| DBFIX[Fix queries: indexes, eager load, paginate]
    DB? -->|No| CPU?[CPU > 30%?]
    CPU? -->|Yes| CPUFIX[Fix compute: cache, batch, async]
    CPU? -->|No| IO?[I/O wait high?]
    IO? -->|Yes| IOFIX[Async: Celery, gevent, async view]
    IO? -->|No| QUEUE[Concurrency: add workers, scale out]
    DBFIX --> RERUN[Re-measure]
    CPUFIX --> RERUN
    IOFIX --> RERUN
    QUEUE --> RERUN
    RERUN --> SLOWENOUGH{Good enough?}
    SLOWENOUGH -->|No| MEASURE
    SLOWENOUGH -->|Yes| DONE[Ship]
```

The two non-negotiable rules:

1. **Never optimize without a measurement first.** If you can't show me the slow query or the slow function, you don't know what's slow.
2. **Never optimize without a measurement after.** If you can't show the latency improvement, you didn't optimize — you changed code.

### Mermaid: where the time goes — typical Flask bottleneck distribution

```mermaid
pie showData
    title Where wall-clock time disappears (well-tuned CRUD app)
    "Database round-trips" : 45
    "ORM hydration / serialization" : 18
    "Template render" : 12
    "External HTTP calls" : 10
    "Redis / cache" : 6
    "Network / TLS (LB to worker)" : 5
    "App business logic" : 4
```

---

## 2. Measurement Layer Cake

```mermaid
flowchart LR
    subgraph "Request Lifecycle"
        CLIENT[Client] --> CDN[CDN]
        CDN --> LB[Load Balancer]
        LB --> NGX[Nginx]
        NGX --> GUN[Gunicorn]
        GUN --> APP[Flask view]
        APP --> DB[(Database)]
        APP --> REDIS[(Redis)]
        APP --> EXT[External APIs]
    end

    subgraph "Metrics at each layer"
        M_CDN[Cache hit ratio<br/>Edge latency]
        M_LB[Request rate<br/>5xx rate]
        M_NGX[Upstream time<br/>Static cache hits]
        M_GUN[Worker utilization<br/>Queue depth]
        M_APP[p50/p95/p99 latency<br/>Per-route]
        M_DB[Query count<br/>Slow query log]
        M_REDIS[Hit ratio<br/>Evictions]
    end

    CDN -.-> M_CDN
    LB -.-> M_LB
    NGX -.-> M_NGX
    GUN -.-> M_GUN
    APP -.-> M_APP
    DB -.-> M_DB
    REDIS -.-> M_REDIS
```

Each layer has its own metric. You need all of them — "the API is slow" without "slow where" is not actionable.

### Key metrics

| Metric | What it tells you | Tool |
|---|---|---|
| **p50 latency** | Typical experience | `prometheus_flask_exporter`, APM |
| **p95 latency** | Most users' worst case | same |
| **p99 latency** | Tail; affects perceived reliability | same |
| **Throughput (req/s)** | Saturation point | same |
| **Error rate** | Often correlates with overload | Sentry, Prometheus |
| **DB query count per request** | N+1 detection | Flask-DebugToolbar, `EXPLAIN` |
| **Cache hit ratio** | Caching effectiveness | Redis `INFO` |
| **CPU / memory per worker** | Saturation, leaks | cAdvisor, Gunicorn stats |
| **Queue depth (Celery)** | Backlog | Flower, Redis `LLEN` |

> [!tip] Watch the tail, not the mean
> Mean latency hides problems. p50 = 50ms, p99 = 5000ms means 1 in 100 users has a terrible experience. Optimize the tail — that's where churn comes from.

---

## 3. Profiling Tools

### Flask-DebugToolbar (dev)

```bash
pip install flask-debugtoolbar
```

```python
from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension(app)
```

Shows on every HTML page: SQL queries with `EXPLAIN`, headers, template render time, request vars. **Dev only.**

### Flask-Silk (prod-safe, opt-in)

```bash
pip install flask-silk
```

```python
from silk import Silk
silk = Silk(app)

# Profile specific endpoints:
@app.route("/expensive")
@silk.profile()
def expensive():
    ...
```

Silk stores profiles in the DB, viewable at `/silk/`. Useful for profiling specific endpoints in staging.

### cProfile (one-off)

```python
import cProfile, pstats

@app.route("/profile-me")
def profile_me():
    pr = cProfile.Profile()
    pr.enable()
    result = expensive_computation()
    pr.disable()
    stats = pstats.Stats(pr).sort_stats("cumulative")
    stats.print_stats(20)
    return str(result)
```

### py-spy (prod sampling, no code changes)

```bash
pip install py-spy
py-spy top --pid <gunicorn-master-pid>
py-spy record --pid <pid> --duration 30 --output flame.svg
```

`py-spy` samples a running process and produces a flamegraph. No code changes, no slowdown — perfect for prod debugging.

### SQL logging

```python
# Quickly: log every query and its duration
import time, logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def before(conn, cursor, statement, params, context, executemany):
    context._query_start = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def after(conn, cursor, statement, params, context, executemany):
    elapsed = time.time() - context._query_start
    if elapsed > 0.1:  # log only slow queries
        logging.getLogger("sqlalchemy.slow").warning(
            f"{elapsed:.3f}s {statement[:200]} {params}"
        )
```

Or use the slow-query log in PostgreSQL itself (`log_min_duration_statement = 100`).

### Mermaid: profiling tools, by what they see

```mermaid
mindmap
  root((Profiling toolkit))
    Dev / in-process
      Flask-DebugToolbar
        SQL queries + EXPLAIN
        template render time
        headers / request vars
      Flask-Silk
        per-endpoint profiles
        stored in DB
        prod-safe opt-in
      cProfile
        one-off function
        pstats.sort_stats
    Prod / sampling
      py-spy
        no code changes
        sampling, low overhead
        flamegraph SVG
      perf / eBPF
        kernel-level
        syscall-level flamegraphs
    Database
        EXPLAIN ANALYZE
        slow query log
        pg_stat_statements
    Memory
      tracemalloc (stdlib)
        top-N allocations by line
      memray
        live mode + flamegraph
        allocation tree
    Frontend
      Browser DevTools (Performance)
      Lighthouse
      Sentry RUM / Datadog RUM
```

---

## 4. Database Optimization

### N+1 queries

The single most common performance bug in Flask apps.

```python
# BAD: 1 query for projects + N queries for their owners
projects = Project.query.all()
for p in projects:
    print(p.owner.name)   # ← query per project
```

**Fix: eager loading.**

```python
from sqlalchemy.orm import selectinload, joinedload

# Option A: selectinload — one extra query with IN (id, id, ...)
projects = db.session.execute(
    select(Project).options(selectinload(Project.owner))
).scalars().all()

# Option B: joinedload — single JOIN
projects = db.session.execute(
    select(Project).options(joinedload(Project.owner))
).scalars().all()
```

| Strategy | SQL | Use when |
|---|---|---|
| `selectinload` | 2 queries: parent + `WHERE id IN (...)` for children | Most cases. Avoids cartesian explosion on multi-level. |
| `joinedload` | 1 query with `LEFT JOIN` | One-to-one, or single child per parent. |
| `subqueryload` | 2 queries: parent + `WHERE id IN (SELECT ...)` | Rarely needed; legacy. |

> [!warning] `joinedload` on collections causes row explosion
> If you `joinedload(Project.tasks)` and a project has 100 tasks, you get 100 rows for one project — SQLAlchemy dedups in Python but you've moved 100× the data over the wire. Use `selectinload` for collections.

### Detection

```python
# Flask-SQLAlchemy 3.x: record queries per request
app.config["SQLALCHEMY_RECORD_QUERIES"] = True

from flask_sqlalchemy.record_queries import get_record_queries

@app.after_request
def log_query_count(resp):
    queries = get_record_queries()
    if len(queries) > 5:
        app.logger.warning(f"{len(queries)} queries on {request.path}")
        for q in queries:
            app.logger.warning(f"  {q.statement[:120]}")
    return resp
```

If you see "10 queries on /projects", you almost certainly have an N+1.

### Indexes

```python
# Add to model
class Task(db.Model):
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), index=True)
    status = db.Column(db.Enum(TaskStatus), index=True)
    created_at = db.Column(db.DateTime, index=True)

# Composite index for common filters
from sqlalchemy import Index
Index("idx_task_project_status", "project_id", "status")
```

Rules of thumb:
- Index columns you **filter** on (`WHERE`), not columns you `SELECT`.
- Index foreign keys (Postgres does NOT do this automatically).
- Composite indexes: order matters. `(project_id, status)` helps `WHERE project_id=? AND status=?` and `WHERE project_id=?`, but **not** `WHERE status=?`.
- Don't over-index — every index slows writes.

Verify with `EXPLAIN ANALYZE`:

```sql
EXPLAIN ANALYZE SELECT * FROM tasks WHERE project_id = 42 AND status = 'todo';
-- If you see "Seq Scan", you're missing an index.
-- If you see "Index Scan", good.
```

### Query optimization

```python
# BAD: loads all columns including a giant TEXT body
tasks = Task.query.all()

# GOOD: only the columns you need
from sqlalchemy import select
tasks = db.session.execute(
    select(Task.id, Task.title, Task.status).where(Task.project_id == 42)
).all()

# BAD: COUNT(*) on every page render
total = Task.query.count()

# GOOD: cache the count
total = cache.get_or_set(f"task_count:{project_id}", lambda: Task.query.count(), timeout=60)
```

### Connection pooling

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 20,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 1800,    # 30 min — recycle before DB/firewall kills idle conns
    "pool_pre_ping": True,   # test liveness before checkout
}
```

Math: `(pool_size + max_overflow) × workers ≤ postgres max_connections`. With 4 workers × 30 = 120 connections. Set Postgres `max_connections=200` to leave headroom.

For many workers, put [PgBouncer](https://www.pgbouncer.org/) in front (transaction-pooling mode) — see [[Production-Deployment]] §8.

### Read replicas

```python
SQLALCHEMY_BINDS = {
    "replica": "postgresql://user:pass@replica-host/db",
}

# Use the replica for reads:
from sqlalchemy import select
with db.session.connection(bind_key="replica") as conn:
    result = conn.execute(select(Task).where(...))
```

Or use [sqlalchemy-read-replica](https://github.com/mcalloc/sqlalchemy-read-replica) pattern: route `SELECT` to replica, writes to primary.

---

## 5. Caching Strategies

### Layer 1: HTTP caching (best — never hits your app)

```python
from flask import make_response

@app.route("/api/v1/projects/<int:pid>/tasks")
@cache.cached(timeout=60)
def list_tasks(pid):
    resp = make_response(jsonify(...))
    resp.headers["Cache-Control"] = "public, max-age=60"
    resp.headers["ETag"] = hashlib.md5(resp.data).hexdigest()
    return resp
```

Browsers and CDNs honor `Cache-Control` and `ETag`. A CDN cache hit is a 0ms response from your server's perspective.

### Layer 2: Application caching (Redis/Memcached)

```python
@cache.cached(timeout=300, key_prefix=lambda: f"tasks:p{request.args.get('p',1)}")
def list_tasks():
    return TaskSchema(many=True).dump(Task.query.all())
```

See [[Flask-Caching]] for the full API.

### Layer 3: Database query caching

Not recommended directly — SQLAlchemy doesn't cache results, and caching ORM objects leads to stale data. Cache **serialized output** (e.g., a Marshmallow-dumped dict) instead.

### Layer 4: Template caching

```python
from flask_caching import Cache
cache = Cache(app)

@app.route("/")
@cache.cached(timeout=600, key_prefix="home_page")
def home():
    return render_template("home.html", items=expensive_query())
```

Or cache fragments with [Jinja2's cache extension](https://jinja.palletsprojects.com/en/stable/templates/#extensions):

```jinja
{% cache 600, "sidebar" %}
  {{ render_sidebar() }}
{% endcache %}
```

### Cache invalidation

The hardest problem in CS. Three approaches:

```python
# 1. TTL — accept stale data for N seconds
@cache.cached(timeout=60)

# 2. Explicit — delete when underlying data changes
def update_task(task):
    ...
    cache.delete_memoized(get_task, task.id)
    cache.delete(f"task_list:p{task.project_id}")

# 3. Write-through — update cache as you write
def update_task(task):
    db.session.commit()
    cache.set(f"task:{task.id}", TaskSchema().dump(task), timeout=300)
```

> [!warning] Cache stampede
> When a popular cache entry expires, 1000 requests simultaneously miss the cache and compute the same expensive value. Fix with `cache.get_or_set(key, fn, timeout=N)` which uses a per-key lock — only one request computes, the rest wait.

---

## 6. Asynchronous Processing

### Celery for offloading

Anything that takes > 100ms should not be in the request path.

```python
@shared_task
def generate_report(user_id):
    # 5-second job
    return report_bytes

@app.route("/reports/<int:user_id>")
def request_report(user_id):
    job = generate_report.delay(user_id)
    return {"job_id": job.id}, 202   # client polls

@app.route("/reports/status/<job_id>")
def status(job_id):
    result = generate_report.AsyncResult(job_id)
    return {"state": result.state, "ready": result.ready()}
```

See [[Celery]] for the full pattern.

### Flask 2.x async views

```python
import asyncio, httpx

@app.route("/aggregate")
async def aggregate():
    async with httpx.AsyncClient() as client:
        a, b, c = await asyncio.gather(
            client.get("https://api.a.com/data"),
            client.get("https://api.b.com/data"),
            client.get("https://api.c.com/data"),
        )
    return jsonify([a.json(), b.json(), c.json()])
```

> [!warning] Async views don't make your app faster by themselves
> Flask still runs in a sync WSGI container. Each async view runs on an event loop in the worker, but if your worker is sync (default Gunicorn), the request still blocks a worker thread. To benefit, you need `gthread` workers, or `eventlet`/`gevent`, **and** the work must be I/O-bound. CPU-bound async is slower than sync.

### Async tasks inside sync Flask

Use a thread pool for CPU-bound or blocking I/O:

```python
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)

@app.route("/compute")
def compute():
    future = executor.submit(heavy_compute, arg)
    result = future.result(timeout=10)
    return jsonify(result)
```

Or use [anyio](https://anyio.readthedocs.io/) to bridge sync/async cleanly.

---

## 7. Concurrency: gevent / eventlet

For workloads with many idle connections (long-polling, WebSockets), async workers serve thousands of concurrent clients per process.

```python
# gunicorn.conf.py
worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1000   # up to 1000 sockets per worker
```

```python
# Monkey-patch very early in wsgi.py — before any DB driver import
import gevent.monkey
gevent.monkey.patch_all()

from app import create_app
app = create_app("production")
```

> [!danger] Monkey-patch before importing anything
> `psycopg2`, `requests`, `ssl` — all stdlib-based — must be imported **after** `monkey.patch_all()`. If you import them first, gevent's greenlets will deadlock on the original (blocking) socket implementation. Put `monkey.patch_all()` as the **first line** of `wsgi.py`.

For Flask-SocketIO, use `eventlet`:

```python
worker_class = "eventlet"
workers = 1   # multi-worker SocketIO needs Redis message queue — see Flask-SocketIO note
```

See [[Flask-SocketIO]] for the full discussion.

---

## 8. Static File & Asset Optimization

### Serve static files from Nginx or CDN, never from Flask

```nginx
location /static/ {
    alias /var/taskflow/app/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
    access_log off;
}
```

A Gunicorn worker serving a 1MB image is a worker not serving API requests. Static files belong in Nginx or a CDN.

### Fingerprint filenames for cache busting

```python
# Flask-Assets
from flask_assets import Environment, Bundle
assets = Environment(app)
js = Bundle("js/app.js", "js/utils.js", filters="jsmin", output="gen/app.%(version)s.js")
assets.register("js_all", js)
```

```html
{% assets "js_all" %}
<script src="{{ ASSET_URL }}"></script>
{% endassets %}
```

The `%(version)s` is a content hash — `app.a3f9c1.js`. When the content changes, the URL changes, so the browser fetches the new version. The CDN can use `immutable` cache.

### Compression

Enable gzip/brotli in Nginx:

```nginx
gzip on;
gzip_types text/plain application/json application/javascript text/css;
gzip_min_length 1024;
```

Or use [Flask-Compress](https://github.com/colour-science/flask-compress) if you can't touch Nginx:

```python
from flask_compress import Compress
Compress(app)
```

### Image optimization

- Convert PNG/JPEG to WebP/AVIF — 30-50% smaller.
- Use `srcset` for responsive images.
- Strip EXIF metadata on upload with Pillow.

```python
from PIL import Image
img = Image.open(upload)
img.save(dest, "WEBP", quality=82, method=6)
```

---

## 9. Memory Profiling

### tracemalloc (stdlib)

```python
import tracemalloc
tracemalloc.start()

# ... your code ...

snapshot = tracemalloc.take_snapshot()
top = snapshot.statistics("lineno")
for stat in top[:10]:
    print(stat)
```

### memray (modern, GUI)

```bash
pip install memray
memray run --live wsgi.py
# or
memray run -o output.bin wsgi.py
memray flamegraph output.bin
```

Shows allocations by file/function, with a flamegraph. Excellent for finding leaks.

### Common Flask leaks

| Leak | Cause | Fix |
|---|---|---|
| SQLAlchemy session not removed | Manual `Session()` not disposed | Use `db.session` (auto-removed on request teardown) |
| Growing cache | `cache.set` without TTL | Always set `timeout=` |
| SocketIO handlers holding refs | `socketio.on(...)` closures capture request scope | Don't store request-scoped objects in module-level dicts |
| Celery prefetch backlog | `worker_prefetch_multiplier` high | Set to 1 for long tasks |
| PIL images not closed | `Image.open()` without `with` | `with Image.open(...) as img:` |

### Gunicorn worker recycling

```python
# gunicorn.conf.py
max_requests = 1000              # recycle after 1000 requests
max_requests_jitter = 50         # randomize so they don't all restart together
```

A safety net for slow leaks — workers get fresh memory every 1000 requests.

---

## 10. Redis Optimization

### Pipeline commands

```python
# BAD: 4 round-trips
cache.set("a", 1)
cache.set("b", 2)
cache.set("c", 3)
cache.set("d", 4)

# GOOD: 1 round-trip
pipe = cache.cache._client.pipeline()
pipe.set("a", 1); pipe.set("b", 2); pipe.set("c", 3); pipe.set("d", 4)
pipe.execute()
```

### Use the right data structure

| Need | Structure |
|---|---|
| Counter | `INCR` / `INCRBY` |
| Set membership | `SADD` / `SISMEMBER` |
| Sorted leaderboard | `ZADD` / `ZREVRANGE` |
| Rate limit bucket | `INCR` + `EXPIRE` |
| Pub/sub | `PUBLISH` / `SUBSCRIBE` |
| Stream (Celery results) | `XADD` / `XREAD` |

### Monitor Redis

```bash
redis-cli INFO memory
redis-cli INFO stats
redis-cli SLOWLOG GET 10   # slow commands
```

Watch:
- `used_memory_rss` — actual RAM.
- `connected_clients` — should be bounded by your pool size.
- `evicted_keys` — if this grows on your broker Redis, you're losing tasks. Bad.

---

## 11. Load Testing

### Locust (Python, scriptable)

```python
# locustfile.py
from locust import HttpUser, task, between

class TaskFlowUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        r = self.client.post("/api/v1/auth/login", json={
            "email": "loadtest@taskflow.app",
            "password": "loadtest123",
        })
        self.token = r.json()["access_token"]
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(3)
    def list_tasks(self):
        self.client.get("/api/v1/projects/1/tasks")

    @task(1)
    def create_task(self):
        self.client.post("/api/v1/projects/1/tasks", json={"title": "load test"})
```

```bash
locust -f locustfile.py --host https://staging.taskflow.app
# Open http://localhost:8089, set users=200, spawn=10/s
```

### k6 (Go, faster, JS scripts)

```javascript
// loadtest.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 0 },
  ],
  thresholds: { http_req_duration: ['p(95)<500'] },
};

export default function () {
  const res = http.get('https://staging.taskflow.app/api/v1/projects/1/tasks', {
    headers: { Authorization: `Bearer ${__ENV.TOKEN}` },
  });
  check(res, { 'status 200': r => r.status === 200 });
  sleep(1);
}
```

```bash
k6 run --vus 100 --duration 5m loadtest.js
```

### What to look for

- **Throughput plateau** — the req/s where adding more users doesn't increase throughput. That's your saturation point.
- **Latency knee** — the load where p95 starts climbing exponentially. That's where queues are forming.
- **Error rate spike** — usually indicates a resource limit (DB connections, file descriptors).

### Performance budgets

Set thresholds in CI:

```yaml
# .github/workflows/loadtest.yml
- name: Run k6
  run: k6 run --env THRESHOLDS=true loadtest.js
  # Fails the build if p95 > 500ms or error rate > 1%
```

This prevents performance regressions from sneaking in.

---

## 12. Production Monitoring

### Prometheus + Grafana

```python
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)

# Default: http_request_duration_seconds, http_requests_total
metrics.register_default(
    metrics.summary(
        "flask_request_latency_by_path",
        "Request latency",
        labels={"path": lambda: request.path},
    ),
)

# Custom:
task_count = metrics.gauge("taskflow_tasks_total", "Total tasks")
@app.route("/tasks/create")
def create():
    ...
    task_count.inc()
```

Scrape `/metrics` from Prometheus; visualize in Grafana. Pre-built dashboards: [Flask dashboard](https://grafana.com/grafana/dashboards/11001).

### Sentry Performance

```python
sentry_sdk.init(
    dsn="...",
    traces_sample_rate=0.1,   # 10% of requests get full transaction
)
```

Sentry groups slow requests by endpoint, shows the slowest spans (DB queries, HTTP calls), and correlates with errors. Often faster to debug a specific slow endpoint in Sentry than in Prometheus.

### Real User Monitoring (RUM)

For the browser side: Sentry, Datadog RUM, or self-hosted with [OpenTelemetry web](https://opentelemetry.io/docs/demo/browser/). Tracks p75/p95 as experienced by users — different from server p95 because it includes network and rendering.

---

## 13. Putting It All Together: A 10x Improvement Recipe

```mermaid
gantt
    title Optimization phases — from 800ms p95 to 20ms
    dateFormat HH:mm
    axisFormat %H:%M
    section Measure
    Profile with Flask-Silk          :a1, 00:00, 5m
    Identify N+1 (60 queries)        :a2, after a1, 5m
    section Fix DB
    Add selectinload on relationships :b1, after a2, 10m
    Re-measure: 4 queries, 60ms      :b2, after b1, 5m
    Add composite index              :b3, after b2, 10m
    Re-measure: 20ms                 :b4, after b3, 5m
    section Add cache
    @cache.cached(timeout=60)        :c1, after b4, 10m
    HTTP Cache-Control header        :c2, after c1, 5m
    Re-measure: 1ms on cache hit     :c3, after c2, 5m
    section Push to edge
    Cloudflare CDN in front          :d1, after c3, 15m
    Re-measure: 0ms for cached users :d2, after d1, 5m
    section Verify
    Load test (k6) p95 stable        :e1, after d2, 20m
    Rollout + monitor Sentry         :e2, after e1, 30m
```

Imagine `/api/v1/projects/1/tasks` is taking 800ms at p95. The recipe:

1. **Profile** with Flask-Silk: turns out 60 queries, average 12ms each = 720ms in DB.
2. **Find the N+1**: `tasks = Project.query.get(...).tasks` lazily loads each task's `assignee` and `comments`.
3. **Eager load**: `selectinload(Project.tasks).selectinload(Task.assignee).selectinload(Task.comments)`. Down to 4 queries, 60ms.
4. **Add an index**: `Index("idx_task_project_status", "project_id", "status")`. The `WHERE` clause uses it; down to 20ms.
5. **Cache**: `@cache.cached(timeout=60, key_prefix=...)`. p95 first request 20ms, subsequent 1ms.
6. **HTTP cache header**: `Cache-Control: private, max-age=60`. The browser re-uses the response for 60s.
7. **CDN**: if responses are public (no per-user data), put Cloudflare in front. p95 for repeat visitors: 0ms.

Result: 800ms → 0ms for cached, 20ms for cold. A 40x improvement at the user level.

> [!tip] Optimization in priority order
> 1. Don't do the work (cache, CDN, redirect).<br>
> 2. Do the work closer to the user (edge cache, browser cache).<br>
> 3. Do less work (eager load, index, paginate, select fewer columns).<br>
> 4. Do the work in parallel (async, gevent).<br>
> 5. Do the work asynchronously (Celery, return 202).<br>
> 6. Do the work on faster hardware (more CPU, more workers, bigger DB).<br>
> Skip ahead and you'll spend money on instances when a 5-line code change would have fixed it.

### Mermaid: optimization effort vs payoff

```mermaid
quadrantChart
    title Optimization techniques — effort vs payoff
    x-axis Low effort --> High effort
    y-axis Low payoff --> High payoff
    quadrant-1 Big wins, costly
    quadrant-2 Big wins, cheap (do first!)
    quadrant-3 Tiny wins, cheap
    quadrant-4 Tiny wins, costly (skip)
    "Add an index": [0.2, 0.85]
    "selectinload eager": [0.3, 0.9]
    "Cache view": [0.35, 0.85]
    "HTTP Cache-Control": [0.15, 0.7]
    "CDN in front": [0.5, 0.85]
    "Switch to async workers": [0.6, 0.5]
    "PgBouncer pool": [0.5, 0.45]
    "Bigger DB instance": [0.4, 0.35]
    "Rewrite in Go": [0.95, 0.3]
```

---

## 14. Common Performance Anti-Patterns

| Anti-pattern | Cost | Fix |
|---|---|---|
| `Model.query.all()` then Python filter | Loads whole table | DB-level `WHERE` + pagination |
| Lazy loading in a template loop | N+1 queries | `selectinload` in the view |
| `time.sleep()` in a request | Blocks a worker for the duration | Use Celery, or `gevent.sleep()` |
| Calling external API in request path | Adds 100-1000ms latency | Cache response, or async |
| `jsonify` of huge list | Serialization bottleneck | Paginate, or stream |
| Missing index on FK | Seq scan on every join | `index=True` on FK columns |
| `@cache.cached()` without key prefix on auth'd view | Wrong user gets cached data | Include user_id in key |
| Per-request cache warmup | Cache miss every request | Warm at boot, or use longer TTL |
| Sync file I/O in request | Blocks worker | Stream or offload to Celery |
| Many small Celery tasks | Broker overhead > work | Batch into one task |
| `selectinload` on deep graphs | Cartesian explosion | Bound depth, or use DTOs |
| Gunicorn sync workers for WebSockets | Worker blocks per connection | Use `eventlet`/`gevent` |
| `db.session.commit()` in a loop | One transaction per row | Bulk: `session.add_all()` + one commit |
| Loading full ORM objects for counting | Materializes rows just to count | `select(func.count())` or `query.count()` |
| Re-encoding the same JSON on every request | CPU burn | Cache the serialized payload |
| No `pool_pre_ping` on long-lived workers | Stale-connection errors under load | Set `pool_pre_ping=True` |

### Streaming large responses

When you genuinely need to return a large payload (CSV export, NDJSON log dump), **don't build it in memory** — stream it:

```python
from flask import Response, stream_with_context

@app.route("/export/tasks.csv")
def export_tasks():
    def generate():
        yield "id,title,status,assignee\n"
        # Server-side cursor — streaming, not loading all into memory
        stmt = select(Task).execution_options(stream_results=True).yield_per(500)
        for task in db.session.execute(stmt).scalars():
            yield f"{task.id},{task.title},{task.status.value},{task.assignee_id}\n"
    return Response(
        stream_with_context(generate()),
        mimetype="text/csv",
        headers={"Content-Disposition": 'attachment; filename="tasks.csv"'},
    )
```

`stream_results=True` puts psycopg2 into server-side cursor mode — rows are fetched in batches of `yield_per`, never all at once. Combined with `stream_with_context`, the response is sent to the client in chunks while the query is still running.

> [!warning] Streaming + transaction mode PgBouncer don't mix
> Server-side cursors require a session-level connection. If you put PgBouncer in `transaction` mode in front of your DB, streaming queries will fail. Either use `session` mode (less efficient pooling) or run a separate connection pool for streaming queries.

### Bulk operations

```python
# BAD: 1000 INSERTs, 1000 round-trips
for item in items:
    db.session.add(Task(**item))
db.session.commit()

# GOOD: 1 INSERT, 1 round-trip
db.session.execute(Task.__table__.insert(), items)
db.session.commit()

# Or SQLAlchemy 2.0 bulk insert
db.session.execute(insert(Task), items)
```

For updates:

```python
# Bulk update — one statement, no Python loop
db.session.execute(
    update(Task).where(Task.project_id == 42).values(status=TaskStatus.done)
)
```

For 10k+ rows, this is 100× faster than the loop pattern.

---

## 15. Where To Go Next

- [[Production-Deployment]] — operational knobs (workers, Nginx tuning, PgBouncer).
- [[Common-Patterns]] — pagination, caching, background task patterns.
- [[Security-Best-Practices]] — performance is sometimes a security control (rate limits, timeouts).
- [[Full-Stack-Example]] — see these techniques applied to a real app.

---

## 16. References

- [Flask Performance Checklist](https://flask.palletsprojects.com/en/stable/performance/) — official.
- [SQLAlchemy ORM Performance](https://docs.sqlalchemy.org/en/20/faq/performance.html) — query optimization.
- [Gunicorn design doc](https://docs.gunicorn.org/en/stable/design.html) — how workers are scheduled.
- [py-spy](https://github.com/benfred/py-spy) — sampling profiler.
- [memray](https://github.com/bloomberg/memray) — memory profiler.
- [Locust](https://locust.io/) — load testing in Python.
- [k6](https://k6.io/) — modern load testing.
- [Prometheus Flask exporter](https://github.com/rycus86/prometheus_flask_exporter) — metrics.
- [The USE Method](https://brendangregg.com/usemethod.html) — Brendan Gregg's resource analysis framework.
- [High Performance Browser Networking](https://hpbn.co/) — Ilya Grigorik's book; not Flask-specific but the latency fundamentals apply.
