---
tags: [sql, intermediate, window-functions, analytics]
---

# Window Functions

Window functions perform calculations across rows **related to the current row** without collapsing them (unlike GROUP BY). They are essential for analytics.

## Syntax

```sql
function() OVER (
    [PARTITION BY column]
    [ORDER BY column]
    [ROWS BETWEEN ... AND ...]
)
```

## Ranking Functions

```sql
-- Row number, rank, and dense rank within each department
SELECT
    name, department, salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS row_num,
    RANK()       OVER (PARTITION BY department ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank
FROM employees;
```

| salary | ROW_NUMBER | RANK | DENSE_RANK |
|--------|-----------|------|------------|
| 100000 | 1 | 1 | 1 |
| 100000 | 2 | 1 | 1 |
| 90000  | 3 | 3 | 2 |
| 80000  | 4 | 4 | 3 |

- `ROW_NUMBER()` — unique sequential number, no ties
- `RANK()` — ties get same rank, next rank skips (1, 1, 3)
- `DENSE_RANK()` — ties get same rank, no gaps (1, 1, 2)

## LAG and LEAD — Compare to Previous/Next Row

```sql
-- Day-over-day stock price change
SELECT
    symbol, trade_date, close_price,
    LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY trade_date) AS prev_close,
    close_price - LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY trade_date) AS daily_change,
    LEAD(close_price, 1) OVER (PARTITION BY symbol ORDER BY trade_date) AS next_close
FROM stock_prices;
```

## Running Totals and Moving Averages

```sql
-- Running total and 3-row moving average
SELECT
    trade_date, close_price,
    SUM(close_price) OVER (ORDER BY trade_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
    AVG(close_price) OVER (ORDER BY trade_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS ma_3
FROM stock_prices
WHERE symbol = 'AAPL';
```

## FIRST_VALUE, LAST_VALUE, NTH_VALUE

```sql
SELECT
    name, department, salary,
    FIRST_VALUE(salary) OVER w AS dept_min,
    LAST_VALUE(salary) OVER w AS dept_max
FROM employees
WINDOW w AS (
    PARTITION BY department ORDER BY salary
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
);
```

> [!warning] LAST_VALUE pitfall
> The default window frame is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, so `LAST_VALUE` returns the *current* row's value, not the partition's last. Always specify `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` for the true last value.

## NTILE — Divide into Buckets

```sql
-- Split customers into 4 revenue quartiles
SELECT
    customer_name, revenue,
    NTILE(4) OVER (ORDER BY revenue DESC) AS quartile
FROM customers;
```

## Top N Per Group

```sql
-- Top 2 highest-paid employees per department
SELECT * FROM (
    SELECT
        name, department, salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
    FROM employees
) ranked
WHERE rn <= 2;
```

## Practice

```sql
-- Rank employees by salary
SELECT name, salary,
    RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;

-- Running total of salaries by hire date
SELECT name, hire_date, salary,
    SUM(salary) OVER (ORDER BY hire_date) AS cumulative_payroll
FROM employees;
```

## Next

- [[03-Intermediate-SQL/02-CTEs|CTEs]]
- [[03-Intermediate-SQL/06-Indexes|Indexes]]
