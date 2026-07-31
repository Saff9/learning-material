# 15 - Partitioning

> Declarative partitioning strategies, partition pruning, and maintenance.

---

## Range Partitioning

```sql
-- Create partitioned table
CREATE TABLE measurements (
    city_id INT NOT NULL,
    logdate DATE NOT NULL,
    peaktemp INT,
    unitsales INT
) PARTITION BY RANGE (logdate);

-- Create partitions
CREATE TABLE measurements_y2026m01 PARTITION OF measurements
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE measurements_y2026m02 PARTITION OF measurements
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE measurements_y2026m03 PARTITION OF measurements
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Default partition
CREATE TABLE measurements_default PARTITION OF measurements DEFAULT;

-- Insert (auto-routed)
INSERT INTO measurements VALUES (1, '2026-01-15', 25, 100);
-- Goes to measurements_y2026m01

-- Query (partition pruning)
SELECT * FROM measurements WHERE logdate = '2026-01-15';
-- Only scans measurements_y2026m01!

EXPLAIN SELECT * FROM measurements WHERE logdate = '2026-01-15';
-- Should show: Partition Ref: FOR VALUES FROM ('2026-01-01') TO ('2026-02-01')
```

---

## List Partitioning

```sql
CREATE TABLE orders (
    order_id BIGINT,
    country_code CHAR(2),
    amount NUMERIC(10, 2)
) PARTITION BY LIST (country_code);

CREATE TABLE orders_us PARTITION OF orders FOR VALUES IN ('US');
CREATE TABLE orders_eu PARTITION OF orders FOR VALUES IN ('DE', 'FR', 'IT', 'ES');
CREATE TABLE orders_asia PARTITION OF orders FOR VALUES IN ('JP', 'CN', 'KR');
CREATE TABLE orders_other PARTITION OF orders DEFAULT;
```

---

## Hash Partitioning

```sql
CREATE TABLE events (
    event_id BIGINT,
    event_type VARCHAR(50),
    created_at TIMESTAMPTZ
) PARTITION BY HASH (event_id);

CREATE TABLE events_p0 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE events_p1 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE events_p2 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE events_p3 PARTITION OF events FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

---

## Subpartitioning

```sql
CREATE TABLE sales (
    sale_id BIGINT,
    sale_date DATE,
    region VARCHAR(10),
    amount NUMERIC(10,2)
) PARTITION BY RANGE (sale_date);

CREATE TABLE sales_q1_2026 PARTITION OF sales
    FOR VALUES FROM ('2026-01-01') TO ('2026-04-01')
    PARTITION BY LIST (region);

CREATE TABLE sales_q1_2026_north PARTITION OF sales_q1_2026 FOR VALUES IN ('NORTH');
CREATE TABLE sales_q1_2026_south PARTITION OF sales_q1_2026 FOR VALUES IN ('SOUTH');
```

---

## Partition Maintenance

```sql
-- Add new partition
CREATE TABLE measurements_y2026m04 PARTITION OF measurements
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');

-- Detach old partition
ALTER TABLE measurements DETACH PARTITION measurements_y2026m01;

-- Attach existing table
ALTER TABLE measurements ATTACH PARTITION measurements_y2026m05
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

-- Drop old partition
DROP TABLE measurements_y2026m01;

-- Check partitions
SELECT * FROM pg_partitions WHERE tablename = 'measurements';
```

---

## Partitioning Best Practices

1. **Choose partition key wisely** — must be in WHERE clauses for pruning
2. **Don't over-partition** — hundreds of partitions hurt planning time
3. **Index partitions individually** — or use template
4. **Monitor partition sizes** — detach/archive old data
5. **Use pg_partman** for automatic partition management

---
*Previous: 14 - Views | Next: 16 - Security & Authentication*
