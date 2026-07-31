---
tags: [postgresql, advanced, partitioning, large-tables]
---

# Partitioning

Partitioning splits large tables into smaller physical pieces while keeping them as one logical table.

## Range Partitioning (Time-Series)

```sql
CREATE TABLE measurements (
    id BIGSERIAL,
    logged_at TIMESTAMPTZ NOT NULL,
    sensor_id INT NOT NULL,
    value NUMERIC
) PARTITION BY RANGE (logged_at);

-- Monthly partitions
CREATE TABLE measurements_2026_01 PARTITION OF measurements
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE measurements_2026_02 PARTITION OF measurements
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Default partition (catch-all)
CREATE TABLE measurements_default PARTITION OF measurements DEFAULT;
```

## List Partitioning (Categorical)

```sql
CREATE TABLE customers (id INT, name TEXT, region TEXT)
PARTITION BY LIST (region);

CREATE TABLE customers_eu PARTITION OF customers FOR VALUES IN ('UK', 'FR', 'DE');
CREATE TABLE customers_na PARTITION OF customers FOR VALUES IN ('US', 'CA', 'MX');
CREATE TABLE customers_other PARTITION OF customers DEFAULT;
```

## Hash Partitioning (Even Distribution)

```sql
CREATE TABLE events (id BIGSERIAL, user_id INT, data JSONB)
PARTITION BY HASH (user_id);

CREATE TABLE events_p0 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE events_p1 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE events_p2 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE events_p3 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

## Partition Pruning

```sql
-- Only scans the relevant partition (Jan 2026)
SELECT * FROM measurements
WHERE logged_at >= '2026-01-15' AND logged_at < '2026-01-20';
```

## When to Partition

- Tables with tens of millions+ rows
- Time-series data where old partitions can be dropped
- When queries always filter on the partition key

## Maintenance

```sql
-- Detach a partition (becomes standalone table)
ALTER TABLE measurements DETACH PARTITION measurements_2025_01;

-- Drop old data instantly (vs slow DELETE)
DROP TABLE measurements_2025_01;

-- Create future partitions proactively
CREATE TABLE measurements_2026_03 PARTITION OF measurements
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
```

## Next

- [[04-Advanced-Topics/05-Full-Text-Search|Full-Text Search]]
- [[04-Advanced-Topics/06-JSON-JSONB|JSON/JSONB]]
