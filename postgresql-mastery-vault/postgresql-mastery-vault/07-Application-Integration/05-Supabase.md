---
tags: [postgresql, supabase, baas, integration]
---

# Supabase — PostgreSQL BaaS

Supabase is an open-source Firebase alternative built on PostgreSQL. It adds Auth, Realtime, Storage, and Edge Functions on top of managed Postgres.

## What You Get

- **PostgreSQL database** (full access, not a wrapper)
- **Auth** (email/password, OAuth, magic links)
- **Realtime** (subscribe to database changes via WebSocket)
- **Storage** (file storage with RLS policies)
- **Edge Functions** (Deno-based serverless functions)
- **Auto REST API** (via PostgREST)
- **Dashboard GUI** (like phpMyAdmin but better)

## Free Tier (2026)

- 500MB database
- 50,000 monthly active users (auth)
- 1GB file storage
- Paused when inactive (7 days)

## JavaScript Client

```bash
npm install @supabase/supabase-js
```

```javascript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_ANON_KEY
);

// CRUD — goes through PostgREST, enforced by RLS
await supabase.from('posts').insert({ title: 'Hello', body: 'World' });

const { data, error } = await supabase
    .from('posts')
    .select('*, author(*)')  // joins are automatic!
    .eq('published', true)
    .order('created_at', { ascending: false })
    .limit(10);

await supabase.from('posts').update({ title: 'Updated' }).eq('id', 1);
await supabase.from('posts').delete().eq('id', 1);
```

## Row Level Security (RLS) — Essential

> [!important] Enable RLS on every table exposed to the client
> Without RLS, the anon key can read/write ALL data. RLS policies enforce per-row access based on the authenticated user.

```sql
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Users can only see their own posts
CREATE POLICY "select own posts" ON posts
    FOR SELECT USING (auth.uid() = author_id);

-- Users can only insert posts for themselves
CREATE POLICY "insert own posts" ON posts
    FOR INSERT WITH CHECK (auth.uid() = author_id);

-- Users can only update/delete their own posts
CREATE POLICY "update own posts" ON posts
    FOR UPDATE USING (auth.uid() = author_id);
```

## Python Client

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
data = supabase.table("posts").select("*").eq("author_id", user_id).execute()
```

## Realtime Subscriptions

```javascript
const subscription = supabase
    .channel('posts-changes')
    .on('postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'posts' },
        payload => console.log('New post:', payload.new)
    )
    .subscribe();
```

## When to Use Supabase

- Full-stack apps that need auth + database + storage
- Rapid prototyping (set up in 5 minutes)
- When you want Postgres power without managing infrastructure
- Real-time apps (chat, live dashboards)

## Next

- [[07-Application-Integration/06-Connection-Pooling|Connection Pooling]]
- [[08-Projects/01-Study-Log-App|Build a Study Log App]]
