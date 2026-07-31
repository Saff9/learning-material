# 01 - Linux Basics

> **Phase:** 1 (Core Linux) · **Time:** ~2‑3 weeks · **Difficulty:** ⭐

## What it is
The **Linux shell** is the command‑line interface (CLI) to the operating system. It lets you **explore files**, **run programs**, **automate tasks**, and **manage the system** without a graphical interface.

**Core Linux basics** = how to navigate the file system, read/write files, work with users, set permissions, and run everyday commands used by developers and sysadmins.

## Why it matters
- **Every dev** uses CLI tools (Git, containers, CI/CD).
- **Productivity:** one‑liner commands replace GUI workflows.
- **Debugging:** error messages, logs, and system status are often CLI‑only.
- **Automation:** shells and scripts are the backbone of DevOps.

## Core concepts — detailed

### 1. Shell vs Terminal
- **Shell:** interpreter that reads your commands (bash, zsh, fish, sh).
- **Terminal:** program that provides an interface to the shell (gnome-terminal, xterm, VS Code terminal, wsl.exe).

### 2. File system hierarchy (Linux trees)
```text
/ (root)
├── bin        — essential user commands (ls, cat, echo)
├── etc        — system configs
├── home       — users’ home directories (/home/you)
├── var        — variable data (logs, downloads)
├── opt        — optional software
├── root       — root user’s home
├── usr/bin    — most user-installed programs
└── proc       — runtime kernel info (pseudo‑FS)
```
- **`pwd`** prints the current path.
- **`ls`** lists directory contents; `-l` adds details, `-a` shows hidden files.

### 3. Working with files and directories
| Command | What it does | Example use case |
|---|---|---|
| `cat file.txt` | display file content | view a script |
| `echo "text" > file.txt` | overwrite | start a new file |
| `echo "text" >> file.txt` | append | log to a file |
| `cp src dst` | copy, recurse with `-r` |
| `mv src dst` | move/rename |
| `rm file` | delete; `-r` for dirs |
| `mkdir dir` | create dir, `-p` makes parents |
| `touch file` | create empty file |

### 4. Permissions & ownership
- **User (u), Group (g), Others (o)** × **Read (r), Write (w), Execute (x)**.
- Symbolic: `chmod u+r file`.
- Numeric: `chmod 644 file` (owner r/w, others r). 
- `chown user:group file`.

> Execute on a **directory** allows entering it (`cd`) and listing contents.

### 5. Common system commands
- **`grep pattern file`* — search text.
- **`sed 's/from/to/g' file`* — stream editor.
- **`awk '/pattern/{print}' file`* — column processing.
- **`tar czvf archive.tar.gz dir`* — compress archive.
- **`ssh user@host`* — remote login.
- **`curl url -o file`* — fetch web content.
- **`rsync -av source/ dest/`* — sync.

### 6. The `$PATH` and environment
- `$PATH` lists directories where shell looks for commands.
- Add a dir: `export PATH=$PATH:/usr/local/sbin`.
- Set a variable: `MYVAR=hello; echo $MYVAR`.
- Shell scripts start with `#!/usr/bin/env bash` (shebang).

## Free resources — curated from public Linux learning sites

1. **Linux The Hard Way** (free ebook, 18 lessons) — hands‑on, learns through practice:
   - https://www.linuxhandbook.com/
2. **GeeksforGeeks — Linux Quick Reference:**
   - https://www.geeksforgeeks.org/linux/ (shell, commands, file ops)
3. **Man Pages** — online: https://man7.org/online.html
4. **OverTheWire ( wargames )** — training in security, command fundamentals:
   - https://overthewire.org/wargames/bandit/
5. **Microsoft Docs — WSL2 Guide:**
   - https://learn.microsoft.com/en-us/windows/wsl/
6. **Red Hat Beginners Guide:**
   - https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/
7. **tldr.sh** — concise command examples (install with `pip install tldr`):
   - https://github.com/tldr-pages/tldr

## Practice labs (run in a local VM, WSL2, or the terminal on any Linux host)

### Lab 1: Shell navigation
```bash
# 1. Show current dir
pwd
# 2. List contents (with details)
ls -la
# 3. Navigate up/down
mkdir /tmp/lab1
cd /tmp/lab1
ls -
# 4. Create a file with echo
echo "Hello from the shell" > greeting.txt
cat greeting.txt
```

### Lab 2: File manipulation
```bash
# Duplicate a config
cp /etc/hosts myhosts.backup
# Add a timestamp
echo "$(date)" >> myhosts.backup
# Remove a file (safety: test with rm -i first)
rm -i readme.txt
```

### Lab 3: Permissions
```bash
# Grant read to others
chmod o+r important.txt
# Show with numbers
ls -l important.txt
# Switch owner
chown myuser:mygroup important.txt
```

### Lab 4: Simple utilities
```bash
# Find a line in a file
grep "error" /var/log/syslog | head -5
# Replace a string in a file
sed -i 's/OLD/NEW/g' script.sh
# Archive a directory
tar -czvf backup.tar.gz /home/user/docs
```

### Lab 5: Environment and scripts
```bash
# Set an env var
export MYVAR=world
echo "Hello $MYVAR"
# Create a simple script
cat > hello.sh << 'EOF'
echo "Hello from $(whoami)"
EOF
chmod +x hello.sh
./hello.sh
```

## Self‑check (can you…)
- [ ] `pwd`, `ls`, `cd`, `mkdir`, `rm` confidently
- [ ] Set and use environment variables
- [ ] Explain permissions: user/group/others × rwx
- [ ] `grep`, `sed`, `tar`, `ssh` safely in a shell
- [ ] Start a script with a shebang and make it executable
- [ ] Navigate the filesystem without errors

## Progress
- [ ] Completed Lab 1‑5 (run commands, understand results)
- [ ] Explained basic concepts (shell vs terminal, fs hierarchy)
- [ ] Custom practice script (one you built) works and is documented
- [ ] Set up a local Linux environment (VM/WSL/containers) for practice

## Link to next module
→ [[02 - Users & Permissions]]
