# 15 - Partitioning

> Comprehensive guide on Declarative Partitioning (range, list, hash), partition pruning, constraints, and maintenance.

Table Partitioning involves splitting a single large table into smaller, more manageable physical pieces called partitions. This drastically improves query performance via **Partition Pruning** and allows efficient data lifecycle management.

---

## 1. Range Partitioning (Time-Series / ID Ranges)

Perfect for time-series data, logs, and historical records.

```sql
-- Create partitioned master table
CREATE TABLE measurements (
    city_id INT NOT NULL,
    logdate DATE NOT NULL,
    peaktemp INT,
    unitsales INT
) PARTITION BY RANGE (logdate);

-- Create explicit partitions
-- Note: 'TO' boundary is EXCLUSIVE (e.g., up to but NOT including 2026-02-01)
CREATE TABLE measurements_y2026m01 PARTITION OF measurements
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE measurements_y2026m02 PARTITION OF measurements
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- The DEFAULT partition catches any data that doesn't fit in defined partitions.
-- WARNING: If you use a default partition, adding new specific partitions later requires an expensive exclusive lock!
CREATE TABLE measurements_default PARTITION OF measurements DEFAULT;

-- Insert (Auto-routed by PostgreSQL)
INSERT INTO measurements VALUES (1, '2026-01-15', 25, 100);
```

## 2. List Partitioning (Categorical Data)

Ideal for multi-tenant SaaS applications, regional data, or status codes.

```sql
CREATE TABLE orders (
    order_id BIGINT,
    country_code CHAR(2) NOT NULL,
    amount NUMERIC(10, 2)
) PARTITION BY LIST (country_code);

CREATE TABLE orders_us PARTITION OF orders FOR VALUES IN ('US');
CREATE TABLE orders_eu PARTITION OF orders FOR VALUES IN ('DE', 'FR', 'IT', 'ES');
CREATE TABLE orders_asia PARTITION OF orders FOR VALUES IN ('JP', 'CN', 'KR');
CREATE TABLE orders_other PARTITION OF orders DEFAULT;
```

## 3. Hash Partitioning (Load Balancing)

Used to evenly distribute data across a fixed number of partitions when there is no logical range or list key.

```sql
CREATE TABLE events (
    event_id UUID,
    event_type VARCHAR(50),
    created_at TIMESTAMPTZ
) PARTITION BY HASH (event_id);

-- You define the modulo (total partitions) and remainder (specific partition index)
CREATE TABLE events_p0 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE events_p1 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE events_p2 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE events_p3 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

---

## Subpartitioning (Multi-Level)

You can partition a partition. For example, partitioning by Range (Year) and then by List (Region).

```sql
CREATE TABLE sales (
    sale_id BIGINT,
    sale_date DATE,
    region VARCHAR(10),
    amount NUMERIC(10,2)
) PARTITION BY RANGE (sale_date);

-- The child partition is also defined as partitioned
CREATE TABLE sales_y2026 PARTITION OF sales
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01')
    PARTITION BY LIST (region);

-- Leaf partitions
CREATE TABLE sales_y2026_north PARTITION OF sales_y2026 FOR VALUES IN ('NORTH');
CREATE TABLE sales_y2026_south PARTITION OF sales_y2026 FOR VALUES IN ('SOUTH');
```

---

## Advanced Partitioning Concepts

### Partition Pruning
Pruning allows the query planner to skip scanning partitions that definitely do not contain matching data.

```sql
-- Make sure it's enabled (it is by default in modern PG)
SET enable_partition_pruning = on;

-- Query (Partition Pruning in Action)
EXPLAIN SELECT * FROM measurements WHERE logdate = '2026-01-15';
-- Will show only a sequential/index scan on `measurements_y2026m01`. It completely ignores all other tables.
```

### Unique Constraints & Primary Keys
**Critical Limitation:** Primary keys or unique constraints on partitioned tables **must include the partition key**.

```sql
-- This WILL FAIL:
-- CREATE TABLE users (id SERIAL PRIMARY KEY, tenant_id INT) PARTITION BY LIST (tenant_id);

-- This SUCCEEDS:
CREATE TABLE users (
    id SERIAL, 
    tenant_id INT,
    PRIMARY KEY (id, tenant_id)
) PARTITION BY LIST (tenant_id);
```

### Partitionwise Join & Aggregation
If two partitioned tables are joined on their partition keys, PostgreSQL can join the individual partitions directly to each other, drastically reducing memory usage.

```sql
SET enable_partitionwise_join = on;
SET enable_partitionwise_aggregate = on;
```

---

## Partition Maintenance & Lifecycle

Partitioning is often used for data lifecycle management (ILM). You can drop massive amounts of old data instantly by dropping a partition, bypassing expensive `DELETE` operations.

```sql
-- Detach old partition (Removes it from the partitioning tree but keeps the table and data)
ALTER TABLE measurements DETACH PARTITION measurements_y2026m01;

-- Detach Concurrently (PG 14+) - Does not block queries on the main table!
ALTER TABLE measurements DETACH PARTITION measurements_y2026m01 CONCURRENTLY;

-- Archive/Export the detached table using pg_dump
-- Then drop it to free up disk space instantly
DROP TABLE measurements_y2026m01;

-- Create and Attach a new partition
CREATE TABLE measurements_y2026m05 (LIKE measurements INCLUDING ALL);
ALTER TABLE measurements ATTACH PARTITION measurements_y2026m05
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');
```

### pg_partman
Managing partitions manually via cron/scripts is error-prone. The industry standard is to use the `pg_partman` extension to auto-create future partitions and optionally drop/archive old ones.

```sql
CREATE SCHEMA partman;
CREATE EXTENSION pg_partman SCHEMA partman;

-- Tell partman to manage our table, creating daily partitions
SELECT partman.create_parent(
    p_parent_table => 'public.measurements',
    p_control => 'logdate',
    p_type => 'native',
    p_interval=> '1 day',
    p_premake => 5 -- Keep 5 future partitions ready
);
```

---

## Partitioning Best Practices

1. **Choose the partition key wisely** — The key MUST be heavily utilized in your `WHERE` clauses, otherwise pruning fails and queries scan *all* partitions (Catastrophic performance).
2. **Don't over-partition** — PostgreSQL has to lock and plan across all partitions. Having thousands of partitions severely impacts query planning time. Aim for 10s to 100s.
3. **Index at the parent level** — Indexes created on the parent automatically cascade down to all current and future partitions.
4. **Use Default partitions carefully** — They make adding new specific partitions lock-heavy and slow because PG has to scan the entire default partition to ensure no data violates the new partition's boundaries.
5. **Updates moving rows across partitions** — If an `UPDATE` changes the partition key such that the row belongs in a new partition, PG will execute a `DELETE` + `INSERT` under the hood. Avoid this if possible.

---
*Previous: 14 - Views | Next: 16 - Security & Authentication*
