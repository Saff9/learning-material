---
tags: [sql, fundamentals, set-operations, union]
---

# Set Operations

Set operations combine the results of two or more queries.

## UNION

```sql
-- Combine results, remove duplicates
SELECT city FROM customers
UNION
SELECT city FROM suppliers;

-- UNION ALL: keep duplicates (faster — no deduplication)
SELECT city FROM customers
UNION ALL
SELECT city FROM suppliers;
```

> [!tip] Use UNION ALL when possible
> `UNION` removes duplicates by sorting and comparing — this is expensive. If you know there are no duplicates (or don't care), use `UNION ALL` — it's much faster.

## INTERSECT

```sql
-- Cities that appear in BOTH tables
SELECT city FROM customers
INTERSECT
SELECT city FROM suppliers;
```

## EXCEPT

```sql
-- Cities in customers but NOT in suppliers
SELECT city FROM customers
EXCEPT
SELECT city FROM suppliers;
```

## Rules

- All queries must return the **same number of columns**
- Column types must be **compatible** (PostgreSQL will cast where possible)
- Result column names come from the **first query**
- Use `ORDER BY` only at the end (applies to the entire result)

```sql
-- With ORDER BY at the end
SELECT name, 'customer' AS type FROM customers
UNION ALL
SELECT name, 'supplier' AS type FROM suppliers
ORDER BY name;
```

## Practical Examples

```sql
-- Find products that have never been ordered
SELECT id, name FROM products
EXCEPT
SELECT product_id, product_name FROM order_items;

-- All people in the system (customers + employees + suppliers)
SELECT name, email, 'customer' AS role FROM customers
UNION ALL
SELECT name, email, 'employee' AS role FROM employees
UNION ALL
SELECT name, email, 'supplier' AS role FROM suppliers
ORDER BY name;
```

## Practice

```sql
-- Combine employee names from different departments
SELECT name FROM employees WHERE department = 'Engineering'
UNION
SELECT name FROM employees WHERE department = 'Sales';

-- This is equivalent to:
SELECT DISTINCT name FROM employees
WHERE department IN ('Engineering', 'Sales');
```

## Next

- [[03-Intermediate-SQL/01-Window-Functions|Window Functions]]
- [[09-Cheat-Sheets/SQL-Cheat-Sheet|SQL Cheat Sheet]]
