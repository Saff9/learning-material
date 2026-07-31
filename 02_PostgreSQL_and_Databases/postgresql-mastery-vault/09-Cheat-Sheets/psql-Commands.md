---
tags: [cheat-sheet, psql, cli, reference]
---

# psql Commands Cheat Sheet

## Connection

```bash
psql -U user -d dbname -h localhost -p 5432 -W
psql "postgresql://user:pass@host:5432/dbname"
psql -c "SELECT 1;"  # run and exit
psql -f file.sql     # execute file
```

## Meta-Commands

| Command | Purpose |
|---------|---------|
| `\l` | List databases |
| `\c dbname` | Connect to database |
| `\dt` | List tables |
| `\d table` | Describe table |
| `\d+ table` | Describe with details |
| `\di` | List indexes |
| `\dv` | List views |
| `\df` | List functions |
| `\du` | List roles |
| `\dx` | List extensions |
| `\dn` | List schemas |
| `\dp table` | Show privileges |
| `\x` | Toggle expanded output |
| `\x auto` | Auto-expand |
| `\timing` | Toggle query timing |
| `\i file.sql` | Execute SQL file |
| `\o file` | Output to file |
| `\e` | Edit in $EDITOR |
| `\watch 5` | Re-run last query every 5s |
| `\?` | Help on meta-commands |
| `\h SQL_CMD` | Help on SQL command |
| `\q` | Quit |

## Copy (CSV)

```sql
\copy users TO 'users.csv' WITH CSV HEADER
\copy users FROM 'data.csv' WITH CSV HEADER
\copy (SELECT name, email FROM users) TO 'emails.csv' WITH CSV HEADER
```

## Related

- [[09-Cheat-Sheets/SQL-Cheat-Sheet|SQL Cheat Sheet]]
- [[01-Foundations/03-psql-Basics|psql Basics]]
