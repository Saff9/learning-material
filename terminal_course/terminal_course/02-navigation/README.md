# Module 2: Navigating the File System

## Introduction

Welcome back! Now that you know what a terminal is and how to open it, it's time to learn how to **move around** your computer's files and folders using only text commands.

Think of your computer's file system like a big city. You need to know:
- Where you are (`pwd`)
- How to look around (`ls`)
- How to move to different places (`cd`)
- How the streets are organized (the directory tree)

---

## Understanding the File System Tree

Your computer organizes files in a **hierarchical tree structure**:

```
/
├── home/
│   ├── username/
│   │   ├── Documents/
│   │   ├── Downloads/
│   │   ├── Desktop/
│   │   ├── Pictures/
│   │   └── Music/
│   └── anotheruser/
├── etc/
├── var/
├── usr/
└── tmp/
```

- `/` is the **root** — the top of everything
- `home/` contains user folders
- Each user has their own space
- Folders inside folders create the tree

---

## The `pwd` Command — Where Am I?

`pwd` stands for **Print Working Directory**. It tells you your current location in the file system.

```bash
pwd
```

Example output:
```
/home/yourname
```

This is like a GPS showing your exact coordinates!

---

## The `ls` Command — What's Around Me?

`ls` stands for **List**. It shows the contents of your current directory.

```bash
ls
```

Example output:
```
Desktop  Documents  Downloads  Music  Pictures  Videos
```

### Useful `ls` Options (Flags)

You can modify how `ls` works by adding **options** (also called flags or arguments):

| Command | What It Shows |
|---------|--------------|
| `ls -l` | Detailed list with permissions, sizes, dates |
| `ls -a` | Show ALL files, including hidden ones (starting with `.`) |
| `ls -la` | Both detailed AND hidden files |
| `ls -lh` | Detailed list with human-readable file sizes (KB, MB, GB) |
| `ls -ltr` | Detailed, sorted by time, reversed (newest at bottom) |
| `ls -R` | Recursive — shows subdirectories too |

Try them all! Here's what `ls -la` might show:

```bash
ls -la
```

```
drwxr-xr-x  5 user user 4096 Jul 21 10:00 .
drwxr-xr-x  3 root root 4096 Jul 20 09:00 ..
-rw-r--r--  1 user user  220 Jul 20 09:00 .bash_logout
-rw-r--r--  1 user user 3771 Jul 20 09:00 .bashrc
-rw-r--r--  1 user user  898 Jul 20 09:00 .profile
drwxr-xr-x  2 user user 4096 Jul 21 10:00 Desktop
drwxr-xr-x  2 user user 4096 Jul 21 10:00 Documents
```

> 🔍 **Notice**: Files starting with `.` (like `.bashrc`) are **hidden files**. They're configuration files and are hidden to keep your view clean.

### Understanding `ls -l` Output

```
-rw-r--r--  1 user user  898 Jul 20 09:00 .profile
││││││││││  │  │    │    │   │    │    │
││││││││││  │  │    │    │   │    │    └── Filename
││││││││││  │  │    │    │   │    └─────── Time
││││││││││  │  │    │    │   └──────────── Date
││││││││││  │  │    │    └──────────────── Size in bytes
││││││││││  │  │    └───────────────────── Group
││││││││││  │  └────────────────────────── Owner
││││││││││  └───────────────────────────── Number of links
│││││││││└──────────────────────────────── Others permissions
│││││││└───────────────────────────────── Group permissions
││││││└────────────────────────────────── Owner permissions
│││││└─────────────────────────────────── File type (- = file, d = directory)
└──────────────────────────────────────── Not used here
```

Don't worry about permissions yet — we'll cover that in Module 5!

---

## The `cd` Command — Moving Around

`cd` stands for **Change Directory**. This is how you move between folders.

### Absolute vs. Relative Paths

**Absolute path**: Starts from root (`/`). It's the full address.
```bash
cd /home/yourname/Documents
```

**Relative path**: Starts from where you are now.
```bash
cd Documents
```

### Special Directory Symbols

| Symbol | Meaning |
|--------|---------|
| `.` | Current directory (where you are now) |
| `..` | Parent directory (one level up) |
| `~` | Your home directory (shortcut for `/home/yourname`) |
| `-` | Previous directory (where you were before) |
| `/` | Root directory (the very top) |

### Common `cd` Examples

```bash
cd Documents          # Go into Documents folder
cd ..                # Go up one level
cd ../..             # Go up two levels
cd ~                 # Go to home directory
cd                   # Also goes to home (shorthand!)
cd /                 # Go to root directory
cd -                 # Go back to where you were
cd ~/Downloads       # Go to Downloads from anywhere
cd ./Desktop         # Go to Desktop in current dir (./ is optional)
```

> 💡 **Pro Tip**: If you type `cd` with no arguments, it always takes you home. This is super useful!

---

## Practice: Navigating Your Computer

Let's do a navigation exercise together:

```bash
# Step 1: Where are we?
pwd

# Step 2: What's here?
ls

# Step 3: Let's go to Documents
cd Documents

# Step 4: Where are we now?
pwd

# Step 5: What's in Documents?
ls

# Step 6: Go back home
cd ~

# Step 7: Or just
cd

# Step 8: Go to root
cd /

# Step 9: List root contents
ls

# Step 10: Go back home
cd ~
```

---

## Creating Directories with `mkdir`

`mkdir` = **Make Directory**

```bash
mkdir myfolder
```

Create multiple directories at once:
```bash
mkdir folder1 folder2 folder3
```

Create nested directories (parent directories too):
```bash
mkdir -p projects/website/images
```

The `-p` flag means "create parent directories if they don't exist."

---

## Removing Empty Directories with `rmdir`

```bash
rmdir myfolder
```

> ⚠️ **Warning**: `rmdir` only works on **empty** directories!

---

## The `tree` Command (If Installed)

Some systems have a `tree` command that shows a nice visual tree:

```bash
tree
```

If you don't have it, you can install it:
```bash
# Ubuntu/Debian
sudo apt install tree

# macOS
brew install tree
```

---

## Practice Exercises 🎯

### Exercise 1: The Navigation Challenge
1. Open your terminal
2. Check where you are with `pwd`
3. List your home directory contents with `ls -la`
4. Navigate to your Documents folder
5. Create a new folder called `terminal-practice`
6. Navigate into it
7. Create three more folders: `notes`, `scripts`, `projects`
8. List them with `ls`
9. Go back to your home directory
10. Go back to `terminal-practice` using the absolute path

### Exercise 2: The Dot-Dot Dance
1. Go to your home directory
2. Navigate to `Documents/terminal-practice/notes`
3. Go up one level (you should be in `terminal-practice`)
4. Go up another level (you should be in `Documents`)
5. Go back to `notes` using a relative path
6. Go to your home directory in one command
7. Go back to where you just were using `cd -`

### Exercise 3: Hidden Files Hunt
1. Go to your home directory
2. List all files including hidden ones
3. How many hidden files do you see?
4. Look at the `.bashrc` file (we'll learn more about it later!)

---

## Common Mistakes & How to Fix Them

| Mistake | What Happens | Fix |
|---------|-------------|-----|
| `cd my folder` (with space) | Error: "too many arguments" | Use quotes: `cd "my folder"` or escape: `cd my\ folder` |
| `cd MyFolder` (wrong case) | "No such file or directory" | Use correct case: `cd myfolder` |
| `cd /home` then `ls` as normal user | Some directories need admin rights | Use `sudo` or navigate elsewhere |
| Forgetting `..` vs `.` | Confusion about where you are | Remember: `.` = here, `..` = up |

---

## Key Takeaways

- ✅ `pwd` shows your current location
- ✅ `ls` lists directory contents; use `-la` for details and hidden files
- ✅ `cd` changes directories; `~` is home, `..` is up, `-` is back
- ✅ Paths can be absolute (from `/`) or relative (from current location)
- ✅ `mkdir` creates folders; `rmdir` removes empty ones
- ✅ The file system is a tree starting at `/`

---

## Next Up

In **Module 3**, we'll learn how to **create, copy, move, and delete files** — the essential file management skills every terminal user needs!

> 📝 **Homework**: Create a folder structure like this in your home directory:
> ```
> ~/learning/
> ├── terminal/
> │   ├── notes/
> │   └── exercises/
> └── programming/
>     └── python/
> ```
> Use only `mkdir` and `cd` commands!
