---
tags: [project, beginner, crud, study-log]
---

# Project 1: Study Log App

A simple CRUD app to log your study sessions. Tests basic SQL, CRUD, and simple analytics.

## Schema

```sql
CREATE DATABASE studylog;
\c studylog

CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#6366f1'
);

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    minutes INTEGER NOT NULL CHECK (minutes > 0),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO subjects (name) VALUES
    ('PostgreSQL'), ('Python'), ('Algorithms'), ('System Design');

INSERT INTO sessions (subject_id, minutes, notes) VALUES
    (1, 60, 'Learned about indexes'),
    (1, 45, 'Practiced JOINs'),
    (2, 90, 'Built a Flask app'),
    (3, 30, 'Sorting algorithms'),
    (1, 75, 'EXPLAIN ANALYZE practice');
```

## Queries to Build

```sql
-- Total study time per subject
SELECT s.name, SUM(se.minutes) AS total_minutes
FROM subjects s
LEFT JOIN sessions se ON se.subject_id = s.id
GROUP BY s.name
ORDER BY total_minutes DESC NULLS LAST;

-- Study sessions in the last 7 days
SELECT subject_id, date, minutes, notes
FROM sessions
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date DESC;

-- Daily study totals
SELECT date, SUM(minutes) AS total
FROM sessions
GROUP BY date
ORDER BY date DESC;

-- Average session length per subject
SELECT s.name, ROUND(AVG(se.minutes), 1) AS avg_minutes
FROM subjects s
JOIN sessions se ON se.subject_id = s.id
GROUP BY s.name;

-- Streak: consecutive days with at least one session
WITH dated AS (
    SELECT DISTINCT date FROM sessions ORDER BY date
),
grouped AS (
    SELECT date, date - (ROW_NUMBER() OVER (ORDER BY date))::INTEGER AS grp
    FROM dated
)
SELECT MIN(date) AS start_date, MAX(date) AS end_date,
       MAX(date) - MIN(date) + 1 AS streak_length
FROM grouped GROUP BY grp ORDER BY streak_length DESC LIMIT 1;
```

## What You Learn

- Basic CRUD (INSERT, SELECT, UPDATE, DELETE)
- JOINs
- Aggregates (SUM, AVG, COUNT)
- GROUP BY
- Date arithmetic
- Window functions (for the streak query)
- Foreign keys and CASCADE

## Next

- [[08-Projects/02-Blog-Platform|Project 2: Blog Platform]]
- [[09-Cheat-Sheets/SQL-Cheat-Sheet|SQL Cheat Sheet]]
