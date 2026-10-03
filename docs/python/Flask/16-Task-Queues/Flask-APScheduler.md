---
title: Flask-APScheduler
tags:
  - flask
  - apscheduler
  - scheduler
  - cron
  - background-tasks
  - scheduling
  - triggers
  - job-stores
aliases:
  - flask-apscheduler
  - apscheduler
  - advanced-python-scheduler
related:
  - "[[Celery]]"
  - "[[Flask-RQ]]"
  - "[[Flask-Dramatiq]]"
  - "[[Flask-Huey]]"
  - "[[Flask-SQLAlchemy]]"
  - "[[Flask-Mail]]"
created: 2024-01-15
updated: 2024-01-15
---

# Flask-APScheduler

#flask #apscheduler #scheduler #cron #background-tasks #scheduling #triggers #job-stores

> [!info] In-process job scheduler — no separate worker required
> **APScheduler (Advanced Python Scheduler)** is a library for scheduling Python jobs to run at specific times or intervals. Unlike [[Celery]], [[Flask-RQ]], [[Flask-Dramatiq]], and [[Flask-Huey]], **APScheduler runs inside your Flask web process** — there is no broker, no separate worker process, and no external dependency beyond the optional job-store database.
>
> In Flask, APScheduler is the right choice when you want "run this every Monday at 9 AM" or "send these emails in 5 minutes" without standing up a worker. It pairs naturally with [[Flask-Mail]] for scheduled email, [[Flask-SQLAlchemy]] for daily rollups, and [[Flask-Caching]] for periodic cache refresh.

Think of APScheduler as a **wall calendar with alarm clocks**. The Flask process owns the calendar; every alarm fires a function inside that same process. There's no messenger, no courier, no separate kitchen — the calendar rings and your function runs right there in the same room. This is wonderfully simple, and it's also APScheduler's main limitation: if the Flask web process restarts mid-job, the job is lost unless you've configured a persistent job store.

---

## 1. Overview & Metaphor

### Why APScheduler exists

Task queues ([[Celery]], [[Flask-RQ]], [[Flask-Dramatiq]], [[Flask-Huey]]) all share one assumption: there is a separate worker process that pops work off a queue. That gives you durability and horizontal scale, but it adds infrastructure — a broker (Redis/RabbitMQ) and a daemon you have to supervise.

For a large class of Flask apps, that infrastructure is overkill:

- "Run this cleanup every night at 3 AM."
- "Send a welcome email 5 minutes after signup."
- "Refresh the cache of stock prices every 30 seconds."
- "Compute monthly aggregates on the 1st of each month."

These are **scheduling problems**, not **queueing problems**. APScheduler solves them with:

- **Triggers**: when a job should run (`date`, `interval`, `cron`).
- **Job stores**: where the schedule is persisted (memory, SQLAlchemy, MongoDB, Redis).
- **Executors**: how the job's function is run (thread pool, process pool, async).
- **Schedulers**: the top-level coordinator (`BackgroundScheduler`, `BlockingScheduler`, `AsyncIOScheduler`, `QtScheduler`, `TwistedScheduler`).

### APScheduler architecture

```mermaid
flowchart TB
    subgraph WebProcess[Flask web process]
        A[Application code] -->|add_job| S[Scheduler]
        S --> JS[Job store<br/>memory / sqlalchemy / redis / mongo]
        S --> E1[ThreadPoolExecutor]
        S --> E2[ProcessPoolExecutor]
        S --> E3[AsyncIOExecutor]
    end
    subgraph ExternalInfra[Optional external infra]
        DB[(PostgreSQL)]
        RD[(Redis)]
        MG[(MongoDB)]
    end
    JS -.persistent.-> DB
    JS -.persistent.-> RD
    JS -.persistent.-> MG
    E1 --> F[Job function runs in-process]
    E2 --> F
    E3 --> F
    F --> A2[Side effects: email, DB writes, cache updates]
```

| Component | Role | Example |
|---|---|---|
| **Scheduler** | Top-level coordinator; owns the event loop | `BackgroundScheduler()` |
| **Trigger** | Decides when a job fires | `CronTrigger`, `IntervalTrigger`, `DateTrigger` |
| **Job store** | Persists jobs between restarts | `MemoryJobStore`, `SQLAlchemyJobStore`, `RedisJobStore`, `MongoDBJobStore` |
| **Executor** | Runs the job function | `ThreadPoolExecutor`, `ProcessPoolExecutor`, `AsyncIOExecutor` |
| **Job** | The (func, trigger, args, kwargs) tuple | `scheduler.add_job(send_email, "cron", hour=7)` |

> [!note] APScheduler ≠ Celery beat
> Both can run "every Monday at 9 AM" jobs, but their models differ:
> - **APScheduler** runs the job **inside the scheduler process** (typically your Flask web process). No worker, no broker.
> - **[[Celery]] beat** schedules jobs by *enqueueing them onto the broker*; a separate worker picks them up.
> Beat is durable across many workers; APScheduler is simpler but tied to one process.

### How APScheduler compares to [[Celery]] beat and [[Flask-Huey]]

| Dimension | APScheduler | [[Celery]] beat | [[Flask-Huey]] |
|---|---|---|---|
| **Runs where?** | In-process (typically Flask web) | Beat process → enqueue to worker | Worker process |
| **Separate worker needed?** | No | Yes (worker + beat) | Yes (worker) |
| **External infra required?** | Optional (job store) | Yes (Redis/RabbitMQ) | Optional (SQLite/Redis) |
| **Triggers** | `date`, `interval`, `cron` | `crontab`, `schedule`, `eta`, `countdown` | `crontab`, `schedule(... delay=N)` |
| **Job stores** | Memory, SQLAlchemy, MongoDB, Redis, etcd | Schedule in beat config | SQLite, Redis, Memory |
| **Executors** | Thread, process, asyncio, gevent, tornado, qt | Prefork, eventlet, gevent, threads | Thread, process, greenlet |
| **Code complexity** | ~5k LOC, typed | ~50k LOC | ~2k LOC |
| **Best for** | In-process scheduling; single-host Flask | Distributed task processing | Lightweight worker-based |

> [!tip] Choose APScheduler when…
> …your scheduled jobs are short (< 30 s), idempotent, and tied to a single Flask host. Choose [[Celery]] beat when jobs are heavy, you need fan-out across many workers, or you already operate Celery. Choose [[Flask-Huey]] when you want periodic + ad-hoc background tasks with one worker process and SQLite storage.

---

## 2. Installation

```bash
# Core APScheduler
pip install "APScheduler>=3.10"

# Optional: SQLAlchemy job store (recommended for production)
pip install "SQLAlchemy>=2.0"

# Optional: Redis job store
pip install "redis>=5.0"

# Optional: MongoDB job store
pip install "pymongo>=4.5"

# Optional: asyncio support (APScheduler 3.x; native in 4.x)
pip install "APScheduler>=3.10"

# Optional: Flask-APScheduler thin wrapper (provides REST API)
pip install "Flask-APScheduler>=1.13"

# Optional: Sentry SDK for crash reporting
pip install "sentry-sdk>=1.40"
```

> [!warning] APScheduler 3.x vs 4.x
> APScheduler 4.x is a major rewrite that introduces async-first API and changes the public surface significantly. As of this writing, **3.x is the stable, widely-deployed line**. This guide covers 3.x; if you adopt 4.x, expect to rewrite your scheduler initialization and trigger configuration.

### No external infrastructure required

Unlike [[Celery]] and [[Flask-RQ]], APScheduler has no Docker dependencies for the basic case. The default in-memory job store is enough for dev/test; for production you add a SQLAlchemy job store pointing at your existing Postgres.

```yaml
# docker-compose.yml — only needed if you use the SQLAlchemy job store
version: "3.9"
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: secret
    ports: ["5432:5432"]
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

---

## 3. Configuration

### The `scheduler.py` module

The recommended pattern is to construct the scheduler in a factory function and attach it to the Flask app:

```python
# myapp/scheduler.py
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.redis import RedisJobStore
from flask import Flask

def make_scheduler(app: Flask) -> BackgroundScheduler:
    """Build an APScheduler instance bound to app config."""
    jobstores = {"default": MemoryJobStore()}
    executors = {
        "default": ThreadPoolExecutor(app.config.get("APSCHEDULER_THREADS", 10)),
        "process": ProcessPoolExecutor(app.config.get("APSCHEDULER_PROCESSES", 2)),
    }
    job_defaults = {
        "coalesce": True,            # collapse missed runs into one
        "max_instances": 1,          # only one instance of a job at a time
        "misfire_grace_time": 60,    # seconds late a job can still run
    }

    backend = app.config.get("APSCHEDULER_JOBSTORE", "memory")
    if backend == "sqlalchemy":
        jobstores["default"] = SQLAlchemyJobStore(
            url=app.config["APSCHEDULER_SQLALCHEMY_URL"],
            tablename=app.config.get("APSCHEDULER_TABLENAME", "apscheduler_jobs"),
        )
    elif backend == "redis":
        jobstores["default"] = RedisJobStore(
            host=app.config["APSCHEDULER_REDIS_HOST"],
            port=app.config.get("APSCHEDULER_REDIS_PORT", 6379),
            db=app.config.get("APSCHEDULER_REDIS_DB", 0),
        )
    elif backend == "memory":
        pass  # already set above
    else:
        raise ValueError(f"unsupported job store: {backend}")

    scheduler = BackgroundScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=app.config.get("APSCHEDULER_TIMEZONE", "UTC"),
    )
    return scheduler
```

```python
# myapp/__init__.py
from flask import Flask
from myapp.scheduler import make_scheduler

def create_app(config="myapp.settings.Production"):
    app = Flask(__name__)
    app.config.from_object(config)

    scheduler = make_scheduler(app)
    scheduler.start()
    app.extensions["scheduler"] = scheduler

    # Shut down cleanly when the app tears down
    import atexit
    atexit.register(lambda: scheduler.shutdown(wait=True))

    from myapp.routes import bp
    app.register_blueprint(bp)
    return app
```

### Full configuration reference

| Key | Default | What it does |
|---|---|---|
| `APSCHEDULER_JOBSTORE` | `"memory"` | Storage: `memory`, `sqlalchemy`, `redis`, `mongodb` |
| `APSCHEDULER_SQLALCHEMY_URL` | — | SQLAlchemy URL for the job store (when backend=sqlalchemy) |
| `APSCHEDULER_REDIS_HOST` | `"localhost"` | Redis host (when backend=redis) |
| `APSCHEDULER_REDIS_PORT` | `6379` | Redis port |
| `APSCHEDULER_REDIS_DB` | `0` | Redis database number |
| `APSCHEDULER_THREADS` | `10` | ThreadPoolExecutor size |
| `APSCHEDULER_PROCESSES` | `2` | ProcessPoolExecutor size (for CPU jobs) |
| `APSCHEDULER_TIMEZONE` | `"UTC"` | Timezone for cron triggers |
| `APSCHEDULER_TABLENAME` | `"apscheduler_jobs"` | SQL table for the job store |
| `APSCHEDULER_MISFIRE_GRACE_TIME` | `60` (s) | Late run grace period |
| `APSCHEDULER_COALESCE` | `True` | Collapse N missed runs into 1 |
| `APSCHEDULER_MAX_INSTANCES` | `1` | Max concurrent instances of one job |

```python
# myapp/settings.py
class Production:
    APSCHEDULER_JOBSTORE = "sqlalchemy"
    APSCHEDULER_SQLALCHEMY_URL = "postgresql://myapp:secret@postgres:5432/myapp"
    APSCHEDULER_THREADS = 20
    APSCHEDULER_PROCESSES = 2
    APSCHEDULER_TIMEZONE = "UTC"
    APSCHEDULER_MISFIRE_GRACE_TIME = 300
    APSCHEDULER_COALESCE = True
    APSCHEDULER_MAX_INSTANCES = 1

class Testing:
    APSCHEDULER_JOBSTORE = "memory"
    APSCHEDULER_THREADS = 1
```

> [!tip] Use `coalesce=True` for periodic jobs
> Without `coalesce`, if your Flask process is down for 5 hours during a `cron(minute="*")` job, you'll get 5 missed-run alerts and 5 immediate executions on restart. With `coalesce=True`, only one execution happens.

---

## 4. Basic Usage

### Defining jobs

APScheduler jobs are plain Python functions. You don't decorate them — you register them with the scheduler at app startup:

```python
# myapp/jobs.py
from myapp.extensions import mail, db
from myapp.models import User, EmailLog, Subscription
from flask_mail import Message
from flask import current_app, render_template

def send_welcome_email(user_id: int):
    """Send a personalized welcome email."""
    user = User.query.get(user_id)
    if not user:
        raise ValueError(f"no such user {user_id}")
    msg = Message(
        subject=f"Welcome to {current_app.config['SITE_NAME']}",
        recipients=[user.email],
        html=render_template("emails/welcome.html", user=user),
    )
    mail.send(msg)
    EmailLog.log(user.id, "welcome", "sent")
    db.session.commit()

def refresh_stock_cache():
    """Periodically refresh the stock price cache."""
    from myapp.extensions import cache
    prices = fetch_latest_prices()
    cache.set("stock_prices", prices, timeout=300)

def cleanup_expired_sessions():
    """Delete sessions older than 7 days."""
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=7)
    Session.query.filter(Session.updated_at < cutoff).delete()
    db.session.commit()

def send_daily_digest():
    """Send a daily digest email to all subscribers."""
    for user in User.query.filter_by(active=True).all():
        msg = Message(
            subject="Your daily digest",
            recipients=[user.email],
            body=render_template("emails/digest.txt", user=user),
        )
        mail.send(msg)
```

### Registering jobs at app startup

```python
# myapp/__init__.py (continued)
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta

def register_jobs(app, scheduler):
    """Register all scheduled jobs."""
    # Cron: every day at 07:00 UTC
    scheduler.add_job(
        send_daily_digest,
        trigger=CronTrigger(hour=7, minute=0),
        id="daily-digest",
        replace_existing=True,
    )

    # Interval: every 30 seconds
    scheduler.add_job(
        refresh_stock_cache,
        trigger=IntervalTrigger(seconds=30),
        id="refresh-stocks",
        replace_existing=True,
    )

    # Cron: every Sunday at 02:00 UTC
    scheduler.add_job(
        cleanup_expired_sessions,
        trigger=CronTrigger(day_of_week="sun", hour=2),
        id="cleanup-sessions",
        replace_existing=True,
    )

# In create_app():
register_jobs(app, scheduler)
```

### Scheduling one-off jobs from a Flask view

```python
# myapp/routes.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.post("/signup")
def signup():
    user_id = 42
    scheduler = current_app.extensions["scheduler"]
    # Send welcome email 5 minutes after signup
    scheduler.add_job(
        "myapp.jobs:send_welcome_email",
        trigger="date",
        run_date=datetime.utcnow() + timedelta(minutes=5),
        args=[user_id],
        id=f"welcome-{user_id}",
        replace_existing=True,
    )
    return jsonify({"user_id": user_id, "scheduled_for": "+5min"}), 202

@bp.post("/delayed-charge")
def delayed_charge():
    subscription_id = request.json["subscription_id"]
    scheduler = current_app.extensions["scheduler"]
    # Run in 1 hour
    scheduler.add_job(
        "myapp.jobs:charge_subscription",
        trigger="date",
        run_date=datetime.utcnow() + timedelta(hours=1),
        args=[subscription_id],
    )
    return jsonify({"status": "scheduled"}), 202
```

### Inspecting scheduled jobs

```python
# myapp/routes/admin.py
@bp.get("/admin/jobs")
def list_jobs():
    scheduler = current_app.extensions["scheduler"]
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "func": str(job.func_ref),
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
        })
    return jsonify({"jobs": jobs})

@bp.delete("/admin/jobs/<job_id>")
def remove_job(job_id: str):
    scheduler = current_app.extensions["scheduler"]
    scheduler.remove_job(job_id)
    return jsonify({"removed": job_id})
```

> [!example] Scheduler lifecycle
> 1. `BackgroundScheduler.start()` spawns a thread that wakes up every `1` second (configurable).
> 2. Each wake: query job store for jobs whose `next_run_time <= now`.
> 3. For each due job, submit it to its executor (thread or process pool).
> 4. After completion, compute the next run time from the trigger and update the job store.
> 5. On `shutdown(wait=True)`, scheduler waits for running jobs to finish before exiting.

```mermaid
sequenceDiagram
    participant A as App startup
    participant S as Scheduler
    participant JS as JobStore
    participant E as ThreadPoolExecutor
    participant F as Job function

    A->>S: scheduler.start()
    A->>S: add_job(daily_digest, CronTrigger(hour=7))
    S->>JS: persist job
    loop every 1s
        S->>JS: get_jobs_due(now)
        JS-->>S: list of due jobs
        S->>E: submit job
        E->>F: call func(*args, **kwargs)
        F-->>E: return / raise
        E-->>S: result / exception
        S->>JS: update next_run_time
    end
    A->>S: shutdown(wait=True)
    S->>E: wait for running
    S-->>A: stopped
```

---

## 5. Intermediate Patterns

### The three trigger types

```mermaid
mindmap
  root((Triggers))
    DateTrigger
      Run once
      run_date=...
      Use case: delayed one-offs
    IntervalTrigger
      Run every N seconds
      seconds/minutes/hours
      Use case: cache refresh, polling
    CronTrigger
      Cron expression
      year/month/day/weekday/hour/minute/second
      Use case: scheduled reports, daily cleanup
```

```python
# DateTrigger — one-shot, run at a specific moment
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta

scheduler.add_job(
    "myapp.jobs:charge_subscription",
    trigger=DateTrigger(run_date=datetime(2024, 12, 31, 23, 59)),
    args=[42],
)

# IntervalTrigger — run every N seconds/minutes/hours
from apscheduler.triggers.interval import IntervalTrigger

scheduler.add_job(
    "myapp.jobs:refresh_stock_cache",
    trigger=IntervalTrigger(minutes=5),
    id="refresh-stocks",
)

# CronTrigger — Unix cron semantics
from apscheduler.triggers.cron import CronTrigger

scheduler.add_job(
    "myapp.jobs:send_daily_digest",
    trigger=CronTrigger(hour=7, minute=0),
    id="daily-digest",
)

scheduler.add_job(
    "myapp.jobs:weekly_report",
    trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
    id="weekly-report",
)

# Last day of every month at midnight
scheduler.add_job(
    "myapp.jobs:monthly_billing",
    trigger=CronTrigger(day="last", hour=0, minute=0),
    id="monthly-billing",
)

# Every weekday (Mon-Fri) at 09:00 and 18:00
scheduler.add_job(
    "myapp.jobs:commute_alert",
    trigger=CronTrigger(day_of_week="mon-fri", hour="9,18"),
    id="commute-alert",
)
```

### Cron trigger evaluation

```mermaid
flowchart TD
    N[Now: 2024-03-15 09:00:05 UTC] --> C{CronTrigger<br/>hour=9, minute=0}
    C -->|matches year| Y{year: '*'}
    Y -->|matches month| M{month: '*'}
    M -->|matches day| D{day: '*'}
    D -->|matches weekday| W{day_of_week: '*'}
    W -->|matches hour| H{hour: '9'}
    H -->|matches minute| Mi{minute: '0'}
    Mi -->|matches second| S{second: '0'}
    S --> Fire[Fire job!]
    S -->|no match| Next[Compute next_run_time<br/>= 2024-03-16 09:00:00]
    Next --> Store[Update JobStore]
```

### Misfire policies

When the scheduler is offline at a job's scheduled time, the job is "misfired". APScheduler offers three policies:

| Policy | Behavior |
|---|---|
| `misfire_grace_time=N` (default 1s) | If the job runs within N seconds of its scheduled time, run it; otherwise skip. |
| `coalesce=True` (default False) | If multiple runs were missed, collapse into one. |
| `max_instances=1` (default 1) | Don't start a new instance if one is still running. |

```python
scheduler.add_job(
    "myapp.jobs:heavy_rollup",
    trigger=CronTrigger(hour=2),
    id="daily-rollup",
    misfire_grace_time=3600,       # tolerate 1 hour late
    coalesce=True,
    max_instances=1,
    replace_existing=True,
)
```

### Job listeners (events)

Subscribe to scheduler events for logging, metrics, Sentry capture:

```python
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED

def job_listener(event):
    if event.code == EVENT_JOB_EXECUTED:
        current_app.logger.info(f"job {event.job_id} succeeded: {event.retval}")
    elif event.code == EVENT_JOB_ERROR:
        import sentry_sdk
        sentry_sdk.capture_exception(event.exception)
        current_app.logger.exception(f"job {event.job_id} failed: {event.exception}")
    elif event.code == EVENT_JOB_MISSED:
        current_app.logger.warning(f"job {event.job_id} missed its schedule")

scheduler.add_listener(job_listener,
                       EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED)
```

### Pass data into jobs

APScheduler serializes the args/kwargs of a job. If you use a persistent job store, they must be picklable:

```python
# Good: pass primitive IDs
scheduler.add_job("myapp.jobs:send_email", "date",
                  run_date=run_at, args=[user_id, template_name])

# Bad: pass a SQLAlchemy object — won't pickle cleanly
scheduler.add_job("myapp.jobs:send_email", "date",
                  run_date=run_at, args=[user_obj, template_name])
```

---

## 6. Advanced Usage

### ProcessPoolExecutor for CPU-bound jobs

By default, jobs run in a thread pool — which means they share the GIL. For CPU-bound work (image processing, ML inference, big CSV parsing), use the process executor:

```python
# Define the executor at scheduler construction
executors = {
    "default": ThreadPoolExecutor(10),
    "process": ProcessPoolExecutor(2),
}

# Route specific jobs to the process pool
scheduler.add_job(
    "myapp.jobs:generate_thumbnail",
    trigger=CronTrigger(hour=3),
    args=["/uploads/2024/03/big_video.mp4"],
    executor="process",          # use process pool
    misfire_grace_time=600,
)
```

### AsyncIOScheduler for async Flask

If you're using Flask 2.3+ with async views, the `AsyncIOScheduler` runs jobs as coroutines:

```python
# myapp/scheduler.py (async variant)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor

def make_async_scheduler(app):
    scheduler = AsyncIOScheduler(
        jobstores={"default": MemoryJobStore()},
        executors={"default": AsyncIOExecutor()},
        job_defaults={"coalesce": True, "max_instances": 1},
    )
    return scheduler
```

```python
# An async job
async def refresh_cache_async():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.example.com/prices")
        cache.set("prices", r.json())

scheduler.add_job(refresh_cache_async, "interval", seconds=30)
```

### SQLAlchemy job store with PostgreSQL

```python
jobstores = {
    "default": SQLAlchemyJobStore(
        url="postgresql://myapp:secret@postgres:5432/myapp",
        tablename="apscheduler_jobs",
        # Optional: use an existing engine
        # engine=engine,
    ),
}
```

> [!warning] Multiple processes + SQLAlchemy job store = leader election
> If you run multiple Flask web processes (gunicorn `--workers 4`) all hitting the same SQLAlchemy job store, every process will try to fire every job — duplicate execution. APScheduler has no built-in leader election. Solutions:
> 1. **Run the scheduler in only one process** (a dedicated worker process or a `gunicorn --preload` master).
> 2. **Use Redis `SETNX`-based leader election** — your scheduler's `start()` becomes conditional on acquiring the lock.
> 3. **Use [[Celery]] beat** — it's designed for this.

### Flask-APScheduler thin wrapper

`Flask-APScheduler` adds a REST API on top of APScheduler so you can manage jobs over HTTP:

```bash
pip install Flask-APScheduler
```

```python
# myapp/__init__.py
from flask_apscheduler import APScheduler

def create_app():
    app = Flask(__name__)
    app.config["SCHEDULER_API_PREFIX"] = "/scheduler"
    app.config["SCHEDULER_API_ENABLED"] = True
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    # ...
    return app

# Now you can:
#   GET  /scheduler/jobs                → list all jobs
#   POST /scheduler/jobs                → add a job
#   GET  /scheduler/jobs/<id>           → get one job
#   DELETE /scheduler/jobs/<id>         → remove a job
#   PATCH /scheduler/jobs/<id>          → reschedule
#   POST /scheduler/jobs/<id>/pause     → pause
#   POST /scheduler/jobs/<id>/resume    → resume
```

### Pausing and resuming

```python
scheduler.pause_job("daily-digest")        # stop firing, keep in store
scheduler.resume_job("daily-digest")       # resume firing
scheduler.reschedule_job(
    "daily-digest",
    trigger=CronTrigger(hour=8, minute=30),  # change the trigger
)
scheduler.modify_job("daily-digest", args=[42])  # change args
```

### Job listeners for execution-time metrics

```python
import time
from apscheduler.events import EVENT_JOB_SUBMITTED, EVENT_JOB_EXECUTED

durations = {}

def submitted_listener(event):
    durations[event.job_id] = time.monotonic()

def executed_listener(event):
    start = durations.pop(event.job_id, None)
    if start:
        duration = time.monotonic() - start
        prometheus_histogram.labels(job=event.job_id).observe(duration)

scheduler.add_listener(submitted_listener, EVENT_JOB_SUBMITTED)
scheduler.add_listener(executed_listener, EVENT_JOB_EXECUTED)
```

---

## 7. Common Pitfalls & Troubleshooting

### "Jobs fire twice"

This is the #1 APScheduler pitfall and it has two main causes:

1. **Multiple gunicorn/uwsgi workers** all running the scheduler. Fix: run scheduler in only one process (a dedicated worker, or `gunicorn --preload`).
2. **Persistent job store + coalesce=False**: missed runs replay on restart. Fix: set `coalesce=True`.

### "Jobs don't fire after deploy"

- If you use `MemoryJobStore`, every process restart wipes the schedule. Use `SQLAlchemyJobStore` for persistence.
- If you use `SQLAlchemyJobStore`, ensure the table exists. APScheduler creates it lazily on first write; if the database user lacks DDL permission, jobs won't persist.
- Did you call `scheduler.start()` in `create_app()`? On gunicorn, `--preload` ensures it runs once.

### "Job fails silently"

- Check the listener — `EVENT_JOB_ERROR` fires when a job raises. Without a listener, exceptions are swallowed.
- Check `job.next_run_time` after a failure. If the job has no `next_run_time` (e.g., DateTrigger), it's gone — re-add if you need to retry.

### "Database is locked" (SQLite job store)

SQLite is single-writer. Under high scheduling throughput you'll see `database is locked`. Switch to PostgreSQL or Redis.

### "Cron fires at the wrong time"

- Check `timezone`. The default is the system timezone; in Docker this is UTC. Be explicit: `CronTrigger(hour=7, minute=0, timezone="UTC")`.
- Check `day_of_week` semantics: APScheduler uses `0-6` (Sun–Sat) or `mon-sun`. Mixing them causes confusion.

### "ProcessPoolExecutor jobs raise `PicklingError`"

Functions passed to the process pool must be importable (top-level in a module) and their args must be picklable. Lambdas and closures won't work.

> [!example] Diagnostic flowchart
> ```mermaid
> flowchart TD
>     A[Job didn't fire] --> B{Scheduler started?}
>     B -- no --> C[scheduler.start()]
>     B -- yes --> D{Job in store?}
>     D -- no --> E[Re-add job; use persistent store]
>     D -- yes --> F{next_run_time in future?}
>     F -- no --> G[Check misfire_grace_time]
>     F -- yes --> H[Wait / check timezone]
>     G --> I{coalesce=True?}
>     I -- no --> J[Set coalesce=True]
>     I -- yes --> K[Check listener for EVENT_JOB_ERROR]
> ```

---

## 8. Best Practices

1. **One scheduler per app.** Build it in `create_app()`, attach to `app.extensions["scheduler"]`, start once.
2. **Use a persistent job store in production.** `SQLAlchemyJobStore` backed by Postgres survives restarts. `MemoryJobStore` is fine for dev.
3. **Run the scheduler in only one process.** If you have multiple gunicorn workers, use `--preload` or a dedicated scheduler process to avoid duplicate execution.
4. **Set `coalesce=True` and `max_instances=1` globally** via `job_defaults`. These are sensible for 95% of periodic jobs.
5. **Always set `misfire_grace_time`.** Default 1s is too short for most real jobs. 60–300s is a sensible default.
6. **Use `ProcessPoolExecutor` for CPU-bound jobs.** Threads share the GIL; a 30-second CPU job blocks the scheduler thread.
7. **Pass IDs and primitives, not objects.** Job args go through pickle for the persistent store. Pass `user_id`, not `User` instances.
8. **Add a listener for `EVENT_JOB_ERROR`.** Without one, exceptions vanish silently.
9. **Don't use APScheduler as a general task queue.** It's a scheduler, not a queue — there's no retry policy, no backoff, no priority. If you need those, use [[Celery]] or [[Flask-Dramatiq]].
10. **Pin `APScheduler>=3.10,<4.0`** until 4.x stabilizes. The 4.x rewrite changes the public API.

---

## 9. Integration with Other Extensions

### [[Flask-Mail]] — scheduled email

The most common use case. Wrap `mail.send()` in a scheduled job:

```python
def send_daily_digest():
    from flask import render_template
    from flask_mail import Message
    from myapp.extensions import mail
    from myapp.models import User
    for user in User.query.filter_by(active=True).all():
        msg = Message(
            subject="Your daily digest",
            recipients=[user.email],
            html=render_template("emails/digest.html", user=user),
        )
        mail.send(msg)

scheduler.add_job(
    send_daily_digest,
    trigger=CronTrigger(hour=7, minute=0),
    id="daily-digest",
)
```

### [[Flask-SQLAlchemy]] — DB-bound jobs

Jobs run inside the Flask app context if you push it manually:

```python
from contextlib import contextmanager
from flask import current_app

@contextmanager
def app_context():
    from myapp import create_app
    app = create_app()
    with app.app_context():
        yield

def daily_rollup():
    with app_context():
        from myapp.extensions import db
        from myapp.models import Order
        Order.rollup_yesterday()
        db.session.commit()

scheduler.add_job(daily_rollup, CronTrigger(hour=2), id="daily-rollup")
```

Or push context once for the whole scheduler thread:

```python
# Wrap scheduler.start() with app context
def start_scheduler(app):
    with app.app_context():
        scheduler.start()
```

### [[Flask-Caching]] — periodic refresh

APScheduler is ideal for "refresh this cache every N seconds":

```python
def refresh_prices():
    from myapp.extensions import cache
    prices = fetch_latest_prices()
    cache.set("stock_prices", prices, timeout=300)

scheduler.add_job(refresh_prices, IntervalTrigger(seconds=30), id="refresh-prices")
```

### [[Celery]] — when to migrate

APScheduler → [[Celery]] migration paths:

- One-off `DateTrigger` → `task.apply_async(eta=...)`
- `IntervalTrigger` → `beat_schedule` with `schedule=N`
- `CronTrigger` → `beat_schedule` with `crontab(hour=…, minute=…)`
- `ProcessPoolExecutor` jobs → Celery prefork workers
- Event listeners → Celery signals (`task_success`, `task_failure`)

Migrate when you need:
- Retries with backoff
- Distributed fan-out (multiple worker hosts)
- A separate worker process for crash isolation
- Priority queues or complex routing

### [[Flask-Huey]] — combining the two

A common pattern: APScheduler in the web process triggers Huey tasks for the heavy lifting. This keeps scheduling lightweight (no beat process) while offloading work to a worker:

```python
def trigger_daily_billing():
    from myapp.tasks import run_daily_billing
    run_daily_billing()   # enqueues onto Huey

scheduler.add_job(
    trigger_daily_billing,
    CronTrigger(hour=2),
    id="trigger-daily-billing",
)
```

### [[Flask-SocketIO]] — periodic broadcasts

Pair APScheduler with [[Flask-SocketIO]] to push periodic updates to browsers:

```python
def broadcast_stock_prices():
    from myapp.extensions import socketio
    from myapp.extensions import cache
    prices = cache.get("stock_prices") or {}
    socketio.emit("prices", prices)

scheduler.add_job(broadcast_stock_prices, IntervalTrigger(seconds=5), id="broadcast-prices")
```

---

## 10. Real-World Example

A multi-tenant SaaS that needs:
1. Daily rollups per tenant (heavy DB work, run at 02:00 UTC).
2. Hourly cache refresh (lightweight, run every hour at minute 0).
3. Welcome email 5 minutes after signup (one-shot).
4. Weekly invoice generation on Mondays at 09:00 UTC.
5. Prometheus metrics on every job execution.

```python
# myapp/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from prometheus_client import Histogram
import sentry_sdk

JOB_DURATION = Histogram(
    "apscheduler_job_duration_seconds",
    "Duration of APScheduler jobs",
    ["job_id"],
)

def make_scheduler(app):
    scheduler = BackgroundScheduler(
        jobstores={
            "default": SQLAlchemyJobStore(
                url=app.config["APSCHEDULER_SQLALCHEMY_URL"],
                tablename="apscheduler_jobs",
            ),
        },
        executors={
            "default": ThreadPoolExecutor(20),
            "process": ProcessPoolExecutor(2),
        },
        job_defaults={
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": 300,
        },
        timezone="UTC",
    )

    # Listener for metrics + error capture
    import time
    durations = {}

    def on_submitted(event):
        durations[event.job_id] = time.monotonic()

    def on_executed(event):
        start = durations.pop(event.job_id, None)
        if start:
            JOB_DURATION.labels(job_id=event.job_id).observe(time.monotonic() - start)
        if event.code == EVENT_JOB_ERROR:
            sentry_sdk.capture_exception(event.exception)
            app.logger.exception(f"job {event.job_id} failed: {event.exception}")

    from apscheduler.events import EVENT_JOB_SUBMITTED
    scheduler.add_listener(on_submitted, EVENT_JOB_SUBMITTED)
    scheduler.add_listener(on_executed, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    return scheduler
```

```python
# myapp/jobs.py
from datetime import datetime, timedelta
from myapp.extensions import db, mail, cache
from myapp.models import Tenant, Order, Invoice, User
from flask import current_app, render_template
from flask_mail import Message

def daily_rollup_for_tenant(tenant_id: int):
    """Heavy DB rollup — runs in the process pool."""
    tenant = Tenant.query.get(tenant_id)
    Order.rollup_yesterday(tenant)
    db.session.commit()

def daily_rollup_all_tenants():
    """Trigger per-tenant rollups."""
    for tenant in Tenant.query.filter_by(active=True).all():
        # Submit each to the process pool
        from flask import current_app
        scheduler = current_app.extensions["scheduler"]
        scheduler.add_job(
            daily_rollup_for_tenant,
            executor="process",
            args=[tenant.id],
            id=f"daily-rollup-{tenant.id}-{datetime.utcnow().date()}",
        )

def refresh_cache():
    """Lightweight cache refresh — runs in the thread pool."""
    prices = fetch_latest_prices()
    cache.set("stock_prices", prices, timeout=3600)

def send_welcome_email(user_id: int):
    user = User.query.get(user_id)
    if not user:
        return
    msg = Message(
        subject=f"Welcome to {current_app.config['SITE_NAME']}",
        recipients=[user.email],
        html=render_template("emails/welcome.html", user=user),
    )
    mail.send(msg)

def generate_weekly_invoices():
    """Monday 09:00 UTC — generate invoices for all active tenants."""
    for tenant in Tenant.query.filter_by(active=True).all():
        invoice = Invoice.generate_weekly(tenant)
        db.session.add(invoice)
        msg = Message(
            subject=f"Invoice #{invoice.id}",
            recipients=[tenant.billing_email],
            html=render_template("emails/invoice.html", invoice=invoice),
        )
        mail.send(msg)
    db.session.commit()
```

```python
# myapp/__init__.py
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import timedelta

def register_jobs(app, scheduler):
    # Daily rollup at 02:00 UTC
    scheduler.add_job(
        "myapp.jobs:daily_rollup_all_tenants",
        trigger=CronTrigger(hour=2, minute=0),
        id="daily-rollup",
        replace_existing=True,
    )

    # Hourly cache refresh
    scheduler.add_job(
        "myapp.jobs:refresh_cache",
        trigger=CronTrigger(minute=0),
        id="hourly-cache-refresh",
        replace_existing=True,
    )

    # Weekly invoice generation on Mondays at 09:00 UTC
    scheduler.add_job(
        "myapp.jobs:generate_weekly_invoices",
        trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
        id="weekly-invoices",
        replace_existing=True,
    )

# In a Flask view, schedule the welcome email 5 minutes after signup
@bp.post("/signup")
def signup():
    user_id = 42
    from datetime import datetime, timedelta
    scheduler = current_app.extensions["scheduler"]
    scheduler.add_job(
        "myapp.jobs:send_welcome_email",
        trigger=DateTrigger(run_date=datetime.utcnow() + timedelta(minutes=5)),
        args=[user_id],
        id=f"welcome-{user_id}",
        replace_existing=True,
    )
    return jsonify({"user_id": user_id}), 202
```

```mermaid
gantt
    title Weekly APScheduler rhythm (UTC)
    dateFormat  HH:mm
    axisFormat  %H:%M
    section Daily
    Cache refresh (every hour)    :crit, 00:00, 23h
    Daily rollup (02:00)          :done, 02:00, 30m
    section Weekly
    Weekly invoices (Mon 09:00)   :crit, mon 09:00, 1h
```

```mermaid
flowchart TB
    subgraph WebProcess[Flask web process]
        V[/POST /signup/] --> S[Scheduler]
        S -->|DateTrigger +5min| J1[send_welcome_email]
        S -->|CronTrigger hour=2| J2[daily_rollup_all_tenants]
        J2 -->|submits N jobs| P[ProcessPoolExecutor]
        S -->|CronTrigger minute=0| J3[refresh_cache]
        S -->|CronTrigger Mon 9| J4[generate_weekly_invoices]
    end
    subgraph ExternalResources
        DB[(PostgreSQL)]
        M[(SMTP)]
        C[(Redis cache)]
    end
    J1 --> M
    J2 --> P
    P --> DB
    J3 --> C
    J4 --> DB
    J4 --> M
    S --> JS[(SQLAlchemy<br/>JobStore)]
    JS <--> DB
```

---

## 11. References

- **Official docs**: <https://apscheduler.readthedocs.io>
- **Source repo**: <https://github.com/agronholm/apscheduler>
- **Triggers reference**: <https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html>
- **Job stores reference**: <https://apscheduler.readthedocs.io/en/3.x/userguide.html#stores>
- **Flask-APScheduler**: <https://github.com/viniciuschiele/flask-apscheduler>
- **Companion notes**: [[Celery]], [[Flask-RQ]], [[Flask-Dramatiq]], [[Flask-Huey]]
- **Internal patterns**: [[Project-Structure]], [[Performance-Optimization]], [[Security-Best-Practices]]

> [!quote] Alex Grönholm, APScheduler author
> "APScheduler is a light but powerful in-process task scheduler that lets you schedule jobs (functions or any other callables) to be executed at specific times or intervals. It supports a variety of triggers, job stores and executors, and can be used in a wide variety of Python applications."

Related pages you should read next:
- [[Celery]] — for the comparison baseline and beat scheduling
- [[Flask-RQ]] — when you need a separate worker
- [[Flask-Dramatiq]] — when you want middleware
- [[Flask-Huey]] — lightweight worker-based alternative with built-in crontab
