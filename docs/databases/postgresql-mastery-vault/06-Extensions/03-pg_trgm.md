---
tags: [postgresql, extensions, pg_trgm, fuzzy-search]
---

# pg_trgm — Trigram Fuzzy Search

Provides fuzzy text matching using trigrams (3-character sequences).

## Setup

```sql
CREATE EXTENSION pg_trgm;
```

## Usage

```sql
-- Create a GIN index for fast fuzzy search
CREATE INDEX idx_users_name_trgm ON users USING GIN (name gin_trgm_ops);

-- Fuzzy match with ILIKE (now uses the index)
SELECT * FROM users WHERE name ILIKE '%jon%';

-- Similarity search (returns similar names)
SELECT name, similarity(name, 'John') AS sim
FROM users
WHERE name % 'John'
ORDER BY sim DESC
LIMIT 10;

-- Show similarity score
SELECT name, similarity(name, 'Alice') AS sim FROM users ORDER BY sim DESC;
```

## When to Use

- Search with typos
- Autocomplete
- Deduplication (find similar entries)
- "Did you mean...?" suggestions

## Next

- [[06-Extensions/04-pgvector|pgvector for AI]]
- [[06-Extensions/05-Other-Useful-Extensions|Other Extensions]]
