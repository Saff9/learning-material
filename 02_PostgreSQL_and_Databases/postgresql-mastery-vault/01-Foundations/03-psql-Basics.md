---
tags: [postgresql, foundations, psql, cli]
---

# psql Basics

`psql` is PostgreSQL's interactive command-line tool. It is the most powerful way to interact with PostgreSQL — every GUI tool (pgAdmin, DBeaver, TablePlus) is ultimately a wrapper around what psql can do.

## Connecting

```bash
# Basic connection
psql -U username -d databasename -h localhost -p 5432

# With password prompt
psql -U username -d databasename -W

# Connection URI
psql "postgresql://username:password@localhost:5432/databasename"

# Run a single query and exit
psql -c "SELECT version();"

# Execute a SQL file
psql -f schema.sql

# Execute a file in a single transaction
psql -1 -f migrate.sql
```

## Essential Meta-Commands

psql meta-commands start with a backslash (`\`). These are NOT SQL — they are psql commands.

### Navigation

| Command | What It Does |
|---------|-------------|
| `\l` or `\l+` | List databases (with sizes and descriptions) |
| `\c dbname` | Connect to a different database |
| `\dn` | List schemas |
| `\dt` or `\dt+` | List tables in current schema (with sizes) |
| `\dt *.*` | List tables in ALL schemas |
| `\d tablename` | Describe a table (columns, types, indexes, FKs) |
| `\d+ tablename` | Describe with storage info and description |
| `\di` | List indexes |
| `\dv` | List views |
| `\ds` | List sequences |
| `\df` | List functions |
| `\dT` | List data types |
| `\dx` | List installed extensions |
| `\du` or `\dg` | List roles/users |
| `\dp` or `\z` | Show table access privileges |

### Output Formatting

| Command | What It Does |
|---------|-------------|
| `\x` | Toggle expanded (vertical) output — great for wide rows |
| `\x auto` | Auto-expand wide rows (recommended) |
| `\a` | Toggle aligned/unaligned output |
| `\H` | Toggle HTML output |
| `\t` | Show tuples only (no headers/footers) |
| `\pset border 2` | Box-drawing table borders |
| `\pset null '∅'` | Show NULLs with a visible symbol |

### Help

| Command | What It Does |
|---------|-------------|
| `\?` | Help on psql meta-commands |
| `\h SQL_STATEMENT` | Help on a SQL statement (e.g., `\h CREATE TABLE`) |
| `\h` | List all SQL commands with help available |

### File and Editor

| Command | What It Does |
|---------|-------------|
| `\i file.sql` | Execute SQL from a file |
| `\o file.txt` | Send query output to a file |
| `\o` | Stop sending output to file |
| `\e` | Open current query buffer in `$EDITOR` |
| `\ef func_name` | Edit a function definition |
| `\s` | Show command history |

### Other Useful Commands

| Command | What It Does |
|---------|-------------|
| `\timing` | Toggle query timing on/off |
| `\watch 5` | Re-run last query every 5 seconds |
| `\conninfo` | Show current connection details |
| `\q` | Quit psql |
| `\copy` | Client-side CSV import/export (works without superuser) |

## Try It Yourself

```bash
# Connect to PostgreSQL
sudo -u postgres psql
```

```sql
-- List databases
\l

-- Create a practice database
CREATE DATABASE practice;

-- Connect to it
\c practice

-- Create a table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert some data
INSERT INTO users (name, email) VALUES
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Carol', 'carol@example.com');

-- Describe the table
\d users

-- Query the data
SELECT * FROM users;

-- Toggle expanded output for better readability
\x
SELECT * FROM users;

-- Turn on timing
\timing
SELECT * FROM users;

-- List tables
\dt

-- Quit
\q
```

## The .psqlrc File

Create a `~/.psqlrc` file to customize psql on startup:

```sql
-- ~/.psqlrc
\set PROMPT1 '%[%033[1m%]%n@%/%[%033[0m%]%R%# '
\set PROMPT2 '> '
\pset pager off
\pset null '∅'
\pset border 2
\pset linestyle unicode
\x auto
\timing on
\set HISTFILE ~/.psql_history-:DBNAME
\set HISTCONTROL ignoredups
\set VERBOSE verbose
\set ON_ERROR_STOP on

-- Handy aliases
\set e 'EXPLAIN ANALYZE'
\set eps 'EXPLAIN (ANALYZE, BUFFERS, VERBOSE)'
```

> [!tip] pgcli — a modern alternative
> [pgcli](https://www.pgcli.com) is a psql replacement with auto-completion and syntax highlighting. Install with `pip install pgcli` and run with `pgcli -U username -d databasename`. It supports most psql meta-commands.

## CSV Import/Export

### Export to CSV

```sql
-- Server-side (requires superuser or pg_write_server_files role)
COPY users TO '/tmp/users.csv' WITH CSV HEADER;

-- Client-side (works for any user)
\copy users TO '/tmp/users.csv' WITH CSV HEADER;

-- Custom query
\copy (SELECT name, email FROM users ORDER BY name) TO '/tmp/emails.csv' WITH CSV HEADER
```

### Import from CSV

```sql
-- Create table first
CREATE TABLE imports (id int, name text, email text);

-- Import
\copy imports FROM '/tmp/data.csv' WITH CSV HEADER;

-- Or with specific delimiter
\copy imports FROM '/tmp/data.csv' WITH (FORMAT csv, HEADER true, DELIMITER ';')
```

## Key Bindings

- **Up/Down arrows** — navigate command history
- **Ctrl+R** — reverse search history
- **Tab** — autocomplete table/column names
- **Ctrl+L** — clear screen

## What's Next

- [[01-Foundations/04-Creating-Database-Tables|Creating Databases and Tables]]
- [[01-Foundations/05-Data-Types|Data Types]]
- [[09-Cheat-Sheets/psql-Commands|psql Commands Cheat Sheet]]

## External Resources

- [Official psql Documentation](https://www.postgresql.org/docs/current/app-psql.html)
- [psql Cheat Sheet (Kartones)](https://gist.github.com/Kartones/dd3ff5ec5ea238d4c546)
- [pgcli](https://www.pgcli.com)
