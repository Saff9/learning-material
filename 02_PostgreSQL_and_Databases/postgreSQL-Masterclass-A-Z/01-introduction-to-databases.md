# 01 - Introduction to Databases & PostgreSQL

> **Version Context**: This guide covers PostgreSQL 14 through 18 (released September 2025), with emphasis on production-ready features as of 2026.

---

## What is a Database?

A **database** is an organized collection of structured data stored electronically, designed for efficient storage, retrieval, and manipulation. A **Database Management System (DBMS)** is the software layer that manages databases, handles queries, enforces integrity, and controls concurrent access.

### Database Evolution Timeline

| Era | Technology | Characteristics |
|-----|-----------|-----------------|
| 1960s | Hierarchical/Network (IMS, CODASYL) | Tree/graph structures, rigid schemas. Difficult to query dynamically. |
| 1970s | Relational (System R, Ingres) | Tables, SQL, set theory foundation. Strong data consistency. |
| 1990s | Object-Relational (PostgreSQL, Oracle) | Complex types, inheritance, extensibility. Bridged OO code and data. |
| 2000s | NoSQL (MongoDB, Cassandra) | Schema flexibility, horizontal scaling, CAP theorem trade-offs. |
| 2010s | NewSQL (CockroachDB, Spanner) | Distributed SQL, ACID at global scale, consensus algorithms (Raft/Paxos). |
| 2020s | Multi-model + AI-native (PostgreSQL + pgvector) | Relational + vector embeddings + JSON + time-series in one converged engine. |

### The Relational Model & Normalization

Proposed by Edgar F. Codd (IBM, 1970), the relational model organizes data into **relations** (tables) consisting of **tuples** (rows) and **attributes** (columns). 

**Key principles:**
1. **Data Independence**: Logical and physical storage are separate.
2. **Set-oriented Operations**: Operations work on entire sets, not individual records.
3. **Declarative Queries**: You specify *what* you want, not *how* to get it.
4. **Mathematical Foundation**: Based on relational algebra and calculus.

**Normalization** is the process of structuring a database to reduce data redundancy and improve data integrity:
- **1NF**: Atomic values, no repeating groups.
- **2NF**: 1NF + no partial dependencies (all non-key attributes depend on the whole primary key).
- **3NF**: 2NF + no transitive dependencies (non-key attributes depend *only* on the primary key).
- **BCNF / 4NF / 5NF**: Advanced forms dealing with multi-valued dependencies and overlapping candidate keys.

```text
Relational Algebra Operations:
┌─────────────┬────────────────────────────────────────┐
│ σ (sigma)   │ Selection (WHERE) - filter rows        │
│ π (pi)      │ Projection (SELECT) - choose columns   │
│ ⋈           │ Join - combine relations               │
│ ∪           │ Union - combine sets                   │
│ −           │ Difference - subtract sets             │
│ ×           │ Cartesian Product - all combinations   │
│ ρ (rho)     │ Rename - alias relations               │
└─────────────┴────────────────────────────────────────┘
```

---

## Why PostgreSQL?

PostgreSQL began at UC Berkeley in 1986 as POSTGRES ("Post-Ingres"), led by Michael Stonebraker. It became open-source in 1996 and is now the **world's most advanced open-source relational database**.

### 2026 PostgreSQL Market Position

- **#1 most wanted database** in Stack Overflow Developer Survey 2025.
- Used by: Apple, Instagram, Spotify, Netflix, Uber, Reddit, NASA, FDA.
- Default choice for: AI/LLM applications (via pgvector), geospatial (PostGIS), financial systems, and modern SaaS backends.

### Core Strengths

| Capability | Description | Competitive Advantage |
|-----------|-------------|----------------------|
| **ACID Compliance** | Full atomicity, consistency, isolation, durability | Unlike older MySQL or MongoDB, ACID is the non-negotiable default. |
| **MVCC** | Multi-Version Concurrency Control | Readers never block writers; no read locks needed. Excellent high-concurrency throughput. |
| **Extensibility** | Custom types, operators, indexes, languages, extensions | Unmatched flexibility. Add Python, Rust (plrust), or JS logic inside the DB. |
| **SQL Standard** | Follows ISO/IEC 9075 strictly | Window functions, CTEs, LATERAL joins, JSON_TABLE, standard-compliant implementations. |
| **Data Types** | 40+ built-in types + custom | Arrays, JSONB, ranges, geometric, network (CIDR, INET), UUID, composite. |
| **NoSQL Inside** | JSONB with GIN indexes | Fast document queries without sacrificing relational joins. |
| **Full-Text Search** | Built-in tsvector/tsquery | Built-in language stemming and ranking, replacing Elasticsearch for many. |
| **Geospatial** | PostGIS extension | Industry standard GIS, processing complex spatial polygons. |
| **AI/Vector** | pgvector + pgvectorscale | HNSW and IVFFlat index types for ultra-fast ANN search on embeddings. |

---

## PostgreSQL Architecture Deep Dive

### Process Model (Multi-Process, Not Multi-Threaded)

Unlike SQL Server or MySQL, PostgreSQL forks a new OS process for each connection. This guarantees memory isolation but means connections are heavy.

```text
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                              │
│  psql  pgAdmin  DBeaver  App (libpq)  JDBC/ODBC/.NET       │
└────────────────────────┬────────────────────────────────────┘
                         │ TCP/IP or Unix Socket
┌────────────────────────▼────────────────────────────────────┐
│                  CONNECTION POOLER (Optional but standard)   │
│  PgBouncer / Pgpool-II (Multiplexes 10,000 clients into      │
│  100 actual PostgreSQL backend connections)                  │
└────────────────────────┬────────────────────────────────────┘
                         │ Multiplexed connections
┌────────────────────────▼────────────────────────────────────┐
│                  POSTMASTER PROCESS (PID 1 of PG)            │
│  • Listens on port 5432                                      │
│  • Forks backend for each connection                         │
│  • Manages shared memory initialization                      │
│  • Handles startup, shutdown, crash recovery                 │
└────────────────────────┬────────────────────────────────────┘
                         │ forks
┌────────────────────────▼────────────────────────────────────┐
│              BACKEND PROCESSES (1 per actual connection)     │
│  • Parses, plans, and executes queries                       │
│  • Has private memory (work_mem, temp buffers)               │
│  • Uses CPU for sorts, hashes, aggregations                  │
└─────────────────────────────────────────────────────────────┘
```

**Best Practice: Connection Pooling**
Because PostgreSQL forks a heavy process per connection (taking ~10MB RAM each), having 5,000 idle connections will crash your server. **Always use PgBouncer** (or a proxy like Supabase Supavisor) in production to pool connections. PgBouncer maps thousands of lightweight client connections to a small pool of heavy Postgres processes.

### Memory Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    SHARED MEMORY (IPC)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Shared Buffer Cache (shared_buffers)                │   │
│  │ • Caches table and index pages (8KB each)           │   │
│  │ • Default 128MB, production: 25%-40% of total RAM   │   │
│  │ • Uses clock sweep algorithm for eviction           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ WAL Buffers (wal_buffers)                           │   │
│  │ • Buffers WAL records before fsync to disk          │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Commit Log (CLOG) / Lock Manager                    │   │
│  │ • Transaction statuses and concurrency locks        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              PER-BACKEND PRIVATE MEMORY                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ work_mem (default 4MB, tune to ~16MB-64MB)          │   │
│  │ • Sort operations, hash joins, materialization      │   │
│  │ • NOTE: Multiplied by concurrent nodes in a query!  │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ maintenance_work_mem (default 64MB, tune to 1GB+)   │   │
│  │ • VACUUM, CREATE INDEX, ALTER TABLE, etc.           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Storage Layout and TOAST

```text
Data Directory ($PGDATA)
├── base/                    # DB files (dirs named by DB OID)
│   ├── 13806/               # Your database
│   │   ├── 16384            # Table file (8KB chunks)
│   │   ├── 16384_fsm        # Free Space Map (where to insert)
│   │   └── 16384_vm         # Visibility Map (used by Vacuum/Index-only scans)
├── global/                  # Cluster-wide metadata
├── pg_wal/                  # Write-Ahead Log segments (16MB files)
```

**TOAST (The Oversized-Attribute Storage Technique)**
PostgreSQL pages are 8KB. A single row cannot span multiple pages. If you insert a 10MB JSON document, PostgreSQL automatically compresses and splits it into smaller chunks, storing them in a hidden "TOAST" table, leaving only a pointer in the main table. This keeps sequential scans on the main table extremely fast!

---

## Transaction Isolation & MVCC in Depth

### Transaction Isolation Levels

SQL Standard defines isolation levels. PostgreSQL implements them via MVCC:

1. **Read Uncommitted**: Postgres treats this exactly like Read Committed. Dirty reads are strictly impossible.
2. **Read Committed (Default)**: A query sees data committed before the *query* began.
   - *Issue*: Non-repeatable reads (running the same SELECT twice in a transaction might yield different results if someone else committed an UPDATE in between).
3. **Repeatable Read**: A query sees data committed before the *transaction* began.
   - *Issue*: Serialization anomalies.
4. **Serializable**: Strictest. Simulates transactions executing serially. Will throw serialization errors requiring app retries.

### MVCC (Multi-Version Concurrency Control)

PostgreSQL doesn't overwrite data on UPDATE. It marks the old row as "dead" and inserts a completely new row.

Key hidden columns in every tuple:
- `xmin`: Transaction ID that inserted this row.
- `xmax`: Transaction ID that deleted/updated this row (0 if still live).

**The VACUUM Process**
Because UPDATEs create new rows, old "dead tuples" accumulate (table bloat). The **AutoVacuum** background worker wakes up periodically to scan for dead tuples and marks their space as reusable in the Free Space Map. Proper AutoVacuum tuning is the #1 skill for a DBA.

---

## Advanced Architecture Concepts

### 1. Partitioning (Handling Terabytes of Data)

Partitioning splits a massive logical table into smaller physical pieces.
- **Range Partitioning**: E.g., partitioned by month (sales_jan, sales_feb). Ideal for time-series, allowing rapid dropping of old partitions (`DROP TABLE sales_2020`).
- **List Partitioning**: E.g., partitioned by region (US, EU, ASIA).
- **Hash Partitioning**: Distribute evenly based on a hash key.

### 2. High Availability (HA) & Replication

- **Physical Streaming Replication**: Byte-for-byte exact copy of the WAL stream. Used for hot standby servers (read replicas).
- **Logical Replication**: Replicates data on a per-table/row basis via pub/sub. Allows replicating from Postgres 14 to Postgres 16, or from Postgres to Kafka.
- **Patroni**: The industry standard HA template (using etcd/ZooKeeper) to automatically promote a replica to primary if the primary dies.

### 3. Vector Search (pgvector) in AI Era

In 2026, `pgvector` makes PostgreSQL a tier-1 vector database.
- Stores high-dimensional arrays (embeddings) generated by LLMs.
- Queries semantic similarity using operators like `<->` (L2 distance), `<#>` (Inner product), and `<=>` (Cosine distance).
- **Indexes**: Supports **IVFFlat** (approximate, requires building after data load) and **HNSW** (Hierarchical Navigable Small World, handles dynamic updates and offers superior recall/speed).

### 4. Security Hardening & RBAC

- **Role-Based Access Control (RBAC)**: Create granular roles (`readonly_role`, `app_user`).
- **Row-Level Security (RLS)**: Define policies on tables so users only see their own rows. `CREATE POLICY user_policy ON secrets USING (user_id = current_user);`.
- **pg_hba.conf**: The gatekeeper file. Explicitly maps IPs, users, and authentication methods (SCRAM-SHA-256, OAuth).

### 5. Cloud Deployment Topologies

- **Self-Hosted / Kubernetes**: Maximum control. Use CloudNativePG operator.
- **Managed RDS / Cloud SQL**: Standard managed instances.
- **Aurora (AWS) / AlloyDB (GCP)**: Compute separated from storage. The engine writes WAL directly to distributed cloud storage. Massive write throughput and instant read replicas.

---

## PostgreSQL Version History & 2026 State

| Version | Release | Key Features |
|---------|---------|-------------|
| 14 | 2021 | Multirange types, pipeline mode |
| 15 | 2022 | MERGE command, improved sort performance |
| 16 | 2023 | SQL/JSON constructors, pg_stat_io, parallel aggregate |
| 17 | Sep 2024 | JSON_TABLE, failover slots, incremental base backup, B-tree dedup |
| **18** | **Sep 2025** | **AIO (async I/O), OAuth 2.0, UUIDv7, virtual generated columns, skip-scan B-tree** |

### PostgreSQL 18 Highlights (2026 Production)

1. **Asynchronous I/O (AIO)**: Uses `io_uring` on Linux. Drastically reduces syscall overhead. Up to 3x faster sequential scans on NVMe/cloud storage.
2. **Native OAuth 2.0**: SASL OAUTHBEARER mechanism. Token auth against IdP (Okta, Azure AD).
3. **UUIDv7**: Time-ordered UUIDs. First 48 bits = Unix timestamp. Prevents B-tree index bloat common with random UUIDv4.
4. **Virtual Generated Columns**: Computed at query time, zero storage footprint.
5. **Skip-Scan B-tree**: Index on `(a,b)` efficiently answers queries filtering only on `b`.

---

## When to Choose PostgreSQL

### Ideal Use Cases

| Use Case | Why PostgreSQL |
|----------|---------------|
| **Core OLTP Apps** | ACID, constraints, rich types, excellent concurrency. |
| **AI/LLM/RAG Apps** | pgvector for embeddings combined directly with relational metadata filters. |
| **SaaS & Multi-tenant**| RLS (Row Level Security), separate schemas per tenant, excellent pooling. |
| **Geospatial** | PostGIS is the gold standard for mapping and routing. |
| **Time-Series** | TimescaleDB extension provides automatic partitioning and continuous aggregates. |

### When to Consider Alternatives

| Scenario | Alternative | Reason |
|----------|------------|--------|
| Extreme read/write at edge | SQLite / LibSQL | Embedded, zero-config, runs in mobile devices or Edge workers. |
| Sub-millisecond K/V cache | Redis | In-memory data structures, absolute lowest latency. |
| True multi-master global scale| CockroachDB / Spanner | Built from ground-up for geo-partitioned consensus. |
| 1B+ vector similarity | Pinecone / Milvus | Specialized ANN clustering at extreme scale. |

---

## Summary

PostgreSQL is a mature, feature-rich, extensible database that has successfully absorbed the best concepts of NoSQL, GIS, and Vector engines into a singular, reliable relational core. Its 2026 feature set—including AIO, OAuth, UUIDv7, and deep AI integration—solidifies its position as the default backend for modern applications.

Understanding its multi-process architecture, MVCC isolation model, Vacuum mechanics, and storage fundamentals (like TOAST and shared buffers) is essential for anyone aiming to administer, optimize, or develop against PostgreSQL at scale.

---
*Next: 02 - Installation, Configuration & First Steps*
