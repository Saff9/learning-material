# Module 3: File Management — Creating, Copying, Moving & Deleting

## Introduction

Now that you can navigate around like a pro, it's time to learn how to **work with files**. In this module, we'll cover everything you need to create, copy, move, rename, and delete files and directories.

> ⚠️ **Important Warning**: The terminal doesn't have a "Recycle Bin" or "Trash" by default. When you delete something, it's usually **gone forever**. Be careful, especially when using wildcards and recursive commands!

---

## Creating Files

### 1. `touch` — Create an Empty File

```bash
touch myfile.txt
```

This creates an empty file called `myfile.txt` in your current directory.

Create multiple files at once:
```bash
touch file1.txt file2.txt file3.txt
```

> 💡 **Fun Fact**: `touch` actually updates the "last modified" time of a file. If the file doesn't exist, it creates it. That's why it's called "touch"!

### 2. `echo` — Create a File with Content

```bash
echo "Hello, World!" > hello.txt
```

The `>` symbol **redirects** the output of `echo` into a file. We'll learn more about redirection in Module 7.

Add more content (append):
```bash
echo "This is a new line" >> hello.txt
```

`>>` appends (adds to the end), while `>` overwrites (replaces everything).

### 3. `cat` with Redirection

```bash
cat > myfile.txt
```

Type your content, then press `Ctrl + D` to save and exit.

---

## Viewing File Contents

### 1. `cat` — Concatenate and Display

```bash
cat myfile.txt
```

Shows the entire contents of a file. Great for small files.

### 2. `less` — View Page by Page

```bash
less myfile.txt
```

Shows one screen at a time. Perfect for large files!

**Navigation in `less`:**
- `Space` or `Page Down` — Next page
- `Page Up` or `b` — Previous page
- `↑` / `↓` — Line by line
- `/word` — Search for "word"
- `n` — Next search result
- `q` — Quit

### 3. `head` — View the Beginning

```bash
head myfile.txt        # First 10 lines
head -n 5 myfile.txt   # First 5 lines
```

### 4. `tail` — View the End

```bash
tail myfile.txt        # Last 10 lines
tail -n 5 myfile.txt   # Last 5 lines
tail -f myfile.txt     # Follow (watch for changes in real-time!)
```

`tail -f` is incredibly useful for watching log files!

### 5. `nl` — Number the Lines

```bash
nl myfile.txt
```

Shows the file with line numbers. Great for code!

---

## Copying Files and Directories (`cp`)

### Copy a File

```bash
cp source.txt destination.txt
```

### Copy to a Directory

```bash
cp myfile.txt ~/Documents/
```

### Copy and Rename at the Same Time

```bash
cp oldname.txt ~/Documents/newname.txt
```

### Copy Multiple Files

```bash
cp file1.txt file2.txt file3.txt ~/backup/
```

### Copy a Directory (Recursive)

```bash
cp -r myfolder ~/backup/
```

The `-r` flag means **recursive** — copy the folder and everything inside it.

### Useful `cp` Options

| Option | Meaning |
|--------|---------|
| `-r` | Recursive (for directories) |
| `-i` | Interactive (ask before overwriting) |
| `-v` | Verbose (show what's being copied) |
| `-p` | Preserve permissions and timestamps |
| `-u` | Update (only copy if source is newer) |

Example with multiple options:
```bash
cp -riv myfolder ~/backup/
```

---

## Moving and Renaming (`mv`)

In the terminal, **moving and renaming are the same operation**!

### Rename a File

```bash
mv oldname.txt newname.txt
```

### Move a File to Another Directory

```bash
mv myfile.txt ~/Documents/
```

### Move and Rename at the Same Time

```bash
mv oldname.txt ~/Documents/newname.txt
```

### Move a Directory

```bash
mv myfolder ~/backup/
```

### Useful `mv` Options

| Option | Meaning |
|--------|---------|
| `-i` | Interactive (ask before overwriting) |
| `-v` | Verbose (show what's being moved) |
| `-f` | Force (don't ask, just do it) |

---

## Deleting Files and Directories (`rm`)

> ⚠️ **DANGER ZONE**: `rm` is permanent. There is no undo. Be very careful!

### Delete a File

```bash
rm myfile.txt
```

### Delete Multiple Files

```bash
rm file1.txt file2.txt file3.txt
```

### Delete a Directory (and everything inside!)

```bash
rm -r myfolder/
```

### Force Delete (No Warnings)

```bash
rm -f myfile.txt
```

### The Nuclear Option: Delete Everything

```bash
rm -rf myfolder/
```

> ☠️ **NEVER RUN**: `rm -rf /` — This deletes your entire system. Don't do it. Ever.

### Safe Deletion with `rm -i`

```bash
rm -i myfile.txt
```

This asks you "remove regular file 'myfile.txt'?" before deleting. Type `y` for yes, `n` for no.

### Useful `rm` Options

| Option | Meaning |
|--------|---------|
| `-r` | Recursive (for directories) |
| `-f` | Force (no warnings) |
| `-i` | Interactive (ask before each deletion) |
| `-v` | Verbose (show what's being deleted) |

---

## Wildcards (Globbing)

Wildcards let you work with multiple files at once using patterns.

| Wildcard | Meaning | Example |
|----------|---------|---------|
| `*` | Any characters (zero or more) | `*.txt` matches all .txt files |
| `?` | Any single character | `file?.txt` matches file1.txt, fileA.txt |
| `[abc]` | Any character in brackets | `file[123].txt` matches file1.txt, file2.txt, file3.txt |
| `[a-z]` | Any character in range | `file[a-z].txt` matches filea.txt through filez.txt |
| `{a,b,c}` | Any of the options | `file.{txt,md,log}` matches file.txt, file.md, file.log |

### Wildcard Examples

```bash
ls *.txt              # All .txt files
ls file?.txt          # file1.txt, file2.txt, etc. (not file10.txt)
ls file[0-9].txt      # file0.txt through file9.txt
ls *.{txt,md}         # All .txt and .md files
rm *.tmp              # Delete all .tmp files
cp *.jpg ~/Pictures/  # Copy all .jpg files to Pictures
```

> 💡 **Pro Tip**: Before using wildcards with `rm`, test with `ls` first! Run `ls *.txt` to see what matches, then `rm *.txt` to delete.

---

## Finding File Information

### `file` — What Type of File Is This?

```bash
file myfile.txt
```

Output might be:
```
myfile.txt: ASCII text
```

### `wc` — Word Count (and Line Count, Byte Count)

```bash
wc myfile.txt        # Lines, words, bytes
wc -l myfile.txt     # Lines only
wc -w myfile.txt     # Words only
wc -c myfile.txt     # Bytes only
```

### `du` — Disk Usage

```bash
du myfile.txt        # Size in blocks
du -h myfile.txt     # Human-readable size
du -sh myfolder/     # Total size of directory
```

### `stat` — Detailed File Information

```bash
stat myfile.txt
```

Shows creation time, modification time, access time, size, permissions, and more.

---

## Practice Exercises 🎯

### Exercise 1: File Creation Playground
1. Navigate to your `~/learning/terminal/exercises` folder
2. Create a file called `hello.txt` with `touch`
3. Add "Hello, Terminal!" to it using `echo`
4. View it with `cat`
5. Add "This is my second line" using `>>`
6. View it again with `cat`
7. Count the lines with `wc -l`

### Exercise 2: Copy and Move Practice
1. Copy `hello.txt` to `hello-copy.txt`
2. Move `hello-copy.txt` to `~/learning/terminal/notes/`
3. Rename it to `backup-hello.txt`
4. Check that it's there with `ls`
5. Copy it back to `exercises/` as `returned.txt`

### Exercise 3: Wildcard Challenge
1. Create 5 files: `note1.txt`, `note2.txt`, `note3.txt`, `todo.txt`, `readme.md`
2. List only the `note` files using a wildcard
3. Copy all `.txt` files to a new folder called `txt-backup` (create it first!)
4. Delete all files starting with `note` using a wildcard
5. Verify with `ls`

### Exercise 4: The Dangerous Delete (BE CAREFUL!)
1. Create a folder called `test-delete`
2. Create 3 files inside it
3. Create a subfolder inside it with 2 more files
4. Delete the entire `test-delete` folder and everything in it
5. Verify it's gone

> ⚠️ **Double-check** your command before pressing Enter!

---

## Key Takeaways

- ✅ `touch` creates empty files; `echo` creates files with content
- ✅ `cat`, `less`, `head`, `tail`, `nl` view file contents in different ways
- ✅ `cp` copies files/directories; use `-r` for directories
- ✅ `mv` moves AND renames files
- ✅ `rm` deletes files; `rm -r` deletes directories; **be careful!**
- ✅ Wildcards (`*`, `?`, `[]`, `{}`) let you work with multiple files
- ✅ `wc`, `du`, `file`, `stat` give you file information

---

## Next Up

In **Module 4**, we'll learn about **text editors** — how to create and edit files directly in the terminal using powerful tools like `nano` and `vim`. This is where you start feeling like a real hacker! 😎

> 📝 **Homework**: 
> 1. Create 10 text files in your exercises folder using `touch`
> 2. Write a short story in one file using `echo` and `>>`
> 3. Practice copying, moving, and renaming files
> 4. Use `ls -la` to see how file sizes and timestamps change
