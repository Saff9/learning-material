---
tags: [interview, sql, questions]
---

# SQL Interview Questions

## Easy

**Q: Write a query to find the second highest salary.**
```sql
SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);
-- Or with LIMIT
SELECT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1;
```

**Q: Find employees who earn more than their department average.**
```sql
SELECT e.name, e.salary, e.department
FROM employees e
WHERE e.salary > (SELECT AVG(e2.salary) FROM employees e2 WHERE e2.department = e.department);
```

**Q: Count employees per department.**
```sql
SELECT department, COUNT(*) FROM employees GROUP BY department;
```

## Medium

**Q: Find duplicate emails.**
```sql
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;
```

**Q: Rank employees by salary within each department.**
```sql
SELECT name, department, salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank
FROM employees;
```

**Q: Find the top 3 highest-paid employees per department.**
```sql
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
    FROM employees
) t WHERE rn <= 3;
```

**Q: Write a query to delete duplicate rows, keeping one.**
```sql
DELETE FROM users WHERE id NOT IN (
    SELECT MIN(id) FROM users GROUP BY email
);
```

## Hard

**Q: Calculate running total of sales.**
```sql
SELECT date, amount,
    SUM(amount) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM sales;
```

**Q: Find consecutive days of login (streak).**
```sql
WITH dates AS (
    SELECT DISTINCT user_id, login_date::DATE
    FROM logins
),
grouped AS (
    SELECT user_id, login_date,
        login_date - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date))::INTEGER AS grp
    FROM dates
)
SELECT user_id, MIN(login_date) AS start_date, MAX(login_date) AS end_date,
       MAX(login_date) - MIN(login_date) + 1 AS streak
FROM grouped GROUP BY user_id, grp
ORDER BY streak DESC;
```

**Q: Department with highest average salary (handle ties).**
```sql
WITH dept_avg AS (
    SELECT department, AVG(salary) AS avg_sal,
        RANK() OVER (ORDER BY AVG(salary) DESC) AS rnk
    FROM employees GROUP BY department
)
SELECT department, avg_sal FROM dept_avg WHERE rnk = 1;
```

## Concepts

**Q: What is the N+1 problem?**
Loading N related records issues 1 query for parents + N queries for children. Fix with JOINs or eager loading (`SELECT ... JOIN` or ORM's `include`/`selectinload`).

**Q: What is normalization?**
- 1NF: atomic values, no repeating groups
- 2NF: 1NF + no partial dependency on composite key
- 3NF: 2NF + no transitive dependency

**Q: What is ACID?**
- Atomicity: all-or-nothing transactions
- Consistency: constraints enforced
- Isolation: concurrent transactions don't interfere
- Durability: committed data survives crashes (WAL)

## Related

- [[10-Interview-Prep/Postgres-Specific-Questions|Postgres-Specific Questions]]
- [[10-Interview-Prep/System-Design-with-Postgres|System Design]]
