---
tags: [project, intermediate, blog, relationships]
---

# Project 2: Blog Platform

A blog with users, posts, comments, and tags. Tests relationships, JOINs, and aggregation.

## Schema

```sql
CREATE DATABASE blog;
\c blog

CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    bio TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE posts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    author_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    published BOOLEAN NOT NULL DEFAULT false,
    view_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE comments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body TEXT NOT NULL,
    post_id BIGINT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE post_tags (
    post_id BIGINT REFERENCES posts(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);

-- Indexes for performance
CREATE INDEX idx_posts_author ON posts(author_id);
CREATE INDEX idx_posts_published ON posts(published, created_at DESC);
CREATE INDEX idx_comments_post ON comments(post_id);

-- Sample data
INSERT INTO users (username, email, bio) VALUES
    ('alice', 'alice@blog.com', 'Software engineer'),
    ('bob', 'bob@blog.com', 'Database enthusiast');

INSERT INTO posts (title, body, author_id, published) VALUES
    ('Getting Started with PostgreSQL', 'PostgreSQL is...', 1, true),
    ('Advanced SQL Techniques', 'Window functions...', 1, true),
    ('My Draft Post', 'Work in progress...', 2, false);

INSERT INTO comments (body, post_id, author_id) VALUES
    ('Great post!', 1, 2),
    ('Thanks for sharing.', 1, 1),
    ('Very helpful.', 2, 2);

INSERT INTO tags (name) VALUES ('postgres'), ('sql'), ('tutorial'), ('advanced');
INSERT INTO post_tags VALUES (1,1), (1,2), (1,3), (2,1), (2,2), (2,4);
```

## Queries to Build

```sql
-- Get published posts with author and comment count
SELECT p.title, u.username, COUNT(c.id) AS comment_count
FROM posts p
JOIN users u ON u.id = p.author_id
LEFT JOIN comments c ON c.post_id = p.id
WHERE p.published = true
GROUP BY p.id, u.username
ORDER BY p.created_at DESC;

-- Search posts by tag
SELECT p.title FROM posts p
JOIN post_tags pt ON pt.post_id = p.id
JOIN tags t ON t.id = pt.tag_id
WHERE t.name = 'postgres';

-- Top authors by post count
SELECT u.username, COUNT(p.id) AS post_count
FROM users u
LEFT JOIN posts p ON p.author_id = u.id AND p.published = true
GROUP BY u.username
ORDER BY post_count DESC;

-- Recent comments with post title
SELECT c.body, c.created_at, p.title AS post_title, u.username AS commenter
FROM comments c
JOIN posts p ON p.id = c.post_id
JOIN users u ON u.id = c.author_id
ORDER BY c.created_at DESC LIMIT 5;
```

## What You Learn

- Many-to-many relationships (post_tags junction table)
- CASCADE deletes
- Complex JOINs (3+ tables)
- Aggregation with GROUP BY
- Indexing strategy

## Next

- [[08-Projects/03-E-commerce-Database|Project 3: E-commerce]]
- [[08-Projects/04-Analytics-Dashboard|Project 4: Analytics]]
