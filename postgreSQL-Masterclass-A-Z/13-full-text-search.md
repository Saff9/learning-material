# 13 - Full-Text Search

> Built-in text search with tsvector, tsquery, dictionaries, ranking, and indexing.

---

## Basics

```sql
-- Convert text to tsvector (search document)
SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog');
-- Result: 'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2

-- Convert query to tsquery
SELECT to_tsquery('english', 'fox & dog');
-- Result: 'fox' & 'dog'

-- Match
SELECT to_tsvector('english', 'The quick brown fox') @@ to_tsquery('english', 'fox & dog');
-- Result: FALSE (no dog)

SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog') 
    @@ to_tsquery('english', 'fox & dog');
-- Result: TRUE
```

---

## Table Setup

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    search_vector TSVECTOR
);

-- Update search vector
UPDATE articles SET search_vector = 
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(content, '')), 'B');

-- Trigger to auto-update
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_articles_search
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_search_vector();
```

---

## Querying

```sql
-- Basic search
SELECT * FROM articles 
WHERE search_vector @@ to_tsquery('english', 'postgresql & tutorial');

-- Plain text query (handles quoting)
SELECT * FROM articles 
WHERE search_vector @@ plainto_tsquery('english', 'postgresql tutorial');
-- Equivalent to: 'postgresql' & 'tutorial'

-- Phrase search
SELECT * FROM articles 
WHERE search_vector @@ phraseto_tsquery('english', 'quick brown fox');
-- Equivalent to: 'quick' <-> 'brown' <-> 'fox'

-- Web search style
SELECT * FROM articles 
WHERE search_vector @@ websearch_to_tsquery('english', 'postgresql -mysql tutorial');

-- Ranking
SELECT 
    title,
    ts_rank(search_vector, to_tsquery('english', 'postgresql')) AS rank
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql')
ORDER BY rank DESC;

-- Ranking with weights
SELECT 
    title,
    ts_rank_cd('{0.1, 0.2, 0.4, 1.0}', search_vector, 
               to_tsquery('english', 'postgresql')) AS rank
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql')
ORDER BY rank DESC;

-- Highlighting
SELECT 
    title,
    ts_headline('english', content, to_tsquery('english', 'postgresql'),
        'StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=10'
    ) AS snippet
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql');
```

---

## Indexing

```sql
-- GIN index (recommended for read-heavy)
CREATE INDEX idx_articles_search ON articles USING gin(search_vector);

-- GiST index (good for frequent updates)
CREATE INDEX idx_articles_search_gist ON articles USING gist(search_vector);
```

---

## Dictionaries & Configuration

```sql
-- List configurations
SELECT * FROM pg_ts_config;

-- Simple search (no stemming)
SELECT to_tsvector('simple', 'The quick brown foxes');
-- Result: 'The':1 'brown':3 'foxes':4 'quick':2

-- English search (with stemming)
SELECT to_tsvector('english', 'The quick brown foxes');
-- Result: 'brown':3 'fox':4 'quick':2

-- Custom dictionary
CREATE TEXT SEARCH DICTIONARY my_dict (
    TEMPLATE = snowball,
    LANGUAGE = english
);
```

---

## Multilingual Search

```sql
-- Store language per document
CREATE TABLE multilingual_docs (
    id SERIAL PRIMARY KEY,
    lang VARCHAR(2) DEFAULT 'en',
    title TEXT,
    content TEXT
);

-- Search with correct language
SELECT * FROM multilingual_docs 
WHERE to_tsvector(lang::regconfig, content) @@ to_tsquery(lang::regconfig, 'search_term');
```

---
*Previous: 12 - Arrays | Next: 14 - Views & Materialized Views*
