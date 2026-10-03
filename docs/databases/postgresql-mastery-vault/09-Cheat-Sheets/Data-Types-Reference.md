---
tags: [cheat-sheet, data-types, reference]
---

# Data Types Reference

## Numeric

| Type | Use |
|------|-----|
| `SMALLINT` | Small numbers (-32K to 32K) |
| `INTEGER` / `INT` | Default whole numbers |
| `BIGINT` | Large numbers |
| `NUMERIC(p,s)` | Exact decimals (money) |
| `REAL` | Float (4 bytes) |
| `DOUBLE PRECISION` | Float (8 bytes) |
| `SERIAL` | Auto-increment (legacy, prefer IDENTITY) |
| `BIGINT GENERATED ALWAYS AS IDENTITY` | Modern auto-increment PK |

## Text

| Type | Use |
|------|-----|
| `TEXT` | Variable, no limit (**preferred**) |
| `VARCHAR(n)` | Variable, max n chars |
| `CHAR(n)` | Fixed, blank-padded (avoid) |

## Date/Time

| Type | Use |
|------|-----|
| `DATE` | Calendar date |
| `TIME` | Time of day |
| `TIMETZ` | Time with timezone |
| `TIMESTAMP` | Date and time |
| `TIMESTAMPTZ` | Date+time+timezone (**preferred**) |
| `INTERVAL` | Duration |

## Other

| Type | Use |
|------|-----|
| `BOOLEAN` | true/false |
| `UUID` | UUID (use `gen_random_uuid()` or `uuidv7()`) |
| `JSONB` | Binary JSON (**preferred over json**) |
| `TEXT[]` | Array of text |
| `INET` | IP address |
| `TSTZRANGE` | Time range (for bookings) |

## Related

- [[01-Foundations/05-Data-Types|Data Types (detailed)]]
- [[09-Cheat-Sheets/SQL-Cheat-Sheet|SQL Cheat Sheet]]
