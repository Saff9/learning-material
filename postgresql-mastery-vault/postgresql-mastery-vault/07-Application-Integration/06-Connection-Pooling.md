---
tags: [postgresql, connection-pooling, pgbouncer]
---

# Connection Pooling

PostgreSQL forks a heavyweight OS process per connection (~5-10MB each). Without pooling, hundreds of app connections exhaust `max_connections` (default 100).

## PgBouncer

Lightweight connection pooler that multiplexes many client connections onto fewer server backends.

### Three Pooling Modes

| Mode | Connection Held | Best For | Caveat |
|------|-----------------|----------|--------|
| **Session** | Entire session | Need session state | No multiplexing benefit |
| **Transaction** | One transaction | **Most web apps (recommended)** | No session-level features |
| **Statement** | Single query | Stateless autocommit | No multi-statement transactions |

### Setup

```ini
# pgbouncer.ini
[databases]
myapp = host=127.0.0.1 port=5432 dbname=myapp

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

### Connection from App

```python
# Connect to PgBouncer (port 6432) instead of PostgreSQL (port 5432)
DSN = "dbname=myapp user=appuser password=secret host=localhost port=6432"
```

> [!important] Always use connection pooling in production
> For web apps and serverless, PgBouncer in transaction mode is mandatory. It prevents connection exhaustion under load and reduces memory usage.

## Next

- [[08-Projects/01-Study-Log-App|Build a Study Log App]]
- [[09-Cheat-Sheets/SQL-Cheat-Sheet|SQL Cheat Sheet]]
