---
tags: [project, advanced, analytics, window-functions, ctes]
---

# Project 4: Analytics Dashboard

A database designed for analytics — tests window functions, CTEs, materialized views, and performance.

## Schema

```sql
CREATE DATABASE analytics;
\c analytics

CREATE TABLE events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL,
    event_type TEXT NOT NULL,  -- 'page_view', 'click', 'signup', 'purchase'
    page_url TEXT,
    amount NUMERIC(10,2),  -- for purchase events
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Monthly partitions
CREATE TABLE events_2026_01 PARTITION OF events FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE events_2026_02 PARTITION OF events FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE TABLE events_2026_03 PARTITION OF events FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
CREATE TABLE events_2026_04 PARTITION OF events FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');
CREATE TABLE events_2026_05 PARTITION OF events FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');
CREATE TABLE events_2026_06 PARTITION OF events FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
CREATE TABLE events_2026_07 PARTITION OF events FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
CREATE TABLE events_default PARTITION OF events DEFAULT;

-- Index
CREATE INDEX idx_events_user_time ON events(user_id, created_at DESC);

-- Generate sample data
INSERT INTO events (user_id, event_type, page_url, amount, created_at)
SELECT
    (random() * 1000)::BIGINT + 1,
    (ARRAY['page_view','click','signup','purchase'])[1 + (random() * 3)::INT],
    'page' || ((random() * 10)::INT + 1),
    CASE WHEN random() > 0.7 THEN (random() * 100)::NUMERIC(10,2) ELSE NULL END,
    NOW() - (random() * INTERVAL '180 days')
FROM generate_series(1, 100000);
```

## Analytics Queries

```sql
-- Daily active users (DAU)
SELECT DATE(created_at) AS day, COUNT(DISTINCT user_id) AS dau
FROM events
GROUP BY day ORDER BY day DESC LIMIT 30;

-- Monthly active users (MAU)
SELECT DATE_TRUNC('month', created_at) AS month, COUNT(DISTINCT user_id) AS mau
FROM events
GROUP BY month ORDER BY month DESC;

-- Revenue by month
SELECT DATE_TRUNC('month', created_at) AS month,
       COUNT(*) FILTER (WHERE event_type = 'purchase') AS purchases,
       SUM(amount) FILTER (WHERE event_type = 'purchase') AS revenue
FROM events
GROUP BY month ORDER BY month;

-- User retention cohort (users who signed up in month X and returned in month X+1, X+2...)
WITH signups AS (
    SELECT user_id, DATE_TRUNC('month', MIN(created_at)) AS signup_month
    FROM events WHERE event_type = 'signup'
    GROUP BY user_id
),
activity AS (
    SELECT DISTINCT user_id, DATE_TRUNC('month', created_at) AS active_month
    FROM events
)
SELECT
    s.signup_month,
    COUNT(DISTINCT s.user_id) AS cohort_size,
    COUNT(DISTINCT a.user_id) FILTER (WHERE a.active_month = s.signup_month + INTERVAL '1 month') AS month_1,
    COUNT(DISTINCT a.user_id) FILTER (WHERE a.active_month = s.signup_month + INTERVAL '2 months') AS month_2,
    COUNT(DISTINCT a.user_id) FILTER (WHERE a.active_month = s.signup_month + INTERVAL '3 months') AS month_3
FROM signups s
LEFT JOIN activity a ON a.user_id = s.user_id
GROUP BY s.signup_month
ORDER BY s.signup_month;

-- Top 10 pages by views
SELECT page_url, COUNT(*) AS views
FROM events WHERE event_type = 'page_view'
GROUP BY page_url ORDER BY views DESC LIMIT 10;

-- Conversion funnel
WITH funnel AS (
    SELECT
        user_id,
        BOOL_OR(event_type = 'page_view') AS viewed,
        BOOL_OR(event_type = 'signup') AS signed_up,
        BOOL_OR(event_type = 'purchase') AS purchased
    FROM events
    GROUP BY user_id
)
SELECT
    COUNT(*) FILTER (WHERE viewed) AS page_views,
    COUNT(*) FILTER (WHERE signed_up) AS signups,
    COUNT(*) FILTER (WHERE purchased) AS purchases,
    ROUND(COUNT(*) FILTER (WHERE signed_up) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE viewed), 0), 2) AS view_to_signup_pct,
    ROUND(COUNT(*) FILTER (WHERE purchased) * 100.0 / NULLIF(COUNT(*) FILTER (WHERE signed_up), 0), 2) AS signup_to_purchase_pct
FROM funnel;
```

## Materialized View for Dashboard

```sql
CREATE MATERIALIZED VIEW daily_metrics AS
SELECT
    DATE(created_at) AS day,
    COUNT(*) AS total_events,
    COUNT(DISTINCT user_id) AS unique_users,
    COUNT(*) FILTER (WHERE event_type = 'purchase') AS purchases,
    SUM(amount) FILTER (WHERE event_type = 'purchase') AS revenue
FROM events
GROUP BY day
WITH DATA;

CREATE UNIQUE INDEX idx_daily_metrics_day ON daily_metrics(day);

-- Refresh daily
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_metrics;

-- Query the dashboard
SELECT * FROM daily_metrics ORDER BY day DESC LIMIT 30;
```

## What You Learn

- Table partitioning
- Window functions (for cohorts)
- CTEs (for multi-step analytics)
- Materialized views
-- FILTER clause for conditional aggregates
- Funnel analysis
- Retention cohorts
- EXPLAIN ANALYZE for performance

## Next

- [[09-Cheat-Sheets/SQL-Cheat-Sheet|SQL Cheat Sheet]]
- [[10-Interview-Prep/SQL-Interview-Questions|Interview Prep]]
