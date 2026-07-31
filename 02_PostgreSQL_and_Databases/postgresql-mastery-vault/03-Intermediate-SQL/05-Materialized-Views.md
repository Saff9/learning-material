---
tags: [sql, intermediate, materialized-views, cache]
---

# Materialized Views

Materialized views store the query result physically — like a cached table that can be refreshed.

## Creating Materialized Views

```sql
-- Create a materialized view
CREATE MATERIALIZED VIEW daily_sales AS
SELECT
    DATE(created_at) AS sale_date,
    COUNT(*) AS order_count,
    SUM(amount) AS total_revenue
FROM orders
GROUP BY DATE(created_at)
WITH DATA;  -- or WITH NO DATA to create empty

-- Query like a regular table
SELECT * FROM daily_sales ORDER BY sale_date DESC LIMIT 10;
```

## Refreshing

```sql
-- Refresh (locks the view during refresh)
REFRESH MATERIALIZED VIEW daily_sales;

-- Refresh concurrently (no lock, requires unique index)
CREATE UNIQUE INDEX idx_daily_sales_date ON daily_sales(sale_date);
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales;
```

> [!tip] Use CONCURRENTLY for production
> `REFRESH MATERIALIZED VIEW CONCURRENTLY` doesn't block reads during refresh. Requires a unique index. Use it for production materialized views.

## When to Use Materialized Views

- **Expensive aggregations** that don't need real-time data
- **Dashboards** refreshed hourly/daily
- **Pre-computed joins** for reporting

## vs Regular Views

| Feature | View | Materialized View |
|---------|------|-------------------|
| Storage | None (query only) | Physical storage |
| Freshness | Always current | Stale until refreshed |
| Performance | Same as underlying query | Fast (pre-computed) |
| Can index | No | Yes |

## Practice

```sql
-- Create a materialized view of top customers
CREATE MATERIALIZED VIEW top_customers AS
SELECT
    u.id, u.name,
    COUNT(o.id) AS order_count,
    SUM(o.amount) AS total_spent
FROM users u
JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name
ORDER BY total_spent DESC
LIMIT 100;

-- Index it for fast lookups
CREATE INDEX idx_top_customers_id ON top_customers(id);

-- Refresh daily
REFRESH MATERIALIZED VIEW CONCURRENTLY top_customers;
```

## Next

- [[03-Intermediate-SQL/06-Indexes|Indexes]]
- [[03-Intermediate-SQL/07-Transactions|Transactions]]
