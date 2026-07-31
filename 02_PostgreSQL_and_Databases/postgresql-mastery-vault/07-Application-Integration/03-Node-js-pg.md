---
tags: [postgresql, nodejs, javascript, pg, integration]
---

# Node.js + pg (node-postgres)

The foundational PostgreSQL driver for Node.js.

## Installation

```bash
npm install pg
```

## Connection Pool (Recommended)

```javascript
const { Pool } = require('pg');

// One pool per application process
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    max: 20,                    // max clients in pool
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
});

// Parameterized query (prevents SQL injection!)
async function getUser(email) {
    const { rows } = await pool.query(
        'SELECT id, name, email FROM users WHERE email = $1',
        [email]
    );
    return rows[0];
}

async function createUser(name, email) {
    const { rows } = await pool.query(
        'INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id',
        [name, email]
    );
    return rows[0].id;
}
```

## Transactions

```javascript
async function transferMoney(fromId, toId, amount) {
    const client = await pool.connect();
    try {
        await client.query('BEGIN');
        await client.query('UPDATE accounts SET balance = balance - $1 WHERE id = $2', [amount, fromId]);
        await client.query('UPDATE accounts SET balance = balance + $1 WHERE id = $2', [amount, toId]);
        await client.query('COMMIT');
    } catch (e) {
        await client.query('ROLLBACK');
        throw e;
    } finally {
        client.release();  // always release back to pool
    }
}
```

> [!warning] Always use $1, $2 placeholders
> NEVER use JavaScript template literals (backticks) for SQL values. This causes SQL injection. Always use `$1, $2` parameterized queries.

## Next

- [[07-Application-Integration/04-Prisma|Prisma ORM]]
- [[07-Application-Integration/05-Supabase|Supabase]]
