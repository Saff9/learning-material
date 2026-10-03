---
tags: [dashboard, postgresql, course]
---

# PostgreSQL Mastery Vault

> [!info] The only PostgreSQL resource you need — A to Z, 2026 edition

## Quick Start

1. **New to PostgreSQL?** Start at [[01-Foundations/01-What-is-PostgreSQL|What is PostgreSQL]]
2. **Know basics, want SQL?** Jump to [[02-SQL-Fundamentals/01-SELECT-Basics|SELECT Basics]]
3. **Need a quick reference?** [[09-Cheat-Sheets/SQL-Cheat-Sheet|SQL Cheat Sheet]]
4. **Want to connect your app?** [[07-Application-Integration/01-Python-psycopg2|Python Integration]]

## Course Structure

| Section | Topic | Difficulty |
|---------|-------|------------|
| [[01-Foundations/\|01. Foundations]] | Installation, psql, data types | Beginner |
| [[02-SQL-Fundamentals/\|02. SQL Fundamentals]] | SELECT, JOINs, GROUP BY, subqueries | Beginner |
| [[03-Intermediate-SQL/\|03. Intermediate SQL]] | Window functions, CTEs, indexes, transactions | Intermediate |
| [[04-Advanced-Topics/\|04. Advanced Topics]] | Performance, EXPLAIN, partitioning, JSON | Advanced |
| [[05-Administration/\|05. Administration]] | Users, backup, replication, config | Advanced |
| [[06-Extensions/\|06. Extensions]] | PostGIS, pgvector, pg_stat_statements | Intermediate |
| [[07-Application-Integration/\|07. App Integration]] | Python, Node, Prisma, Supabase | Intermediate |
| [[08-Projects/\|08. Projects]] | 4 hands-on build projects | All levels |
| [[09-Cheat-Sheets/\|09. Cheat Sheets]] | Quick reference cards | Reference |
| [[10-Interview-Prep/\|10. Interview Prep]] | SQL and Postgres interview questions | All levels |
| [[11-Resources/\|11. Resources]] | Books, courses, communities | Reference |

## 2026 Highlights (PostgreSQL 18 and 19 Beta)

- **Async I/O** with io_uring (2-3x faster seq scans)
- **Native UUIDv7** (timestamp-ordered, sortable)
- **Virtual generated columns**
- **OAuth 2.0 authentication** (native JWT)
- **B-tree skip scans** (multicolumn optimization)
- **RETURNING OLD/NEW** (audit-style updates)
- **REPACK CONCURRENTLY** (PG19, online rebuilds)
- **Parallel autovacuum** (PG19)

## Completion Checklist

- [ ] Can install PostgreSQL and connect via psql
- [ ] Can write SELECT, JOIN, GROUP BY, subquery queries fluently
- [ ] Understand window functions (ROW_NUMBER, RANK, LAG, LEAD)
- [ ] Can write recursive CTEs for hierarchical data
- [ ] Know when to use B-tree vs GIN vs GiST vs BRIN indexes
- [ ] Can read EXPLAIN ANALYZE output and identify bottlenecks
- [ ] Understand ACID, isolation levels, and SERIALIZABLE
- [ ] Can set up PgBouncer for connection pooling
- [ ] Can connect Python and Node apps to PostgreSQL
- [ ] Have built at least 2 projects from [[08-Projects/]]
- [ ] Can answer common SQL interview questions

---

> [!quote] PostgreSQL is the world's most advanced open-source relational database. Master it once, use it for life.

**Last updated**: July 2026 | **Version**: PostgreSQL 18.4 (stable), 19 Beta 1
