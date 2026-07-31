# 05 - Constraints & Data Integrity

> Every constraint type, custom types, domains, and advanced integrity patterns.

---

## Constraint Types

### NOT NULL
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,        -- Must have value
    phone VARCHAR(20)                   -- Can be NULL
);

ALTER TABLE users ALTER COLUMN email SET NOT NULL;
ALTER TABLE users ALTER COLUMN phone DROP NOT NULL;
```

### UNIQUE
```sql
-- Single column
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);

-- Multi-column
CREATE TABLE enrollments (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    semester VARCHAR(20) NOT NULL,
    UNIQUE (student_id, course_id, semester)
);

-- Named constraint
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    CONSTRAINT uq_users_email UNIQUE (email)
);

-- Partial unique index (more flexible than constraint)
CREATE UNIQUE INDEX idx_active_email ON users(email) WHERE is_active = TRUE;
```

### PRIMARY KEY
```sql
-- Single column
CREATE TABLE products (
    sku VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100)
);

-- Composite
CREATE TABLE order_items (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id)
);

-- Named
CREATE TABLE customers (
    id BIGSERIAL NOT NULL,
    name VARCHAR(100),
    CONSTRAINT pk_customers PRIMARY KEY (id)
);
```

### FOREIGN KEY
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    -- or with explicit constraint:
    CONSTRAINT fk_orders_customer 
        FOREIGN KEY (customer_id) REFERENCES customers(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- Self-referencing
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE
);
```

### CHECK
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price NUMERIC(10, 2) CHECK (price > 0),
    discount_price NUMERIC(10, 2),
    stock INTEGER CHECK (stock >= 0),

    CONSTRAINT chk_valid_discount 
        CHECK (discount_price IS NULL OR discount_price < price),
    CONSTRAINT chk_name_not_empty 
        CHECK (LENGTH(TRIM(name)) > 0)
);

-- Add check to existing table (fast with NOT VALID)
ALTER TABLE employees 
ADD CONSTRAINT chk_salary_positive CHECK (salary > 0) NOT VALID;
ALTER TABLE employees VALIDATE CONSTRAINT chk_salary_positive;
```

### DEFAULT
```sql
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT FALSE
);

-- Expression default
CREATE TABLE events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    due_date DATE DEFAULT CURRENT_DATE + INTERVAL '7 days'
);

-- PostgreSQL 18: Virtual generated columns (computed, not stored)
-- CREATE TABLE products (
--     price NUMERIC(10,2),
--     tax_rate NUMERIC(5,4) DEFAULT 0.08,
--     total_price NUMERIC(10,2) GENERATED ALWAYS AS (price * (1 + tax_rate)) VIRTUAL
-- );
```

### EXCLUSION
```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE room_reservations (
    room_id INTEGER NOT NULL,
    during TSTZRANGE NOT NULL,
    EXCLUDE USING gist (room_id WITH =, during WITH &&)
);

-- No overlapping reservations for same room
INSERT INTO room_reservations VALUES (1, '[2026-07-15 10:00, 2026-07-15 12:00)');
INSERT INTO room_reservations VALUES (1, '[2026-07-15 11:00, 2026-07-15 13:00)'); -- ERROR!
```

---

## Custom Types

### Domains
```sql
CREATE DOMAIN email AS VARCHAR(255)
    CHECK (VALUE ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

CREATE DOMAIN positive_int AS INTEGER CHECK (VALUE > 0);
CREATE DOMAIN percentage AS NUMERIC(5,2) CHECK (VALUE BETWEEN 0 AND 100);
CREATE DOMAIN url AS TEXT CHECK (VALUE ~ '^https?://');

CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    email email NOT NULL,
    age positive_int,
    completion percentage DEFAULT 0,
    website url
);
```

### Composite Types
```sql
CREATE TYPE address AS (
    street TEXT,
    city TEXT,
    postal_code VARCHAR(20),
    country VARCHAR(2)
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    billing_address address,
    shipping_address address
);

SELECT (billing_address).city FROM customers;
```

### Enumerations
```sql
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    status order_status DEFAULT 'pending'
);

-- Add value (PG 16+)
ALTER TYPE order_status ADD VALUE 'refunded' AFTER 'delivered';
```

---

## Advanced Patterns

### Soft Deletes
```sql
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    deleted_at TIMESTAMPTZ,
    CHECK (deleted_at IS NULL OR deleted_at > created_at)
);

-- View showing only active
CREATE VIEW active_documents AS
SELECT * FROM documents WHERE deleted_at IS NULL;

-- Unique constraint that ignores soft-deleted
CREATE UNIQUE INDEX idx_unique_title ON documents(title) WHERE deleted_at IS NULL;
```

### Temporal Tables (System-Versioned)
```sql
-- PostgreSQL doesn't have native temporal tables, but you can build them:
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    price NUMERIC(10,2),
    valid_from TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMPTZ DEFAULT 'infinity'
);

-- Current view
CREATE VIEW current_products AS
SELECT * FROM products WHERE valid_to = 'infinity';

-- History query
SELECT * FROM products 
WHERE id = 1 AND valid_from <= '2026-01-01' AND valid_to > '2026-01-01';
```

---
*Previous: 04 - Joins | Next: 06 - Indexes & Performance*
