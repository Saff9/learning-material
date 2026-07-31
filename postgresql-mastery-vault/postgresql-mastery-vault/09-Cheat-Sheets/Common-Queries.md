---
tags: [cheat-sheet, queries, reference]
---

# Common Queries

## Finding Duplicates

```sql
SELECT email, COUNT(*) FROM users
GROUP BY email HAVING COUNT(*) > 1;
```

## Remove Duplicates (Keep First)

```sql
DELETE FROM users WHERE id NOT IN (
    SELECT MIN(id) FROM users GROUP BY email
);
```

## Top N Per Group

```sql
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
    FROM employees
) t WHERE rn <= 3;
```

## Running Total

```sql
SELECT date, amount,
    SUM(amount) OVER (ORDER BY date) AS running_total
FROM sales;
```

## Year-over-Year Growth

```sql
SELECT year, revenue,
    LAG(revenue, 1) OVER (ORDER BY year) AS prev_year,
    ROUND((revenue - LAG(revenue,1) OVER (ORDER BY year)) * 100.0 /
          NULLIF(LAG(revenue,1) OVER (ORDER BY year), 0), 2) AS yoy_growth_pct
FROM yearly_revenue;
```

## Find Missing Records

```sql
-- Products that have never been ordered
SELECT p.* FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.id
WHERE oi.id IS NULL;

-- Or with EXCEPT
SELECT id FROM products
EXCEPT
SELECT product_id FROM order_items;
```

## Generate Date Series

```sql
SELECT generate_series(
    DATE '2026-01-01',
    DATE '2026-12-31',
    INTERVAL '1 day'
)::DATE AS date;
```

## Pivot Table

```sql
SELECT user_id,
    SUM(amount) FILTER (WHERE month = 1) AS jan,
    SUM(amount) FILTER (WHERE month = 2) AS feb,
    SUM(amount) FILTER (WHERE month = 3) AS mar
FROM monthly_orders
GROUP BY user_id;
```

## Related

- [[09-Cheat-Sheets/SQL-Cheat-Sheet|SQL Cheat Sheet]]
- [[03-Intermediate-SQL/01-Window-Functions|Window Functions]]
