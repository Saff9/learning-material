# 03 - Databases (DBMS)

> **Phase:** 2 (Core Engineering) · **Time:** ~4–6 weeks · **Difficulty:** ⭐⭐

## What it is
A **Database Management System (DBMS)** is software that stores, organizes, retrieves, and protects data. Two families:
- **Relational / SQL** — data in tables (rows & columns). Examples: PostgreSQL, MySQL, SQLite, SQL Server.
- **NoSQL** — documents, key-value, column, or graph. Examples: MongoDB, Redis, Cassandra.

## Why it matters
- Nearly every real application has a database (accounts, posts, orders, logs).
- Picking the wrong model or writing slow queries causes outages and angry users.
- A top interview area for backend roles.

## Relational model — detailed
- **Table** = entity (e.g., `users`). **Row** = one record. **Column** = one attribute.
- **Primary key** — unique id per row.
- **Foreign key** — reference to a row in another table (relationships).
- **Relationships:** one-to-one, one-to-many, many-to-many (via a join table).

## SQL essentials
```sql
SELECT name, email FROM users WHERE age > 18 ORDER BY name;
SELECT u.name, COUNT(o.id) FROM users u
  JOIN orders o ON o.user_id = u.id
  GROUP BY u.name HAVING COUNT(o.id) > 3;
```
- `SELECT / WHERE / ORDER BY / LIMIT`
- `JOIN` (INNER, LEFT, RIGHT) — combine tables
- `GROUP BY` + aggregate (`COUNT`, `SUM`, `AVG`)
- `INSERT / UPDATE / DELETE`
- **Indexes** speed up lookups (but slow writes).

## Normalization
Reducing data duplication and inconsistency:
- **1NF:** atomic values, no repeating groups.
- **2NF:** no partial dependency on the key.
- **3NF:** no transitive dependency.
> Goal: store each fact once. Trade-off: too much normalization = slow JOINs; denormalize for read speed when needed.

## Transactions & ACID
A **transaction** groups operations so they all succeed or all fail:
- **A**tomicity — all-or-nothing
- **C**onsistency — valid state always
- **I**solation — concurrent txns don't interfere
- **D**urability — committed data survives crashes

## NoSQL basics
- **Document (MongoDB):** JSON-like, flexible schema.
- **Key-Value (Redis):** ultra-fast cache.
- **When NoSQL?** Huge scale, flexible schema, or simple key access. SQL still wins for relational, consistent data.

## Free resources
- **CMU Database Group (free YouTube lectures)**: https://www.youtube.com/@CMUDatabaseGroup
  - Intro to Databases playlist: https://www.youtube.com/playlist?list=PLSE8ODhjZXjaKScG3l0nuOiDTTqpfnWFf
- **PostgreSQL official tutorial**: https://www.postgresql.org/docs/current/tutorial.html
- **freeCodeCamp — SQL full course**: https://www.youtube.com/watch?v=HXV3zeQKqGY
- **Your vault notes** (great local references):
  - [[postgresql-mastery-vault]]
  - [[postgreSQL-Masterclass-A-Z]]
  - [[postgresql_tutorial]]

## Practice projects
1. **Blog schema** — `users`, `posts`, `comments` with foreign keys; JOIN queries.
2. **E-commerce** — products, orders, order_items; aggregate sales reports.
3. **Build a CRUD app** — Python/Node + PostgreSQL (create/read/update/delete).
4. **Index experiment** — time a query before/after adding an index.

## Self-check (can you…)
- [ ] Write JOINs across 3 tables
- [ ] Explain normalization trade-offs
- [ ] Use transactions correctly
- [ ] Choose SQL vs NoSQL for a use case

## Progress
- [ ] Write basic + joined SQL queries
- [ ] Understand normalization and indexes
- [ ] Used transactions
- [ ] Built a database-backed app

## Next
→ [[04 - Operating Systems]]
