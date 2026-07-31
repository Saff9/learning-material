# 13 - Full-Text Search

> Built-in text search with tsvector, tsquery, dictionaries, ranking, and indexing. Advanced concepts include fuzzy matching, trigrams, and custom dictionary creation.

---

## Basics

```sql
-- Convert text to tsvector (search document)
-- A tsvector is a sorted list of distinct lexemes, which are words that have been normalized to merge different variants of the same word (see dictionaries).
SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog');
-- Result: 'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2

-- Convert query to tsquery
-- A tsquery contains search terms, which must be already-normalized lexemes, and may combine multiple terms using AND, OR, NOT, and FOLLOWED BY operators.
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
-- We assign different weights to different parts of the document.
-- 'A' weight is usually for titles, 'B' for summaries, 'C' for content, etc.
UPDATE articles SET search_vector = 
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(content, '')), 'B');

-- Trigger to auto-update
-- While triggers work, PostgreSQL 12+ supports generated columns which are much simpler!
ALTER TABLE articles ADD COLUMN search_vector_gen tsvector 
    GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(content, '')), 'B')
    ) STORED;

-- If using older PostgreSQL or needing complex logic:
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
-- <-> operator ensures the words follow each other in exactly that order
SELECT * FROM articles 
WHERE search_vector @@ phraseto_tsquery('english', 'quick brown fox');
-- Equivalent to: 'quick' <-> 'brown' <-> 'fox'

-- Web search style
-- Supports "quoted phrases", OR, and -exclusion
SELECT * FROM articles 
WHERE search_vector @@ websearch_to_tsquery('english', 'postgresql -mysql "advanced tutorial" OR guide');

-- Ranking
-- ts_rank calculates a score based on how often lexemes appear
SELECT 
    title,
    ts_rank(search_vector, to_tsquery('english', 'postgresql')) AS rank
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql')
ORDER BY rank DESC;

-- Ranking with weights
-- Customizing weights (D, C, B, A) -> Default is {0.1, 0.2, 0.4, 1.0}
SELECT 
    title,
    ts_rank_cd('{0.1, 0.2, 0.4, 1.0}', search_vector, 
               to_tsquery('english', 'postgresql')) AS rank
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql')
ORDER BY rank DESC;

-- Highlighting
-- ts_headline generates a snippet showing where the match occurred
SELECT 
    title,
    ts_headline('english', content, to_tsquery('english', 'postgresql'),
        'StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=10'
    ) AS snippet
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql');
```

---

## Indexing (GIN vs GiST)

```sql
-- GIN index (recommended for read-heavy workloads)
-- GIN (Generalized Inverted Index) creates an inverted index, mapping every lexeme to the row IDs containing it. 
-- It is up to 3x faster for querying than GiST but slower to build and update.
CREATE INDEX idx_articles_search ON articles USING gin(search_vector);

-- GiST index (good for frequent updates)
-- GiST (Generalized Search Tree) stores a hashed representation of the tsvector.
-- It is lossy (may produce false positives that must be filtered out by fetching the actual row) but much faster to update.
CREATE INDEX idx_articles_search_gist ON articles USING gist(search_vector);

-- For extremely fast lookups on large tables, you can partition your text search index
-- or use tools like pg_trgm for partial matching fallback.
```

---

## Fuzzy Matching & Trigrams (pg_trgm)

PostgreSQL's `pg_trgm` extension is perfect for fuzzy text search, autocomplete, and finding typos.

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Basic similarity
SELECT similarity('postgresql', 'postgresql'); -- 1.0
SELECT similarity('postgresql', 'postgre sql'); -- 0.72

-- Searching with similarity threshold
-- Set the minimum similarity threshold (default is 0.3)
SET pg_trgm.similarity_threshold = 0.4;

SELECT title 
FROM articles 
WHERE title % 'postgress'; -- Uses the % operator for similarity

-- Trigram Index (Crucial for performance)
-- Works for LIKE, ILIKE, %, and regex operations!
CREATE INDEX idx_articles_title_trgm ON articles USING gin (title gin_trgm_ops);

-- Lightning fast ILIKE search using trigram index
SELECT * FROM articles WHERE title ILIKE '%tutorial%'; 
```

---

## Dictionaries & Configuration

Dictionaries eliminate stop words (e.g., 'the', 'a') and normalize words into lexemes (e.g., 'running' -> 'run').

```sql
-- List configurations
SELECT * FROM pg_ts_config;

-- Simple search (no stemming)
SELECT to_tsvector('simple', 'The quick brown foxes');
-- Result: 'The':1 'brown':3 'foxes':4 'quick':2

-- English search (with stemming)
SELECT to_tsvector('english', 'The quick brown foxes');
-- Result: 'brown':3 'fox':4 'quick':2

-- Custom dictionary configuration
CREATE TEXT SEARCH DICTIONARY my_dict (
    TEMPLATE = snowball,
    LANGUAGE = english
);

-- Using unaccent extension for language-agnostic character handling
CREATE EXTENSION IF NOT EXISTS unaccent;
SELECT unaccent('Hôtel'); -- Returns 'Hotel'

-- Creating a custom search configuration utilizing unaccent
CREATE TEXT SEARCH CONFIGURATION fr_unaccent (COPY = french);
ALTER TEXT SEARCH CONFIGURATION fr_unaccent
    ALTER MAPPING FOR hword, hword_part, word
    WITH unaccent, french_stem;
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

-- Map varchar language codes to regconfig
CREATE OR REPLACE FUNCTION lang_to_regconfig(lang VARCHAR) RETURNS regconfig AS $$
BEGIN
    RETURN CASE lang
        WHEN 'en' THEN 'english'::regconfig
        WHEN 'fr' THEN 'french'::regconfig
        WHEN 'de' THEN 'german'::regconfig
        ELSE 'simple'::regconfig
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Create expression index for multilingual search
CREATE INDEX idx_multilingual_search ON multilingual_docs USING gin (
    to_tsvector(lang_to_regconfig(lang), content)
);

-- Search with correct language
SELECT * FROM multilingual_docs 
WHERE to_tsvector(lang_to_regconfig(lang), content) @@ to_tsquery('english', 'search_term');
```

---
*Previous: 12 - Arrays | Next: 14 - Views & Materialized Views*
