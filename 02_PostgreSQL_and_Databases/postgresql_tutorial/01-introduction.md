# 01 - Introduction to Databases & PostgreSQL

## What is a Database?

A **database** is an organized collection of structured data stored electronically in a computer system. Databases are controlled by a **Database Management System (DBMS)** — software that interacts with end-users, applications, and the database itself to capture and analyze data.

### Types of Databases

| Type | Description | Examples |
|------|-------------|----------|
| **Relational (RDBMS)** | Data stored in tables with rows and columns; uses SQL | PostgreSQL, MySQL, Oracle, SQL Server |
| **NoSQL** | Flexible schemas; document, key-value, wide-column, graph | MongoDB, Redis, Cassandra, Neo4j |
| **NewSQL** | Combines ACID guarantees with horizontal scalability | CockroachDB, Google Spanner |
| **Time-Series** | Optimized for time-stamped data | TimescaleDB, InfluxDB |
| **Vector** | Optimized for similarity search on embeddings | pgvector, Pinecone |

## Why PostgreSQL?

PostgreSQL (often called "Postgres") is a powerful, open-source, object-relational database system with over 35 years of active development. It is the **most advanced open-source relational database** in existence.

### Key Strengths

- **ACID Compliance**: Full support for Atomicity, Consistency, Isolation, and Durability.
- **Extensibility**: Custom data types, operators, index methods, functions, and languages.
- **Standards Compliance**: Follows SQL standards more closely than most databases.
- **Rich Data Types**: Arrays, JSON/JSONB, UUID, geometric types, ranges, custom enums.
- **Concurrency**: Multi-Version Concurrency Control (MVCC) allows high throughput without read locks.
- **Full-Text Search**: Built-in powerful text search capabilities.
- **Geospatial**: PostGIS extension makes it the gold standard for GIS data.
- **NoSQL Capabilities**: JSONB allows document-store-like behavior within a relational engine.

### PostgreSQL vs. MySQL

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| SQL Standard Compliance | Excellent | Moderate |
| Advanced Data Types | Extensive | Limited |
| Concurrency Model | MVCC (no read locks) | MVCC (InnoDB) |
| Extensibility | Highly extensible | Limited |
| JSON Support | JSONB (binary, indexable) | JSON (text-based) |
| Window Functions | Full support | Partial |
| Common Table Expressions (CTEs) | Full support | Limited (until 8.0) |
| Full-Text Search | Built-in | Basic (InnoDB limited) |
| GIS/Geospatial | PostGIS (industry standard) | Limited |

## Architecture Overview

```
┌─────────────────────────────────────────┐
│           Client Applications           │
│    (psql, pgAdmin, app drivers, etc.)  │
└─────────────────┬───────────────────────┘
                  │ libpq / network
┌─────────────────▼───────────────────────┐
│         PostgreSQL Server               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │ Postmaster│  │ Backend  │  │ Backend  │ │
│  │ (listener)│  │ Process │  │ Process  │ │
│  └────┬────┘  └────┬────┘  └────┬────┘ │
│       └─────────────┴─────────────┘      │
│  ┌─────────────────────────────────────┐ │
│  │         Shared Memory               │ │
│  │  (buffer cache, WAL buffers, locks) │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │  WAL    │  │  Data   │  │  Index  │ │
│  │  Files  │  │  Files  │  │  Files  │ │
│  └─────────┘  └─────────┘  └─────────┘ │
└─────────────────────────────────────────┘
```

### Key Processes

- **Postmaster**: The main process that listens for incoming connections and forks backend processes.
- **Backend Process**: One per client connection. Handles query parsing, planning, execution.
- **Background Writer**: Writes dirty buffers from shared memory to disk.
- **WAL Writer**: Writes WAL (Write-Ahead Log) records to disk.
- **AutoVacuum**: Cleans up dead tuples and updates table statistics.
- **Checkpointer**: Ensures data consistency by flushing buffers and writing checkpoint records.

## The ACID Properties

Understanding ACID is fundamental to relational databases:

### Atomicity
A transaction is all-or-nothing. If any part fails, the entire transaction is rolled back.

### Consistency
A transaction brings the database from one valid state to another. All constraints, triggers, and rules are enforced.

### Isolation
Concurrent transactions do not interfere with each other. PostgreSQL uses MVCC to provide isolation without excessive locking.

### Durability
Once a transaction is committed, it survives permanently, even in case of power loss or crash. WAL ensures this.

## When to Choose PostgreSQL

- **Complex queries** with joins, CTEs, window functions
- **Data integrity** is critical (financial, healthcare, legal)
- **Geospatial data** (mapping, location services)
- **JSON/document hybrid** workloads
- **Full-text search** requirements
- **High concurrency** read/write workloads
- **Extensibility** needs (custom types, extensions)

## Summary

PostgreSQL is not just a database — it is a data platform. Its combination of reliability, feature richness, extensibility, and standards compliance makes it suitable for everything from small applications to planet-scale systems.

---
*Next: [02 - Installation & Setup](02-installation-setup.md)*
