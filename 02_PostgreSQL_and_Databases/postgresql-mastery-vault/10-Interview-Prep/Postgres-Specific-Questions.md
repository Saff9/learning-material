---
tags: [interview, postgresql, questions]
---

# PostgreSQL-Specific Interview Questions

**Q: What is MVCC?**
Multi-Version Concurrency Control. Readers never block writers, writers never block readers. Each transaction sees a snapshot. Old row versions are cleaned up by VACUUM.

**Q: What is VACUUM? Why is it needed?**
Because of MVCC, UPDATE/DELETE create dead tuples (old row versions). VACUUM reclaims this space. Without it, tables bloat and performance degrades.

**Q: Difference between json and jsonb?**
`json` stores as text (preserves formatting, slower). `jsonb` stores as binary (decomposed, indexable, faster). Always use `jsonb`.

**Q: What index types does PostgreSQL have?**
- B-tree (default): equality, range, sorting
- Hash: equality only
- GIN: arrays, JSONB, full-text
- GiST: spatial, ranges
- BRIN: huge ordered tables
- SP-GiST: non-balanced trees

**Q: What is the difference between SERIAL and IDENTITY?**
`SERIAL` creates an implicit sequence. `IDENTITY` (SQL standard, PG 10+) is cleaner, doesn't create orphan sequences. Prefer IDENTITY.

**Q: What is a CTE? When would you use it?**
Common Table Expression (WITH clause). Use for readability, reusability, or recursion. Recursive CTEs handle hierarchical data.

**Q: What are isolation levels?**
- READ COMMITTED (default): no dirty reads
- REPEATABLE READ: no non-repeatable reads, no phantoms
- SERIALIZABLE: full isolation via SSI

**Q: How does PostgreSQL handle concurrency?**
MVCC — each transaction sees a consistent snapshot. Writers create new row versions instead of overwriting. Readers see the snapshot from transaction start.

**Q: What is PgBouncer?**
A connection pooler that multiplexes many client connections onto fewer PostgreSQL backend processes. Transaction mode is recommended for web apps.

**Q: How do you optimize a slow query?**
1. Run `EXPLAIN (ANALYZE, BUFFERS)`
2. Check for Seq Scan where Index Scan expected → add index
3. Check estimated vs actual rows → run ANALYZE if off
4. Check for sort spilling to disk → increase work_mem
5. Rewrite query (avoid subqueries, use JOINs, avoid SELECT *)

**Q: What is a partial index?**
An index on a subset of rows (with a WHERE clause). Smaller, faster, automatically used when the query predicate implies the index predicate.

## Related

- [[10-Interview-Prep/SQL-Interview-Questions|SQL Interview Questions]]
- [[10-Interview-Prep/System-Design-with-Postgres|System Design]]
