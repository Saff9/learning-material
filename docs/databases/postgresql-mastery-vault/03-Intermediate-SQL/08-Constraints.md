---
tags: [sql, intermediate, constraints, integrity]
---

# Constraints

Constraints enforce data integrity at the database level. They are non-negotiable for production schemas.

## Types of Constraints

| Constraint | Purpose |
|-----------|---------|
| `NOT NULL` | Column cannot be NULL |
| `UNIQUE` | No duplicate values |
| `PRIMARY KEY` | NOT NULL + UNIQUE (identifies a row) |
| `FOREIGN KEY` | References another table's PK/UNIQUE |
| `CHECK` | Custom boolean condition |
| `EXCLUDE` | No two rows satisfy a predicate (e.g., no overlapping ranges) |

## Examples

```sql
CREATE TABLE products (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    category TEXT CHECK (category IN ('electronics', 'clothing', 'food', 'other')),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE orders (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'paid', 'shipped', 'delivered', 'cancelled')),
    total NUMERIC(10,2) NOT NULL CHECK (total >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## Foreign Key Actions

```sql
-- ON DELETE behavior when parent row is deleted
FOREIGN KEY (customer_id) REFERENCES customers(id)
    ON DELETE CASCADE        -- delete child rows automatically
    ON UPDATE CASCADE        -- update FK if parent PK changes

-- Other options:
-- ON DELETE SET NULL       -- set FK to NULL
-- ON DELETE SET DEFAULT    -- set FK to default value
-- ON DELETE RESTRICT       -- error immediately (no deferred check)
-- ON DELETE NO ACTION      -- error (default, but deferrable)
```

## EXCLUDE Constraint (PostgreSQL Superpower)

```sql
-- Prevent double-booking: no two reservations for the same room can overlap
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    room_id INT NOT NULL REFERENCES rooms(id),
    guest_name TEXT NOT NULL,
    during TSTZRANGE NOT NULL,

    EXCLUDE USING gist (room_id WITH =, during WITH &&)
    -- This means: no two rows where room_id is equal AND during overlaps
);

-- This insert works
INSERT INTO reservations (room_id, guest_name, during)
VALUES (1, 'Alice', '[2026-07-15 10:00+05:30, 2026-07-15 12:00+05:30)');

-- This insert FAILS (overlapping)
INSERT INTO reservations (room_id, guest_name, during)
VALUES (1, 'Bob', '[2026-07-15 11:00+05:30, 2026-07-15 13:00+05:30)');
```

## Adding Constraints to Existing Tables

```sql
-- Add a constraint
ALTER TABLE products ADD CONSTRAINT positive_price CHECK (price >= 0);

-- Add a unique constraint
ALTER TABLE users ADD CONSTRAINT unique_phone UNIQUE (phone);

-- Drop a constraint
ALTER TABLE products DROP CONSTRAINT positive_price;
```

## Best Practices

> [!important] Constraint principles
> 1. Every table should have a PRIMARY KEY
> 2. Use FOREIGN KEYs for all relationships — don't skip them
> 3. Use CHECK constraints for domain integrity (positive prices, valid statuses)
> 4. Use NOT NULL liberally — NULLs complicate queries
> 5. Index foreign key columns (PostgreSQL doesn't auto-create these)
> 6. Use EXCLUDE for scheduling/overlapping-range constraints

## Practice

```sql
-- Try inserting invalid data — constraints should prevent it
INSERT INTO products (name, sku, price) VALUES ('Test', 'TEST-001', -10);
-- Should fail: CHECK constraint (price >= 0)

INSERT INTO products (name, sku) VALUES ('Test2', NULL);
-- Should fail: NOT NULL constraint

INSERT INTO orders (customer_id) VALUES (99999);
-- Should fail: FOREIGN KEY constraint (no customer 99999)
```

## Next

- [[04-Advanced-Topics/01-Performance-Tuning|Performance Tuning]]
- [[04-Advanced-Topics/03-EXPLAIN-ANALYZE|EXPLAIN ANALYZE]]
