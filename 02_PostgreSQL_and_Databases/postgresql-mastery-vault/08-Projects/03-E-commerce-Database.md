---
tags: [project, advanced, ecommerce, transactions]
---

# Project 3: E-commerce Database

A full e-commerce schema with products, orders, inventory, and transactions.

## Schema

```sql
CREATE DATABASE ecommerce;
\c ecommerce

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES categories(id)
);

CREATE TABLE products (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    description TEXT,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    category_id INTEGER REFERENCES categories(id),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE customers (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE orders (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(id),
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','paid','shipped','delivered','cancelled')),
    total NUMERIC(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE order_items (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10,2) NOT NULL,  -- snapshot of price at order time
    line_total NUMERIC(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- Indexes
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_active ON products(is_active) WHERE is_active = true;
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
```

## Place an Order (Transaction)

```sql
-- Place an order in a transaction (atomic — all or nothing)
BEGIN;

    -- Create the order
    INSERT INTO orders (customer_id, status, total)
    VALUES (1, 'pending', 0)
    RETURNING id AS order_id \gset

    -- Add items
    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
    VALUES
        (:order_id, 1, 2, (SELECT price FROM products WHERE id = 1)),
        (:order_id, 2, 1, (SELECT price FROM products WHERE id = 2));

    -- Update order total
    UPDATE orders SET total = (
        SELECT SUM(line_total) FROM order_items WHERE order_id = :order_id
    ) WHERE id = :order_id;

    -- Decrement stock
    UPDATE products SET stock = stock - 2 WHERE id = 1;
    UPDATE products SET stock = stock - 1 WHERE id = 2;

COMMIT;
```

## Analytics Queries

```sql
-- Revenue by month
SELECT DATE_TRUNC('month', created_at) AS month,
       COUNT(*) AS orders, SUM(total) AS revenue
FROM orders WHERE status = 'paid'
GROUP BY month ORDER BY month;

-- Top products by sales
SELECT p.name, SUM(oi.quantity) AS units_sold, SUM(oi.line_total) AS revenue
FROM order_items oi
JOIN products p ON p.id = oi.product_id
JOIN orders o ON o.id = oi.order_id
WHERE o.status = 'paid'
GROUP BY p.name
ORDER BY revenue DESC LIMIT 10;

-- Customers who haven't ordered in 90 days
SELECT c.email, c.name, MAX(o.created_at) AS last_order
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id
HAVING MAX(o.created_at) < NOW() - INTERVAL '90 days' OR MAX(o.created_at) IS NULL;
```

## What You Learn

- Complex schema design
- Transaction safety (BEGIN/COMMIT/ROLLBACK)
- Generated columns
- Check constraints
- Partial indexes
- Snapshot pricing (unit_price in order_items)
- Stock management

## Next

- [[08-Projects/04-Analytics-Dashboard|Project 4: Analytics]]
- [[10-Interview-Prep/SQL-Interview-Questions|Interview Prep]]
