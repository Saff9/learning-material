---
tags: [postgresql, advanced, full-text-search, fts]
---

# Full-Text Search

PostgreSQL has built-in full-text search that handles most search needs without Elasticsearch.

## Basic Full-Text Search

```sql
-- Create a tsvector column for search
ALTER TABLE posts ADD COLUMN search_vector tsvector;

-- Populate it
UPDATE posts SET search_vector = to_tsvector('english', title || ' ' || body);

-- Create a GIN index
CREATE INDEX idx_posts_search ON posts USING GIN (search_vector);

-- Search
SELECT title, ts_rank(search_vector, query) AS rank
FROM posts, to_tsquery('english', 'postgres & tutorial') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

## Using a Trigger (Auto-Update)

```sql
-- Function to auto-update search vector
CREATE OR REPLACE FUNCTION posts_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector = to_tsvector('english', coalesce(NEW.title,'') || ' ' || coalesce(NEW.body,''));
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER trg_posts_search
    BEFORE INSERT OR UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION posts_search_trigger();
```

## Search Queries

```sql
-- Simple word search
SELECT * FROM posts WHERE search_vector @@ to_tsquery('english', 'postgres');

-- Multiple words (AND)
SELECT * FROM posts WHERE search_vector @@ to_tsquery('english', 'postgres & tutorial');

-- Multiple words (OR)
SELECT * FROM posts WHERE search_vector @@ to_tsquery('english', 'postgres | mysql');

-- Phrase search
SELECT * FROM posts WHERE search_vector @@ phraseto_tsquery('english', 'postgres tutorial');

-- Websearch-style query (Google-like)
SELECT * FROM posts WHERE search_vector @@ websearch_to_tsquery('english', '"postgres tutorial" -mysql');
```

## Ranking and Highlighting

```sql
SELECT
    title,
    ts_rank(search_vector, query) AS rank,
    ts_headline('english', body, query, 'MaxWords=35, MinWords=15') AS snippet
FROM posts, websearch_to_tsquery('english', 'postgres tutorial') query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 10;
```

## Next

- [[04-Advanced-Topics/06-JSON-JSONB|JSON/JSONB]]
- [[06-Extensions/03-pg_trgm|pg_trgm for fuzzy search]]
