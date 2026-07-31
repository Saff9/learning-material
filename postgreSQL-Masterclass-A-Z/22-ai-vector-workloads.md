# 22 - AI & Vector Workloads

> pgvector, embeddings, HNSW/IVFFlat, RAG patterns, and hybrid search.

---

## pgvector Setup

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table with embeddings
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536)  -- OpenAI ada-002 dimension
);

-- Insert with embedding
INSERT INTO documents (content, embedding)
VALUES ('PostgreSQL is a powerful database', '[0.1, 0.2, ... 1536 values]');
```

---

## Vector Indexes

### HNSW (Recommended for most cases)

```sql
-- Create HNSW index
CREATE INDEX idx_docs_embedding ON documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Query with ef search parameter
SET hnsw.ef_search = 100;
SELECT * FROM documents 
ORDER BY embedding <=> '[query_embedding]' 
LIMIT 10;
```

### IVFFlat

```sql
-- Create IVFFlat index
CREATE INDEX idx_docs_embedding_ivf ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

| Index | Build Time | Query Speed | Memory | Best For |
|-------|-----------|-------------|--------|----------|
| HNSW | Slower | Faster | Higher | High accuracy, dynamic data |
| IVFFlat | Faster | Slower | Lower | Static data, memory constrained |

---

## Distance Operators

```sql
-- L2 distance (Euclidean)
SELECT embedding <-> '[query]' FROM documents ORDER BY 1 LIMIT 10;

-- Inner product
SELECT embedding <#> '[query]' FROM documents ORDER BY 1 LIMIT 10;

-- Cosine distance
SELECT embedding <=> '[query]' FROM documents ORDER BY 1 LIMIT 10;

-- L1 distance
SELECT embedding <+> '[query]' FROM documents ORDER BY 1 LIMIT 10;
```

---

## Hybrid Search (Vector + Full-Text)

```sql
-- Combine vector similarity with text relevance
WITH vector_results AS (
    SELECT id, 1 - (embedding <=> '[query_embedding]') AS vector_score
    FROM documents ORDER BY embedding <=> '[query_embedding]' LIMIT 100
),
text_results AS (
    SELECT id, ts_rank(to_tsvector('english', content), 
        plainto_tsquery('english', 'search terms')) AS text_score
    FROM documents
    WHERE to_tsvector('english', content) @@ plainto_tsquery('english', 'search terms')
)
SELECT 
    d.id, d.content,
    COALESCE(v.vector_score, 0) * 0.7 + COALESCE(t.text_score, 0) * 0.3 AS combined_score
FROM documents d
LEFT JOIN vector_results v ON d.id = v.id
LEFT JOIN text_results t ON d.id = t.id
WHERE v.id IS NOT NULL OR t.id IS NOT NULL
ORDER BY combined_score DESC
LIMIT 10;
```

---

## RAG Pattern (Retrieval-Augmented Generation)

```sql
-- 1. Store documents with chunks
CREATE TABLE document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES documents(id),
    chunk_index INTEGER,
    content TEXT,
    embedding VECTOR(1536)
);

-- 2. Create index
CREATE INDEX idx_chunks_embedding ON document_chunks 
USING hnsw (embedding vector_cosine_ops);

-- 3. Retrieve relevant chunks
SELECT content 
FROM document_chunks 
ORDER BY embedding <=> '[user_query_embedding]' 
LIMIT 5;

-- 4. Send retrieved chunks + user query to LLM
```

---

## pgvectorscale (2026)

```sql
-- pgvectorscale adds DiskANN for billion-scale vectors
-- and StreamingDiskANN for memory-efficient search
CREATE INDEX idx_large_embedding ON documents 
USING diskann (embedding vector_cosine_ops);
```

---

## Half-Precision Vectors (pgvector 0.8+)

```sql
-- Use halfvec for 50% memory reduction with minimal accuracy loss
CREATE TABLE documents_half (
    id BIGSERIAL PRIMARY KEY,
    embedding halfvec(1536)
);

CREATE INDEX idx_half ON documents_half USING hnsw (embedding halfvec_cosine_ops);
```

---
*Previous: 21 - Extensions | Next: 23 - Cloud Deployment*
