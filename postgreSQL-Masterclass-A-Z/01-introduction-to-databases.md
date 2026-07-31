# 01 - Introduction to Databases & PostgreSQL

> **Version Context**: This guide covers PostgreSQL 14 through 18 (released September 2025), with emphasis on production-ready features as of 2026.

---

## What is a Database?

A **database** is an organized collection of structured data stored electronically, designed for efficient storage, retrieval, and manipulation. A **Database Management System (DBMS)** is the software layer that manages databases, handles queries, enforces integrity, and controls concurrent access.

### Database Evolution Timeline

| Era | Technology | Characteristics |
|-----|-----------|-----------------|
| 1960s | Hierarchical/Network (IMS, CODASYL) | Tree/graph structures, rigid schemas |
| 1970s | Relational (System R, Ingres) | Tables, SQL, set theory foundation |
| 1990s | Object-Relational (PostgreSQL, Oracle) | Complex types, inheritance, extensibility |
| 2000s | NoSQL (MongoDB, Cassandra) | Schema flexibility, horizontal scaling |
| 2010s | NewSQL (CockroachDB, Spanner) | Distributed SQL, ACID at scale |
| 2020s | Multi-model + AI-native (PostgreSQL + pgvector) | Relational + vector + JSON + time-series in one engine |

### The Relational Model

Proposed by Edgar F. Codd (IBM, 1970), the relational model organizes data into **relations** (tables) consisting of **tuples** (rows) and **attributes** (columns). Key principles:

1. **Data Independence**: Logical and physical storage are separate
2. **Set-oriented Operations**: Operations work on entire sets, not individual records
3. **Declarative Queries**: You specify *what* you want, not *how* to get it
4. **Mathematical Foundation**: Based on relational algebra and calculus

```
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

- **#1 most wanted database** in Stack Overflow Developer Survey 2025
- Used by: Apple, Instagram, Spotify, Netflix, Uber, Reddit, NASA, FDA
- Default choice for: AI/LLM applications (via pgvector), geospatial (PostGIS), financial systems

### Core Strengths

| Capability | Description | Competitive Advantage |
|-----------|-------------|----------------------|
| **ACID Compliance** | Full atomicity, consistency, isolation, durability | Unlike MySQL (before 8.0) or MongoDB, ACID is default, not optional |
| **MVCC** | Multi-Version Concurrency Control | Readers never block writers; no read locks needed |
| **Extensibility** | Custom types, operators, indexes, languages, extensions | No other RDBMS matches this flexibility |
| **SQL Standard** | Follows ISO/IEC 9075 more closely than competitors | Window functions, CTEs, LATERAL, JSON_TABLE all standard-compliant |
| **Data Types** | 40+ built-in types + unlimited custom types | Arrays, JSONB, ranges, geometric, network, UUID, composite |
| **NoSQL Inside** | JSONB with GIN indexes, document patterns | Eliminates need for separate document database for many use cases |
| **Full-Text Search** | Built-in tsvector/tsquery with ranking | No external search engine needed for basic-to-moderate search |
| **Geospatial** | PostGIS extension = industry standard GIS | Best-in-class spatial indexing and operations |
| **AI/Vector** | pgvector extension + pgvectorscale | Native vector search competitive with Pinecone at <10M scale |

### PostgreSQL vs. Alternatives (2026)

| Feature | PostgreSQL | MySQL 8.4 | SQL Server 2025 | MongoDB 8 | SQLite |
|---------|-----------|-----------|-----------------|-----------|--------|
| License | PostgreSQL (permissive) | GPL/Commercial | Commercial | SSPL | Public Domain |
| SQL Standard | Excellent | Moderate | Good | N/A (NoSQL) | Good (subset) |
| Window Functions | Full | Partial | Full | N/A | Partial |
| CTEs (Recursive) | Full | Partial | Full | N/A | Partial |
| JSON/Document | JSONB (binary, indexed) | JSON (text) | JSON | Native BSON | JSON (text) |
| Arrays | Native | No | No | Native (BSON) | No |
| Ranges | Native | No | No | No | No |
| Full-Text Search | Built-in | Basic (InnoDB) | Built-in | Text indexes | FTS5 |
| GIS/Spatial | PostGIS (best) | Limited | Spatial | 2dsphere | No |
| Vector Search | pgvector (excellent) | No | No | Atlas Vector | No |
| Partitioning | Declarative (range/list/hash) | Range/list/hash | Full | Shard key | No |
| Replication | Streaming + Logical | Binary + GTID | AlwaysOn | Replica sets | WAL |
| Extensibility | Unlimited | Limited | CLR only | Limited | Loadable extensions |

---

## PostgreSQL Architecture Deep Dive

### Process Model (Multi-Process, Not Multi-Threaded)

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                              │
│  psql  pgAdmin  DBeaver  App (libpq)  JDBC/ODBC/.NET       │
└────────────────────────┬────────────────────────────────────┘
                         │ TCP/IP or Unix Socket
┌────────────────────────▼────────────────────────────────────┐
│                  POSTMASTER PROCESS                          │
│  • Listens on port 5432                                      │
│  • Forks backend for each connection                         │
│  • Manages shared memory initialization                      │
│  • Handles startup, shutdown, crash recovery                 │
└────────────────────────┬────────────────────────────────────┘
                         │ forks
┌────────────────────────▼────────────────────────────────────┐
│              BACKEND PROCESSES (1 per connection)            │
│  • Parses, plans, and executes queries                       │
│  • Has private memory (work_mem, temp buffers)               │
│  • Communicates results to client                            │
│  • Terminates when client disconnects                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│           BACKGROUND WORKER PROCESSES                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Background   │  │ WAL Writer   │  │ AutoVacuum       │  │
│  │ Writer       │  │              │  │ Launcher/Workers │  │
│  │ (bgwriter)   │  │ (walwriter)  │  │                  │  │
│  │ Writes dirty │  │ Writes WAL   │  │ Reclaims dead    │  │
│  │ buffers      │  │ buffers to   │  │ tuples, updates  │  │
│  │ periodically │  │ disk         │  │ statistics       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Checkpointer │  │ Stats Collector│  │ Logger           │  │
│  │              │  │              │  │                  │  │
│  │ Ensures      │  │ Tracks table │  │ Writes to        │  │
│  │ consistency, │  │ and index    │  │ log_destination  │  │
│  │ writes ckpt  │  │ usage stats  │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Archiver     │  │ Logical      │  │ Parallel Workers │  │
│  │ (WAL archive)│  │ Replication  │  │ (query parallel) │  │
│  │              │  │ (pgoutput)   │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SHARED MEMORY                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Shared Buffer Cache (shared_buffers)                │   │
│  │ • Caches table and index pages (8KB each)           │   │
│  │ • Default 128MB, production: 25% of RAM             │   │
│  │ • Uses clock sweep algorithm for eviction           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ WAL Buffers (wal_buffers)                           │   │
│  │ • Buffers WAL records before writing to disk        │   │
│  │ • Default 16MB                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Commit Log (CLOG)                                   │   │
│  │ • Transaction status (in-progress, committed,       │   │
│  │   aborted) for concurrency control                  │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Lock Manager                                        │   │
│  │ • Table-level, row-level, advisory locks            │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Other: Subtrans, MultiXact, Predicate Lock, etc.    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              PER-BACKEND PRIVATE MEMORY                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ work_mem (default 4MB)                              │   │
│  │ • Sort operations, hash joins, materialization      │   │
│  │ • Can be set per-query or per-role                  │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ maintenance_work_mem (default 64MB)                 │   │
│  │ • VACUUM, CREATE INDEX, ALTER TABLE, etc.           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ temp_buffers (default 8MB)                          │   │
│  │ • Temporary table data                              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Storage Layout

```
Data Directory ($PGDATA)
├── base/                    # Database files (one subdir per database OID)
│   ├── 1/                   # Template1 database
│   ├── 13806/               # Your database
│   │   ├── 16384            # Table file (OID = relfilenode)
│   │   ├── 16384_fsm        # Free Space Map
│   │   ├── 16384_vm         # Visibility Map
│   │   └── 16385            # Index file
├── global/                  # Cluster-wide tables (pg_database, pg_authid)
├── pg_wal/                  # Write-Ahead Log files (16MB segments)
├── pg_commit_ts/            # Commit timestamps
├── pg_logical/              # Logical replication data
├── pg_stat/                 # Statistics files
├── pg_stat_tmp/             # Temporary statistics
├── pg_subtrans/             # Subtransaction data
├── pg_tblspc/               # Tablespace symlinks
├── pg_twophase/             # Prepared transaction files
├── pg_dynshmem/             # Dynamic shared memory
├── pg_notify/               # LISTEN/NOTIFY queue
├── pg_replslot/             # Replication slots
├── pg_serial/               # Serializable transaction info
├── pg_snapshots/            # Exported snapshots
├── postgresql.conf          # Main configuration
├── pg_hba.conf              # Client authentication
├── pg_ident.conf            # User name mapping
└── PG_VERSION               # Version file
```

### The Page Structure (8KB)

Every table and index is stored as a sequence of 8KB pages (blocks):

```
┌─────────────────────────────────────────────────────────────┐
│                     PAGE HEADER (24 bytes)                   │
│  ┌─────────────┬─────────────┬───────────────────────────┐  │
│  │ pd_lsn      │ pd_checksum │ pd_flags                  │  │
│  │ (WAL ptr)   │ (CRC)       │ (hint bits, etc.)         │  │
│  ├─────────────┼─────────────┼───────────────────────────┤  │
│  │ pd_lower    │ pd_upper    │ pd_special                │  │
│  │ (free start)│ (free end)  │ (special area start)      │  │
│  ├─────────────┴─────────────┴───────────────────────────┤  │
│  │ pd_pagesize_version                                      │  │
│  └─────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│              ITEM ID ARRAY (line pointers)                   │
│  ┌────────┬────────┬────────┬────────┐                      │
│  │ lp_off │ lp_len │ lp_flags│       │  → Points to tuple   │
│  │ (offset)│ (length)│ (status)│      │                      │
│  └────────┴────────┴────────┴────────┘                      │
├─────────────────────────────────────────────────────────────┤
│                     FREE SPACE                               │
├─────────────────────────────────────────────────────────────┤
│                   TUPLE DATA (grows upward)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ t_xmin │ t_xmax │ t_cid │ t_infomask │ t_bits │ data │   │
│  │ (insert│ (delete│ (cmd  │ (status    │ (null  │ (payload)
│  │  xact) │  xact) │  id)  │  flags)    │  bits) │      │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│              SPECIAL SPACE (index data, etc.)                │
└─────────────────────────────────────────────────────────────┘
```

---

## ACID Properties in PostgreSQL

### Atomicity

All operations in a transaction succeed or none do. Implemented via:
- **WAL (Write-Ahead Logging)**: Changes written to WAL before data files
- **Rollback**: Uses WAL to undo incomplete transactions on crash

### Consistency

Database transitions between valid states. Enforced by:
- Constraints (NOT NULL, UNIQUE, CHECK, FK)
- Triggers
- Rules
- PostgreSQL never allows constraint violations to persist

### Isolation

Concurrent transactions don't interfere. PostgreSQL uses **MVCC** (Multi-Version Concurrency Control):

```
Transaction Timeline:
T1: BEGIN → UPDATE row A → COMMIT
T2: BEGIN → SELECT row A (sees old version) → SELECT row A (still old) → COMMIT

MVCC ensures T2 sees a consistent snapshot from its start time,
regardless of what T1 does.
```

Key MVCC columns in every tuple:
- `xmin`: Transaction ID that inserted this row
- `xmax`: Transaction ID that deleted/updated this row (0 = live)
- `cmin`/`cmax`: Command ID within transaction
- `ctid`: Physical location (block, offset)

### Durability

Committed transactions survive crashes. Guaranteed by:
- **WAL fsync**: WAL written to disk before commit acknowledged
- **Full Page Writes**: After crash, can reconstruct torn pages
- **Replication**: Synchronous replicas confirm write

---

## PostgreSQL Version History & 2026 State

| Version | Release | Key Features |
|---------|---------|-------------|
| 9.6 | 2016 | Parallel query, phrase search |
| 10 | 2017 | Declarative partitioning, logical replication |
| 11 | 2018 | JIT compilation, parallel CREATE INDEX |
| 12 | 2019 | Generated columns, pluggable storage |
| 13 | 2020 | Incremental sorting, parallel vacuum |
| 14 | 2021 | Multirange types, pipeline mode |
| 15 | 2022 | MERGE command, improved sort performance |
| 16 | 2023 | SQL/JSON constructors, pg_stat_io, parallel aggregate |
| 17 | Sep 2024 | JSON_TABLE, failover slots, incremental base backup, B-tree dedup |
| **18** | **Sep 2025** | **AIO (async I/O), OAuth 2.0, UUIDv7, virtual generated columns, skip-scan** |

### PostgreSQL 18 Highlights (2026 Production)

1. **Asynchronous I/O (AIO)**: io_uring on Linux, worker threads elsewhere. Up to 3x faster sequential scans on NVMe/cloud storage.
2. **Native OAuth 2.0**: SASL OAUTHBEARER mechanism. Bearer token auth against IdP (Okta, Azure AD, Auth0).
3. **UUIDv7**: Time-ordered UUIDs. First 48 bits = Unix timestamp. Sequential inserts like BIGINT, global uniqueness like UUID.
4. **Virtual Generated Columns**: Computed at query time, no storage overhead. Add instantly to billion-row tables.
5. **Skip-Scan B-tree**: Multi-column index on (a,b) can now efficiently satisfy queries filtering only on b.

---

## When to Choose PostgreSQL

### Ideal Use Cases

| Use Case | Why PostgreSQL |
|----------|---------------|
| **OLTP Applications** | ACID, constraints, rich types, excellent concurrency |
| **Complex Analytics** | Window functions, CTEs, LATERAL, parallel query |
| **Geospatial/Mapping** | PostGIS is the gold standard |
| **Full-Text Search** | Built-in, no external dependency for moderate scale |
| **JSON/Document Hybrid** | JSONB with GIN indexes; query documents with SQL |
| **AI/LLM/RAG** | pgvector for embeddings, hybrid search with relational filters |
| **Time-Series Data** | TimescaleDB extension, partitioning, BRIN indexes |
| **Financial Systems** | Strict ACID, audit trails, point-in-time recovery |
| **Multi-tenant SaaS** | Row-level security, schemas per tenant, connection pooling |

### When to Consider Alternatives

| Scenario | Alternative | Reason |
|----------|------------|--------|
| Simple key-value caching | Redis | Sub-millisecond latency, data structures |
| 100M+ vectors, pure vector workload | Pinecone/Weaviate | Specialized ANN optimization |
| Globally distributed, always-on | CockroachDB/Spanner | Built-in geo-partitioning |
| Extreme write throughput (IoT) | TimescaleDB/Cassandra | Specialized time-series ingestion |
| Mobile offline-first | SQLite | Embedded, zero-config |
| Graph relationships (social networks) | Neo4j | Native graph traversals |

---

## Summary

PostgreSQL is a mature, feature-rich, extensible relational database that serves as both an OLTP engine and an analytical platform. Its 2026 feature set — including AIO, OAuth, UUIDv7, and advanced vector search — makes it the most versatile open-source database available. Understanding its process architecture, memory model, and MVCC foundation is essential before diving into SQL and administration.

---
*Next: 02 - Installation, Configuration & First Steps*
