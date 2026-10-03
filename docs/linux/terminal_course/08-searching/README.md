# Module 8: Finding Files & Searching Content

## Introduction

One of the most common tasks in the terminal is **finding things** — files you misplaced, text inside files, or specific patterns. In this module, you'll become a search master!

We'll cover:
- `find` — Find files by name, size, date, type
- `grep` — Search inside files
- `locate` — Fast file finding (if available)
- `which` and `whereis` — Find program locations
- `awk` and `sed` — Advanced text searching

---

## `find` — The Ultimate File Finder

`find` searches through directories recursively. It's incredibly powerful!

### Basic Syntax

```bash
find [where] [what] [action]
```

### Find by Name

```bash
find . -name "*.txt"           # Find all .txt files in current directory and below
find . -iname "*.txt"          # Case-insensitive search
find /home -name "document*"    # Find files starting with "document"
find . -name "*.log" -type f  # Only files (not directories)
```

### Find by Type

```bash
find . -type f                 # Find only files
find . -type d                 # Find only directories
find . -type l                 # Find only symbolic links
```

### Find by Size

```bash
find . -size +100M             # Files larger than 100MB
find . -size -1k               # Files smaller than 1KB
find . -size 10M               # Files exactly 10MB
find . -size +1G -size -5G    # Files between 1GB and 5GB
```

Size suffixes: `c` (bytes), `k` (KB), `M` (MB), `G` (GB)

### Find by Time

```bash
find . -mtime -7               # Modified in last 7 days
find . -mtime +30              # Modified more than 30 days ago
find . -atime -1               # Accessed in last day
find . -ctime -7               # Changed (metadata) in last 7 days
find . -mmin -60               # Modified in last 60 minutes
```

### Find by Permissions

```bash
find . -perm 644               # Exact permission match
find . -perm /u=s              # SetUID files
find . -perm -111              # Executable by anyone
```

### Find by Owner

```bash
find . -user username          # Owned by specific user
find . -group developers       # Owned by specific group
```

### Find Empty Files/Directories

```bash
find . -empty                  # Empty files and directories
find . -type f -empty          # Only empty files
find . -type d -empty          # Only empty directories
```

### Actions — What to Do With Found Files

```bash
find . -name "*.tmp" -delete           # Delete found files
find . -name "*.log" -ls               # List found files (like ls -l)
find . -name "*.txt" -exec cat {} \;   # Run cat on each file
find . -name "*.txt" -exec cat {} +    # More efficient version
find . -name "*.old" -exec rm {} \;   # Delete with confirmation
```

> 💡 **The `{}` and `\;`**: `{}` is replaced with each found filename. `\;` marks the end of the `-exec` command. On some systems you can use `+` instead of `\;` for better performance.

### Combining Conditions

```bash
find . -name "*.txt" -and -size +1k     # Both conditions
find . -name "*.tmp" -or -name "*.bak"   # Either condition
find . -not -name "*.txt"               # Negation
find . \! -name "*.txt"                 # Same as -not
```

### Practical Examples

```bash
# Find and delete old log files
find /var/log -name "*.log" -mtime +30 -delete

# Find large files eating up disk space
find /home -size +100M -exec ls -lh {} \;

# Find recently modified files
find . -mtime -1 -type f | sort

# Find duplicate files (by name, then verify with md5)
find . -type f -exec md5sum {} + | sort

# Find all Python files and count lines
find . -name "*.py" -exec wc -l {} + | tail -n 1
```

### Advanced `find` + `xargs` Tricks

While `-exec` is great, pairing `find` with `xargs` can be faster and more flexible. 

**Wait, what is `xargs`?**
It takes input from stdin and converts it into arguments for another command.

```bash
# Faster deletion of many files
find . -name "*.tmp" | xargs rm

# The problem with spaces:
# If a filename is "my file.txt", the above command runs `rm my file.txt` (two files!)

# The safe way to use xargs (using null characters):
find . -name "*.tmp" -print0 | xargs -0 rm

# Search for text ONLY in specific files (fast!)
find . -name "*.js" -print0 | xargs -0 grep "console.log"

# Find files and copy them to a directory
find . -name "*.jpg" -print0 | xargs -0 -I {} cp {} /backup/images/
```

---

## `grep` — Search Inside Files

`grep` searches for text patterns inside files. It's one of the most-used terminal commands!

### Basic Usage

```bash
grep "search term" file.txt
grep "hello" *.txt              # Search in all .txt files
grep -r "hello" .               # Recursive search in all files
grep -i "hello" file.txt        # Case-insensitive
grep -n "hello" file.txt        # Show line numbers
grep -v "hello" file.txt        # Invert (show lines that DON'T match)
grep -c "hello" file.txt        # Count matching lines
```

### Regular Expressions

`grep` supports regular expressions for powerful pattern matching:

```bash
grep "^hello" file.txt          # Lines starting with "hello"
grep "world$" file.txt          # Lines ending with "world"
grep "h.llo" file.txt           # Matches hello, hallo, hullo (any char)
grep "h*llo" file.txt           # Matches llo, hllo, hhllo, etc.
grep "colou\?r" file.txt        # Optional character (color or colour)
grep "[aeiou]" file.txt         # Any vowel
grep "[0-9]" file.txt           # Any digit
grep "\(hello\|hi\)" file.txt  # hello OR hi
```

### Extended Regex with `egrep` or `grep -E`

```bash
grep -E "hello|hi" file.txt     # hello OR hi (simpler syntax)
grep -E "[0-9]{3}-[0-9]{4}"     # Phone number pattern: 123-4567
grep -E "\bword\b" file.txt    # Whole word only
```

### Context Lines

```bash
grep -C 3 "error" log.txt       # Show 3 lines of context around matches
grep -B 2 "error" log.txt       # Show 2 lines BEFORE matches
grep -A 2 "error" log.txt       # Show 2 lines AFTER matches
```

### Only Filenames

```bash
grep -l "search" *.txt          # Only show filenames that contain match
grep -L "search" *.txt          # Only show filenames that DON'T contain match
```

### Count in Multiple Files

```bash
grep -c "TODO" *.py             # Count TODOs in each Python file
```

### `grep` with Pipes

```bash
ps aux | grep firefox           # Find firefox in processes
history | grep "git commit"     # Find git commits in history
cat log.txt | grep ERROR | grep -v "DEBUG"  # Find ERRORs but not DEBUG
```

### `zgrep` — Search in Compressed Files

```bash
zgrep "error" log.txt.gz        # Search inside .gz files without extracting
```

---

## `locate` — Fast File Finding

`locate` is much faster than `find` because it uses a pre-built database.

```bash
locate filename                 # Find files by name anywhere on system
locate "*.conf"                 # Find all .conf files
locate -i "readme"              # Case-insensitive
locate -n 10 "*.log"            # Limit to 10 results
```

> ⚠️ **Important**: The database is updated periodically (usually daily). New files might not appear immediately!

Update the database manually:
```bash
sudo updatedb
```

Install if not available:
```bash
sudo apt install mlocate    # Ubuntu/Debian
```

---

## `which` and `whereis` — Find Programs

### `which` — Find Executable Path

```bash
which python          # Where is the python command?
which -a python       # All locations (if multiple)
which ls              # Where is ls?
```

### `whereis` — Find Binary, Source, and Man Pages

```bash
whereis python        # Find python binary, source, and man page
whereis -b python     # Only binary
whereis -m python     # Only man page
```

---

## `awk` — Advanced Text Processing

`awk` is a full programming language for text processing!

### Basic Usage

```bash
awk '{print $1}' file.txt       # Print first column
awk '{print $1, $3}' file.txt   # Print first and third columns
awk -F',' '{print $2}' file.csv # Use comma as delimiter
```

### With `ps` Output

```bash
ps aux | awk '{print $1, $2, $11}'   # User, PID, and command
ps aux | awk '$3 > 50 {print $2}'    # PIDs using >50% CPU
```

### Calculations

```bash
awk '{sum += $1} END {print sum}' numbers.txt   # Sum of first column
```

---

## `sed` — Stream Editor

`sed` performs text transformations on a stream.

### Search and Replace

```bash
sed 's/old/new/' file.txt       # Replace first occurrence per line
sed 's/old/new/g' file.txt      # Replace all occurrences
sed 's/old/new/2' file.txt      # Replace second occurrence only
sed 's/old/new/gi' file.txt     # Global, case-insensitive
```

### In-Place Editing

```bash
sed -i 's/old/new/g' file.txt   # Edit file in place
sed -i.bak 's/old/new/g' file.txt  # Create backup first
```

### Delete Lines

```bash
sed '2d' file.txt               # Delete line 2
sed '/pattern/d' file.txt        # Delete lines matching pattern
sed '1,5d' file.txt             # Delete lines 1-5
```

### Print Specific Lines

```bash
sed -n '5p' file.txt            # Print only line 5
sed -n '10,20p' file.txt        # Print lines 10-20
```

---

## Practice Exercises 🎯

### Exercise 1: Find Mastery
1. Find all `.txt` files in your home directory
2. Find all files modified in the last 24 hours
3. Find all empty directories
4. Find files larger than 1MB
5. Find all files owned by your user in `/tmp`

### Exercise 2: grep Challenge
1. Create a file with 20 lines of text (use a here document)
2. Search for a specific word
3. Count how many lines contain that word
4. Show lines that DON'T contain that word
5. Search case-insensitively
6. Show line numbers with matches

### Exercise 3: Log Analysis Project
Create a fake server log:
```bash
cat > server.log << 'EOF'
2024-07-21 10:00:01 INFO Server started
2024-07-21 10:00:05 ERROR Connection failed: timeout
2024-07-21 10:00:10 INFO User login: admin
2024-07-21 10:00:15 ERROR Database connection lost
2024-07-21 10:00:20 WARNING Disk space low: 85%
2024-07-21 10:00:25 INFO Backup completed
2024-07-21 10:00:30 ERROR File not found: config.ini
2024-07-21 10:00:35 INFO Server shutting down
EOF
```

Then:
1. Count total lines
2. Count ERROR lines
3. Extract just the timestamps from ERROR lines
4. Find all lines with "INFO" or "WARNING"
5. Show the line before each ERROR

### Exercise 4: System Exploration
1. Find where `python` is installed: `which python`
2. Find all man pages for `ls`: `whereis -m ls`
3. Find all `.conf` files on your system with `locate`
4. Find the 5 largest files in your home directory

---

## Key Takeaways

- ✅ `find` searches by name, type, size, time, permissions, owner
- ✅ `find -exec` runs commands on found files
- ✅ `grep` searches inside files; supports regex and many options
- ✅ `locate` is fast but uses a database (may be outdated)
- ✅ `which` finds program executables; `whereis` finds binaries, source, man pages
- ✅ `awk` processes columns of text data
- ✅ `sed` performs search/replace and line operations

---

## Next Up

In **Module 9**, we'll explore **networking commands** — how to check your internet connection, download files, test servers, and understand how your computer talks to the world!

> 📝 **Homework**: 
> 1. Use `find` to locate all files you created this week
> 2. Use `grep` to search for a word in all files in a directory
> 3. Try `awk` to extract columns from `ps aux` output
> 4. Experiment with `sed` to replace text in a file
