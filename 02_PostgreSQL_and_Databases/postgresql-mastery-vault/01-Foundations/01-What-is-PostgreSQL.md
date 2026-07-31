---
tags: [postgresql, foundations, beginner]
---

# What is PostgreSQL?

PostgreSQL (often called "Postgres") is a powerful, open-source, object-relational database system. It has earned a strong reputation for reliability, feature robustness, and performance. As of 2026, PostgreSQL 18 is the current stable release, with PostgreSQL 19 in beta.

## Why PostgreSQL?

> [!tip] PostgreSQL is the default choice for new web applications in 2026
> It has become the "boring technology" choice — reliable, proven, and capable of handling almost any data workload.

### Key Strengths

1. **Open source and free** — PostgreSQL License (BSD-like), no licensing costs ever
2. **ACID compliant** — guaranteed data integrity with transactions
3. **Extensible** — add types, functions, languages, and indexes via extensions
4. **Rich type system** — JSON/JSONB, arrays, ranges, geometric, network addresses, UUID, and more
5. **Full-text search** — built-in, no need for Elasticsearch for most use cases
6. **Geospatial support** — PostGIS extension is the gold standard for spatial data
7. **Replication** — both physical (streaming) and logical replication built-in
8. **Standards compliant** — closely follows SQL standards
9. **Massive ecosystem** — hosting providers, ORMs, tools, and community support everywhere

### PostgreSQL vs MySQL vs SQLite

| Feature | SQLite | MySQL | PostgreSQL |
|---------|--------|-------|------------|
| Architecture | Embedded file | Client-server | Client-server (ORDBMS) |
| Setup | Zero (one file) | Low | Low-medium |
| Data types | Basic | Good | Exceptional (JSONB, arrays, ranges, geo) |
| JSON quality | Text only | Good | Best (JSONB + GIN + SQL/JSON) |
| Full-text search | FTS5 module | Built-in | tsvector + pg_trgm |
| Strictness | Lenient | Lenient (STRICT mode now) | Strict by default |
| Best for | Mobile, embedded, prototypes | Simple web apps, read-heavy | Complex domains, analytics, SaaS |

> [!note] When to use PostgreSQL
> Use PostgreSQL when you need: complex data, JSON documents, geospatial data, analytics mixed with transactions, financial/strict data integrity, multi-tenant SaaS, full-text search, or when you want one database that can do everything well.

## PostgreSQL Architecture (Simplified)

```
Client (psql, app) <---> PostgreSQL Server
                           |
                           +-- Postmaster (main process)
                           +-- Backend processes (one per connection)
                           +-- Shared memory (shared_buffers)
                           +-- WAL (Write-Ahead Log)
                           +-- Data files
```

- **Postmaster**: The main process that listens for connections and forks a backend process for each client
- **Backend process**: One per connection — handles query parsing, planning, execution
- **Shared buffers**: In-memory cache shared across all backends (default 128MB, tune to 25% of RAM)
- **WAL**: Write-Ahead Log — records all changes before they are written to data files (for crash recovery)
- **Data files**: The actual table and index data on disk

### MVCC (Multi-Version Concurrency Control)

PostgreSQL uses MVCC, which means:
- **Readers never block writers** — SELECT statements see a consistent snapshot
- **Writers never block readers** — UPDATE/DELETE create new row versions, old ones remain until VACUUM
- Each transaction sees a consistent snapshot of the database

This is why PostgreSQL handles concurrent access so well, and why VACUUM is important (it cleans up old row versions).

## PostgreSQL Version History (Recent)

| Version | Release Date | Key Features | Support Until |
|---------|-------------|--------------|---------------|
| 15 | Oct 2022 | MERGE command, logical replication improvements | Nov 2027 |
| 16 | Sep 2023 | Parallel query improvements, logical replication | Nov 2028 |
| 17 | Sep 2024 | JSON_TABLE, MERGE RETURNING, incremental backups | Nov 2027 |
| 18 | Sep 2025 | Async I/O, UUIDv7, virtual generated columns, OAuth | Nov 2028 |
| 19 Beta | Jun 2026 | REPACK CONCURRENTLY, parallel autovacuum, SQL/PGQ | GA ~Sep 2026 |

See [[11-Resources/PostgreSQL-Versions|PostgreSQL Versions]] for full details.

## What You Will Learn in This Course

This course takes you from zero to PostgreSQL mastery:

1. **Foundations** — install, use psql, understand data types
2. **SQL Fundamentals** — SELECT, JOIN, GROUP BY, subqueries, set operations
3. **Intermediate SQL** — window functions, CTEs, indexes, transactions, constraints
4. **Advanced Topics** — performance tuning, EXPLAIN, partitioning, JSON, full-text search
5. **Administration** — users, roles, backup, recovery, replication, configuration
6. **Extensions** — PostGIS, pgvector, pg_stat_statements, pg_trgm
7. **Application Integration** — connect Python and Node.js apps
8. **Projects** — build real applications

## Next Steps

- [[01-Foundations/02-Installation-WSL2|Install PostgreSQL on WSL2]]
- [[01-Foundations/03-psql-Basics|Learn psql Basics]]
- [[00-Index/Learning-Path|View the full Learning Path]]

## External Resources

- [Official PostgreSQL Documentation](https://www.postgresql.org/docs/current/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com)
- [PostgreSQL Wikipedia](https://en.wikipedia.org/wiki/PostgreSQL)

---

> [!quote] "PostgreSQL is not just a database. It's a data platform." — Many developers, 2026
