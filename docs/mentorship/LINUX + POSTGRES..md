# Linux Learning Log — Owais

A full record of a Linux learning session (WSL on Windows), taught lesson-by-lesson. Background: completed CS50P, not yet in college, goal is to become a software developer.

---

## Setup

- Installed WSL (Windows Subsystem for Linux) for learning Linux.
- Later installed Zsh for a nicer-looking terminal:
    
    ```bash
    sudo apt update && sudo apt install zsh -ychsh -s $(which zsh)
    ```
    
- First command run: `whoami` → output: `owais`

---

## Lesson 1: The Linux Filesystem

**Why it matters:** In Linux, everything is a file, and all files live in one tree starting from `/` (root). Understanding this tree = understanding Linux.

**The Tree Structure**

```
/
├── home/       → your personal files (like C:\Users\)
├── etc/        → system configuration files
├── bin/        → essential programs/commands
├── var/        → logs, temporary data
├── tmp/        → temporary files (wiped on reboot)
└── root/       → home folder for the admin user
```

**Commands learned**

|Command|What it does|
|---|---|
|`pwd`|Print Working Directory — where am I right now?|
|`ls`|List files in current directory|
|`cd`|Change Directory — move somewhere|
|`cd ..`|Go up one level (parent folder)|
|`cd ~`|Go home instantly|
|`mkdir`|Create a folder|
|`touch`|Create an empty file|
|`rm`|Delete a file|
|`rm -r`|Delete a folder and everything inside it (recursive)|

**Exercises & Results**

- `pwd` → `/home/owais`
- `ls` (home) → `practice`
- `cd /` then `ls` → `bin dev home lib sys usr boot ...`
- `cd ~` → back to `/home/owais`
- `cd ..` twice → `/home` → `/`
- `mkdir linux_lessons` → `cd linux_lessons` → `touch file1.txt file2.txt file3.txt` → `ls` showed all 3 files
- `rm file1.txt` → file removed
- `cd ~` → `rm -r linux_lessons` → folder fully removed; `ls` showed only `practice`

**⚠️ Key warning:** Linux has **no recycle bin**. `rm` is permanent — no undo, no recovery. Always double-check before running it.

---

## Lesson 2: Reading and Writing Files

**Why it matters:** Developers constantly read logs, write configs, and edit code from the terminal.

**Commands learned**

|Command/Symbol|Purpose|
|---|---|
|`echo "text"`|Print text to screen|
|`>`|Redirect output to file (**overwrites**)|
|`>>`|Redirect output to file (**appends**)|
|`cat`|Read entire file|
|`less`|Read file page by page|
|`head`|Show first 10 lines|
|`nano`|Edit files in terminal|

**Exercises & Results**

- `echo "Hello I am owais and I am learning linux" > hello.txt` → `cat hello.txt` printed the line.
- `echo "I completed cs50p" >> hello.txt` → appended a second line.
- `echo "oops I overwrote everything" > hello.txt` → confirmed `>` destroys old content; `cat` showed only the new line.
- Used `nano hello.txt`: navigated with arrow keys, added a line ("I am learning nano editor"), saved with `Ctrl+O` → `Enter`, exited with `Ctrl+X`. `cat hello.txt` confirmed two lines saved.

**Key distinction**

```
echo "text" > file.txt    ← destroys old content, writes new
echo "text" >> file.txt   ← keeps old content, adds at bottom
```

---

## Lesson 3: `--help` and `man` Pages

**Why it matters:** No developer memorizes every command — knowing how to find answers fast is the real skill.

**Commands learned**

|Method|Purpose|
|---|---|
|`ls --help`|Quick summary of a command and its flags|
|`man ls`|Full manual page (scroll with arrows, quit with `q`)|

**Exercise:** Ran both; explored the `man ls` page and exited with `q`.

---

## Lesson 4: `ls` Flags and File Permissions

**Why it matters:** Permissions control who can read, write, or execute a file — critical for security and for running scripts.

**Useful `ls` flags**

|Command|What it shows|
|---|---|
|`ls`|Basic list|
|`ls -l`|Long format — permissions, size, date|
|`ls -a`|All files — including hidden ones (start with `.`)|
|`ls -la`|Both combined|

**Exercise results**

- `ls` → `code.c`, `hellow.txt`, `practice`
- `ls -l` → showed permission strings like `-rw-r--r-- 1 owais owais 0 jun 29 7:26 code.c`
- `ls -a` → revealed hidden files: `.`, `.bash_history`, `.bashrc`, etc.
- `ls -la` → full combined listing, mix of `-rw-r--r--`, `drwxr-x--`, `drwx------` permission patterns

**Decoding permissions**

```
-  rw-  r--  r--
↑   ↑    ↑    ↑
│   │    │    └── others can only read
│   │    └─────── group can only read  
│   └──────────── owner can read & write
└──────────────── it's a file (not folder, which would be 'd')
```

Full line breakdown:

```
-rw-r--r--  1  owais  owais  48      jun 29 5:18  hello.txt
     │       │    │      │     │           │           │
     │       │    │      │     │           │           └── filename
     │       │    │      │     │           └── last modified
     │       │    │      │     └── size in bytes
     │       │    │      └── group name
     │       │    └── owner name
     │       └── number of links
     └── permissions
```

|Letter|Meaning|
|---|---|
|`r`|read|
|`w`|write|
|`x`|execute|
|`-`|permission not given|

**`chmod`** (change mode = change permissions)

|Command|Meaning|
|---|---|
|`chmod +x file`|Add execute for everyone|
|`chmod -x file`|Remove execute|
|`chmod +w file`|Add write permission|
|`chmod -r file`|Remove read permission|

**Exercise:** `chmod +x hello.txt` → permissions changed from `-rw-r--r--` to `-rwxr-xr-x` (execute added across owner/group/others).

**Why this matters:** Shell scripts and programs won't run in Linux until given execute permission — a common beginner trap.

---

## Lesson 5: Pipes and Filters

**Why it matters:** Each Linux command does one small thing well. Real power comes from chaining commands with the pipe `|`.

```
command1 | command2 | command3
     ↓            ↓           ↓
  output   →   becomes   →  output
             the input
```

**New commands**

|Command|Purpose|
|---|---|
|`grep`|Filter lines matching a pattern|
|`sort`|Sort lines alphabetically|
|`wc -l`|Count number of lines|
|`head`|Show first 10 lines|
|`tail`|Show last 10 lines|

**Exercise: `fruits.txt`**

```bash
echo "banana" > fruits.txt
echo "apple" >> fruits.txt
echo "mango" >> fruits.txt
echo "grape" >> fruits.txt
echo "apricot" >> fruits.txt
```

|Command|Result|
|---|---|
|`cat fruits.txt`|banana, apple, mango, grape, apricot (insertion order)|
|`sort fruits.txt`|apple, apricot, banana, grape, mango (A–Z)|
|`grep "ap" fruits.txt`|apple, grape (contain "ap")|
|`wc -l fruits.txt`|5|

**Chained pipes**

- `cat fruits.txt | sort` → same as `sort fruits.txt`
- `cat fruits.txt | sort | grep "a"` → all fruits contain "a", sorted A–Z
- `cat fruits.txt | grep "a" | wc -l` → 5 (predicted and confirmed)
- `head -3 fruits.txt` → apple, banana, mango (first 3)
- `tail -2 fruits.txt` → last 2 lines
- `cat fruits.txt | sort | tail -2` → grape, mango (last 2 alphabetically — predicted correctly)

**Real-world example:**

```bash
cat server.log | grep "ERROR" | tail -20
```

Find all errors → show the 20 most recent.

**Core takeaway (Unix philosophy):** small commands + pipes = powerful workflows.

---

## Lesson 6: Shell Scripts

**Why it matters:** A shell script is a file full of Linux commands that runs automatically — similar to how Python scripts work, but for controlling the Linux system directly.

**The shebang line**

```bash
#!/bin/bash
```

```
#!        → hey Linux! run this file with...
/bin/bash → ...the bash program located here
```

Comparison:

```
Python files  →  python3 script.py  →  Python interprets it
Shell scripts →  #!/bin/bash        →  Bash interprets it
```

### First script: `myfirst.sh`

```bash
#!/bin/bash
echo "Hello I am Owais"
echo "I am learning Linux shell scripting"
echo "Today's files are:"
ls
```

- Saved with `Ctrl+O` → `Enter` → `Ctrl+X` in `nano`
- Made executable: `chmod +x myfirst.sh`
- Ran with: `./myfirst.sh` (the `./` tells Linux to run the file from the current directory — required for security reasons)
- Output: greeting lines + file listing (`code.c`, `fruits.txt`, `hellow.txt`, `myfirst.sh`, `practice`)

### Variables and conditionals

```bash
#!/bin/bash
name="Owais"
echo "Hello $name"
echo "You are learning Linux"

if [ -f "fruits.txt" ]; then
    echo "fruits.txt EXISTS!"
else
    echo "fruits.txt NOT found"
fi
```

- `$` accesses a variable's value (like Python's `name` but with `$` prefix).
- `-f` tests whether a file exists.

**File test flags**

|Flag|Checks|
|---|---|
|`-f`|is it a file?|
|`-d`|is it a directory?|
|`-e`|does it exist at all?|

**Debugging note:** First attempt had a formatting issue (leftover content not cleared in `nano`, causing `name=owais#!/bin/bash` to appear). Fixed by clearing the file fully (`Ctrl+K` to cut lines in nano) and retyping carefully, paying attention to spacing inside `[ ]` and the semicolon before `then`. Second run gave clean output: `Hello Owais`, `You are learning Linux`, `fruits.txt EXISTS!`.

### Script arguments

```bash
#!/bin/bash
name=$1
echo "Hello $name"

if [ -f "fruits.txt" ]; then
    echo "fruits.txt EXISTS!"
else
    echo "fruits.txt NOT found"
fi
```

- `$1` = first argument passed when running the script (like a function parameter).
- `./myfirst.sh Owais` → `$1 = "Owais"` → "Hello Owais"
- `./myfirst.sh` (no argument) → `$1` is empty → "Hello" (predicted and confirmed correctly)

### Defensive programming — handling missing arguments

```bash
#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: Please provide your name!"
    exit 1
fi

name=$1
echo "Hello $name"
echo "You are learning Linux"

if [ -f "fruits.txt" ]; then
    echo "fruits.txt EXISTS!"
else
    echo "fruits.txt NOT found"
fi
```

- `-z` tests whether a string is empty.
- `exit 1` stops the script with an error status.
- **Why this matters:** real programs should handle bad input gracefully instead of failing silently — professional-level practice.

_(Lesson in progress at the point this log was captured — next step is running and reporting back on both the no-argument and named-argument cases for the defensive version of the script.)_

---

## Full Command Reference (A–Z recap)

|Lesson|Concepts / Commands|
|---|---|
|1 — Filesystem|`pwd`, `ls`, `cd`, `cd ..`, `cd ~`, `mkdir`, `touch`, `rm`, `rm -r`|
|2 — Read/Write|`cat`, `echo`, `>`, `>>`, `nano`|
|3 — Help system|`--help`, `man`|
|4 — Permissions|`ls -l`, `ls -a`, `ls -la`, `chmod`|
|5 — Pipes & filters|`\|`, `grep`, `sort`, `wc -l`, `head`, `tail`|
|6 — Shell scripting|`#!/bin/bash`, variables (`$name`), `if`/`then`/`else`/`fi`, `-f`, `-z`, `$1`, `exit`, `chmod +x`, `./script.sh`|

---

## Teaching Style Notes

- Concepts taught with **why**, not just **what**.
- Student runs each command in their own WSL terminal and reports output before moving on.
- Predictions encouraged before running commands, to build the habit of reasoning before executing.
- Progress paced according to the student's responses; mistakes (e.g. the `nano` formatting issue) used as real teaching moments.

---

---

# Database Learning Log — SQL & PostgreSQL for Big Tech

A mentorship-style learning log on databases, aimed at working at a big tech company. Background: completed CS50P (Python), 18 years old, learning databases for the first time. Plan: master SQL + PostgreSQL deeply first, then move to NoSQL (MongoDB) later.

## Full Roadmap

|Phase|Topic|
|---|---|
|1|SQL Foundations — tables, queries, filtering, joining, aggregating|
|2|PostgreSQL Deep Dive — installation, data types, indexes, constraints, transactions|
|3|Performance & Scale — query optimization, indexing strategies, `EXPLAIN ANALYZE`, partitioning|
|4|Big Data Patterns — sharding, replication, connection pooling, millions of users|
|5|Advanced PostgreSQL — JSON support, full-text search, stored procedures, triggers|
|6|NoSQL (MongoDB) — when to use SQL vs NoSQL, document model, aggregation pipeline|
|7|Big Tech Patterns — how Google/Meta/Amazon actually architect their databases|

---

## Lesson 1 — What Even IS a Database?

A Python dictionary stores data in memory — gone when the program closes. A **database** stores data permanently on disk and lets thousands of users read/write it at the same time.

**The Table** — core building block, exactly like a spreadsheet:

```
users table:
┌────┬──────────┬─────────────────────┬─────┐
│ id │ name     │ email               │ age │
├────┼──────────┼─────────────────────┼─────┤
│ 1  │ Aryan    │ aryan@gmail.com     │ 18  │
│ 2  │ Sara     │ sara@gmail.com      │ 24  │
│ 3  │ John     │ john@gmail.com      │ 31  │
└────┴──────────┴─────────────────────┴─────┘
```

- Each **row** = one record
- Each **column** = one field
- `id` uniquely identifies every row

**CRUD — the five core SQL operations**

```sql
-- CREATE
CREATE TABLE users (
    id    SERIAL PRIMARY KEY,
    name  TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    age   INTEGER
);

-- INSERT
INSERT INTO users (name, email, age)
VALUES ('Aryan', 'aryan@gmail.com', 18);

-- SELECT (read)
SELECT * FROM users;
SELECT name, email FROM users;
SELECT * FROM users WHERE age > 20;
SELECT * FROM users WHERE name = 'Aryan';

-- UPDATE
UPDATE users SET age = 19 WHERE name = 'Aryan';

-- DELETE
DELETE FROM users WHERE id = 3;
```

**Python → SQL analogy map**

|Python|SQL|
|---|---|
|list of dicts|Table|
|one dict|one row|
|dict key|column name|
|`for x in list if x['age'] > 20`|`SELECT * WHERE age > 20`|
|`append()`|`INSERT`|
|modifying a value|`UPDATE`|
|`del`|`DELETE`|

**Homework:** practiced on db-fiddle.com — created `users`, inserted 3 people, filtered by age, updated and deleted a row.

---

## Lesson 2 — Sorting, Aggregates & First JOIN

_(Note: first pass was too query-dump-heavy; lesson was redone with full plain-English explanations — captured below.)_

### `ORDER BY` — sorting results

Like sorting contacts by name on your phone.

```sql
SELECT * FROM users ORDER BY age ASC;   -- youngest first
SELECT * FROM users ORDER BY age DESC;  -- oldest first
```

- `ASC` = ascending (small → big)
- `DESC` = descending (big → small)

### `LIMIT` — stop after N rows

Critical for big apps — never fetch every row at once (e.g. a 3-billion-user table would crash the app).

```sql
SELECT * FROM users ORDER BY age DESC LIMIT 3;
```

### `OFFSET` — pagination

"Skip this many rows, then return results" — how Google search pages or Instagram's "load more" work.

```sql
SELECT * FROM users ORDER BY id ASC LIMIT 2 OFFSET 0; -- page 1
SELECT * FROM users ORDER BY id ASC LIMIT 2 OFFSET 2; -- page 2
SELECT * FROM users ORDER BY id ASC LIMIT 2 OFFSET 4; -- page 3
```

### Aggregate functions — "combine many rows into one answer"

|Function|Meaning|
|---|---|
|`COUNT(*)`|how many rows?|
|`SUM(col)`|add them all up|
|`AVG(col)`|average value|
|`MAX(col)`|highest value|
|`MIN(col)`|lowest value|

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM users WHERE country = 'India';
SELECT SUM(age) FROM users;
SELECT AVG(age) FROM users;
SELECT MAX(age) FROM users;
SELECT MIN(age) FROM users;
```

### `GROUP BY` — split into groups, then aggregate each group

Analogy: counting how many students come from each city — group, then count.

```sql
SELECT country, COUNT(*) AS total_users
FROM users
GROUP BY country;
```

Result:

```
┌──────────┬─────────────┐
│ country  │ total_users │
├──────────┼─────────────┤
│ India    │ 2           │
│ USA      │ 2           │
│ UK       │ 1           │
└──────────┴─────────────┘
```

### `HAVING` — filtering groups (vs `WHERE` filtering rows)

```sql
SELECT country, COUNT(*) AS total
FROM users
GROUP BY country
HAVING COUNT(*) > 1;
```

**Rule:** `WHERE` = filter rows (before grouping). `HAVING` = filter groups (after grouping).

### JOINs — the most important SQL concept

**Why split into tables?** Storing repeated user info on every order row wastes space and risks inconsistency. Instead, link tables via a **foreign key** (`orders.user_id` → `users.id`).

**INNER JOIN** — only rows that match in both tables:

```sql
SELECT users.name, orders.product, orders.price
FROM users
INNER JOIN orders ON users.id = orders.user_id;
```

Users with no orders (e.g. John) are excluded.

**LEFT JOIN** — all rows from the left table, matched or not:

```sql
SELECT users.name, orders.product
FROM users
LEFT JOIN orders ON users.id = orders.user_id;
```

Unmatched rows show `NULL` for the right table's columns (John still appears, with `NULL` product).

**Join types visual:**

```
INNER JOIN          LEFT JOIN           RIGHT JOIN          FULL JOIN
  only overlap       left + overlap      right + overlap      everything
```

INNER JOIN and LEFT JOIN cover ~95% of real-world cases.

### Putting it together

```sql
SELECT users.name, SUM(orders.price) AS total_spent
FROM users
INNER JOIN orders ON users.id = orders.user_id
GROUP BY users.name
ORDER BY total_spent DESC;
```

### Query execution order (important!)

You **write**: `SELECT → FROM → JOIN → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT` PostgreSQL **executes**: `FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`

This explains why a `SELECT` alias can't be used inside `WHERE` — `WHERE` runs before `SELECT`.

**Homework:** Built `users` + `orders` tables on db-fiddle.com, wrote queries for total spent per user, users per country, and a `LEFT JOIN` to find users with no orders. ✅ Completed successfully.

---

## Lesson 3 — PostgreSQL, Data Types, Constraints & Indexes

### What is PostgreSQL, really?

SQL is the language; **PostgreSQL** ("Postgres") is the actual database software that stores data, runs queries, and keeps things safe — free, open source, used by Apple, Instagram, Spotify, Reddit, Uber; handles millions of rows easily.

### Part 1 — Data Types

|Type|Use|Notes|
|---|---|---|
|`INTEGER`|age, count, quantity|whole numbers, ±2 billion range|
|`BIGINT`|views, user_id at scale|for numbers that may exceed 2 billion (e.g. Instagram user IDs)|
|`SERIAL`|`id` columns|auto-incrementing, set automatically|
|`TEXT`|names, bios, descriptions|any length|
|`VARCHAR(n)`|usernames, phone numbers|text with a max length|
|`BOOLEAN`|flags|`TRUE`/`FALSE` only|
|`NUMERIC(p, s)`|money, balances|exact decimal — always use for money, never floating point (`0.1 + 0.2` ≠ `0.3` in floating point)|
|`TIMESTAMP`|created_at, login times|date + time|
|`DATE`|birthdays, join dates|date only|

Example production-style table:

```sql
CREATE TABLE users (
    id            SERIAL          PRIMARY KEY,
    username      VARCHAR(30)     NOT NULL,
    email         TEXT            NOT NULL,
    password_hash TEXT            NOT NULL,
    age           INTEGER,
    balance       NUMERIC(12, 2)  DEFAULT 0.00,
    is_verified   BOOLEAN         DEFAULT FALSE,
    is_deleted    BOOLEAN         DEFAULT FALSE,
    created_at    TIMESTAMP       DEFAULT NOW()
);
```

### Part 2 — Constraints (rules PostgreSQL enforces automatically)

|Constraint|Meaning|Example effect|
|---|---|---|
|`NOT NULL`|column can't be empty|rejects insert with missing value|
|`UNIQUE`|no duplicate values|rejects duplicate email|
|`PRIMARY KEY`|`NOT NULL` + `UNIQUE`, identifies the row|every table needs exactly one|
|`DEFAULT`|auto-fills value if none given|e.g. `DEFAULT NOW()`, `DEFAULT FALSE`|
|`FOREIGN KEY` (`REFERENCES`)|enforces a valid link to another table|prevents "orphan" rows (e.g. order for a non-existent user)|
|`CHECK`|custom validation rule|e.g. `CHECK (age >= 0 AND age <= 120)`|

```sql
CREATE TABLE orders (
    id       SERIAL   PRIMARY KEY,
    user_id  INTEGER  REFERENCES users(id),
    product  TEXT     NOT NULL,
    price    NUMERIC(10, 2) NOT NULL
);
```

### Part 3 — Indexes (where performance begins)

**The problem:** Without an index, finding one row in a 100-million-row table means scanning every row (a "full table scan") — far too slow for production.

**The solution:** An index is a separate sorted lookup structure, like a textbook's index — instead of reading every page, jump straight to the right one.

```sql
CREATE INDEX idx_users_email ON users(email);
```

**When to add an index:** columns frequently used in `WHERE`, `ORDER BY`, or `JOIN ON`.

**Tradeoff:** indexes speed up reads but slow down writes slightly (every `INSERT`/`UPDATE` must also update the index). Rule of thumb: index columns you search/filter/sort by often; don't index everything blindly.

**Automatic indexes:** `PRIMARY KEY` and `UNIQUE` constraints automatically create an index — no manual step needed.

### Part 4 — Full production-style example

```sql
CREATE TABLE users (
    id            SERIAL           PRIMARY KEY,
    username      VARCHAR(30)      NOT NULL UNIQUE,
    email         TEXT             NOT NULL UNIQUE,
    password_hash TEXT             NOT NULL,
    country       TEXT,
    balance       NUMERIC(12, 2)   DEFAULT 0.00 CHECK (balance >= 0),
    is_verified   BOOLEAN          DEFAULT FALSE,
    is_deleted    BOOLEAN          DEFAULT FALSE,
    created_at    TIMESTAMP        DEFAULT NOW()
);

CREATE TABLE orders (
    id          SERIAL          PRIMARY KEY,
    user_id     INTEGER         NOT NULL REFERENCES users(id),
    product     TEXT            NOT NULL,
    price       NUMERIC(10, 2)  NOT NULL CHECK (price > 0),
    status      TEXT            DEFAULT 'pending',
    ordered_at  TIMESTAMP       DEFAULT NOW()
);

CREATE INDEX idx_orders_user_id    ON orders(user_id);
CREATE INDEX idx_orders_ordered_at ON orders(ordered_at);
CREATE INDEX idx_users_country     ON users(country);
```

### Lesson 3 Summary

|Concept|What it does|Why it matters|
|---|---|---|
|Data Types|defines what kind of data a column holds|correctness and efficiency|
|`NOT NULL`|prevents empty values|data integrity|
|`UNIQUE`|prevents duplicates|e.g. no duplicate emails|
|`PRIMARY KEY`|unique row identifier|every table needs one|
|`FOREIGN KEY`|enforces links between tables|prevents orphan data|
|`DEFAULT`|auto-fills value if none given|cleaner inserts|
|`CHECK`|custom validation rule|business logic in the DB|
|`INDEX`|lookup shortcut for fast queries|makes big tables fast|

**Homework:** Created `users`/`orders` with full constraints; deliberately triggered constraint-violation errors (missing email, duplicate username, negative price, invalid `user_id`); inserted valid data; wrote a "total spent per user" query; added a custom column.

---

### Side discussion — "Is PostgreSQL just SQL, or do you code it like an app/API?"

**Clarified mental model:**

```
Your App = A Restaurant

PostgreSQL  = The kitchen (stores and manages data)
Python/JS   = The chef (writes the logic)
Your API    = The waiter (talks to users, talks to kitchen)
The User    = The customer (never sees the kitchen directly)
```

- PostgreSQL only stores and serves data via SQL — it doesn't handle HTTP requests or build UI.
- A real app needs a backend language (e.g. Python) to send SQL to PostgreSQL and return results to users.

**Python ↔ PostgreSQL example (`psycopg2`):**

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="myapp",
    user="postgres",
    password="yourpassword"
)
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE email = %s", ('aryan@gmail.com',))
user = cursor.fetchone()
print(user)
```

**What's an API?** A controlled "door" into the database for the outside world, e.g. with FastAPI:

```python
from fastapi import FastAPI
import psycopg2

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()
```

**Supabase vs Neon vs raw PostgreSQL:**

```
PostgreSQL = just the database engine (raw, runs on a server)

Supabase = PostgreSQL + dashboard + auto-generated API
           + authentication + file storage + realtime
           = "Firebase but with real SQL"

Neon      = PostgreSQL + cloud hosting + auto scaling
           + branching (like Git branches for your database!)
           = "PostgreSQL in the cloud, managed for you"
```

**Final clarified answer to "do you code PostgreSQL from scratch?":**

- PostgreSQL is pre-built software (like Chrome or VS Code) — you install it (or use Supabase/Neon) and only ever talk to it using **SQL**.
- No Python or JavaScript runs inside PostgreSQL itself; no UI is built in PostgreSQL.
- On Supabase/Neon, you just open their dashboard's SQL editor and write SQL — exactly like db-fiddle, but for a real live hosted database.

**Suggested learning order:**

```
Step 1: Learn SQL + PostgreSQL deeply        ← in progress
Step 2: Learn Python + psycopg2 to connect DB to code
Step 3: Learn FastAPI to build real APIs
Step 4: Use Supabase/Neon to host everything in the cloud
Step 5: Scale to millions of users
```

---

## Lesson 4 — Transactions & Data Safety

### The problem transactions solve

Bank transfer example: subtracting ₹1000 from Aryan and adding ₹1000 to Sara are two separate steps. If the server crashes between them, money can vanish — Aryan loses money, Sara never receives it.

### What is a transaction?

A **transaction** groups multiple steps into one unit: either **all** succeed together, or **none** happen at all.

```sql
BEGIN;    -- start a group of steps

-- your SQL steps go here

COMMIT;   -- everything worked, save permanently
-- OR
ROLLBACK; -- something went wrong, undo everything
```

**Bank transfer example:**

```sql
BEGIN;

    UPDATE accounts SET balance = balance - 1000 
    WHERE user_id = 1;  -- subtract from Aryan

    UPDATE accounts SET balance = balance + 1000 
    WHERE user_id = 2;  -- add to Sara

COMMIT;
```

If anything fails, PostgreSQL automatically rolls back — as if nothing happened.

**Manual `ROLLBACK` example:**

```sql
BEGIN;
    UPDATE accounts SET balance = balance - 1000 WHERE user_id = 1;
    -- realize Aryan only has ₹500 — not enough!
ROLLBACK;  -- undo everything
```

### ACID — the four guarantees

|Letter|Meaning|Plain explanation|
|---|---|---|
|**A**tomicity|all or nothing|a transfer can't be "half done" — either both updates happen or neither does|
|**C**onsistency|rules always enforced|constraints (e.g. balance ≥ 0) hold even mid-transaction; DB moves between valid states only|
|**I**solation|transactions don't interfere|concurrent transactions (e.g. 1M simultaneous users) behave as if each runs alone, preventing race conditions like double-spending|
|**D**urability|committed data survives crashes|once `COMMIT` runs, data is safe even if the server crashes a second later (via the Write-Ahead Log, WAL)|

**Isolation race-condition example (what goes wrong without it):**

```
Transaction A reads Aryan's balance → ₹1000
Transaction B reads Aryan's balance → ₹1000 (same time, stale read)
Transaction A subtracts ₹600 → saves ₹400
Transaction B subtracts ₹800 → saves ₹200 (didn't see A's change!)
Aryan effectively spent ₹1400 from a ₹1000 balance — corruption.
```

### Savepoints — checkpoints inside a transaction

Like a manual save point in a video game — roll back to a checkpoint instead of undoing everything.

```sql
BEGIN;
    UPDATE accounts SET balance = balance - 1000 WHERE user_id = 1;
    SAVEPOINT step1_done;
    UPDATE accounts SET balance = balance + 1000 WHERE user_id = 2;
    -- something wrong with step 2
    ROLLBACK TO step1_done;
    UPDATE accounts SET balance = balance + 1000 WHERE user_id = 3;
COMMIT;
```

### Transactions in Python

```python
import psycopg2

conn = psycopg2.connect(...)

try:
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET balance = balance - 1000 WHERE user_id = 1")
    cursor.execute("UPDATE accounts SET balance = balance + 1000 WHERE user_id = 2")
    conn.commit()   # everything worked — save it
    print("Transfer successful!")
except Exception as error:
    conn.rollback() # something failed — undo everything
    print("Transfer failed, nothing changed:", error)
```

`try/except` maps directly to `COMMIT`/`ROLLBACK`.

### Real-world example — user registration as a transaction

```sql
BEGIN;
    INSERT INTO users (username, email)
    VALUES ('Aryan', 'aryan@gmail.com');

    INSERT INTO wallets (user_id, balance)
    VALUES (currval('users_id_seq'), 0.00);

    INSERT INTO notifications (user_id, message)
    VALUES (currval('users_id_seq'), 'Welcome to the app!');
COMMIT;
```

All three inserts succeed together or not at all — never a user without a wallet.

### Lesson 4 Summary

|Concept|Meaning|Simple way to remember|
|---|---|---|
|Transaction|group of steps treated as one unit|all or nothing|
|`COMMIT`|save everything permanently|"I'm sure, save it"|
|`ROLLBACK`|undo everything|"something went wrong, cancel"|
|`SAVEPOINT`|checkpoint inside a transaction|manual save in a video game|
|Atomicity|all steps or no steps|can't be half done|
|Consistency|rules always enforced|database always valid|
|Isolation|transactions don't interfere|each one runs alone|
|Durability|committed data survives crashes|saved forever|

**Homework:**

```sql
CREATE TABLE accounts (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL,
    balance NUMERIC(10,2) CHECK (balance >= 0)
);

INSERT INTO accounts (name, balance) VALUES
('Aryan', 1000.00),
('Sara',  500.00);
```

1. Write a successful transfer of ₹200 from Aryan to Sara, checking balances before/after.
2. Attempt an over-limit transfer (₹2000 from Sara) and observe the `CHECK` constraint protecting her balance.
3. Reflect in plain English on why a hospital would need ACID guarantees.

---

## Database Log — Full Topic Reference

|Lesson|Concepts|
|---|---|
|1 — Databases & CRUD|tables, rows, columns, `CREATE`, `INSERT`, `SELECT`, `UPDATE`, `DELETE`|
|2 — Sorting, Aggregates, Joins|`ORDER BY`, `LIMIT`, `OFFSET`, `COUNT`/`SUM`/`AVG`/`MAX`/`MIN`, `GROUP BY`, `HAVING`, `INNER JOIN`, `LEFT JOIN`, query execution order|
|3 — PostgreSQL Internals|data types, `NOT NULL`, `UNIQUE`, `PRIMARY KEY`, `FOREIGN KEY`, `DEFAULT`, `CHECK`, indexes, Supabase/Neon vs raw PostgreSQL|
|4 — Transactions|`BEGIN`/`COMMIT`/`ROLLBACK`, `SAVEPOINT`, ACID (Atomicity, Consistency, Isolation, Durability)|
|5 (next)|Query performance & `EXPLAIN ANALYZE`|

**Upcoming:** Lesson 5 — Query Performance & `EXPLAIN ANALYZE`: looking inside PostgreSQL's query planner, diagnosing slow queries, and fixing them — daily work for senior engineers at companies like Google and Amazon.