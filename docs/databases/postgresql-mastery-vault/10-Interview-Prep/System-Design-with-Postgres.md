---
tags: [interview, system-design, postgresql]
---

# System Design with PostgreSQL

## When to Use PostgreSQL

- Relational data with complex relationships
- Financial/transactional data (ACID)
- Multi-tenant SaaS
- JSON-heavy apps (JSONB)
- Geospatial (PostGIS)
- Full-text search
- Analytics mixed with OLTP

## Scaling PostgreSQL

### Vertical Scaling (Bigger Machine)
- More RAM, CPU, faster SSDs
- Tune `shared_buffers`, `work_mem`, `max_connections`
- Cheapest first step

### Read Replicas
- Stream writes to primary, reads go to replicas
- Good for read-heavy workloads
- Eventual consistency on replicas

### Partitioning
- Split large tables by range, list, or hash
- Faster queries on partitions (pruning)
- Easy archival (drop old partitions)

### Sharding (Citus)
- Distribute data across multiple PostgreSQL nodes
- For write-heavy workloads beyond single machine
- Use Citus extension or application-level sharding

## Common Patterns

### Multi-Tenant SaaS
```sql
-- Row-Level Security per tenant
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orders
    FOR ALL USING (tenant_id = current_setting('app.tenant_id')::int);
```

### Audit Trail
```sql
-- Trigger to log all changes
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT, operation TEXT,
    old_data JSONB, new_data JSONB,
    changed_by TEXT DEFAULT current_user,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Pagination at Scale
```sql
-- Bad: OFFSET is O(n) for large offsets
SELECT * FROM items ORDER BY id LIMIT 10 OFFSET 100000;

-- Good: keyset pagination is O(log n)
SELECT * FROM items WHERE id > 100000 ORDER BY id LIMIT 10;
```

## Related

- [[10-Interview-Prep/SQL-Interview-Questions|SQL Questions]]
- [[04-Advanced-Topics/01-Performance-Tuning|Performance Tuning]]
