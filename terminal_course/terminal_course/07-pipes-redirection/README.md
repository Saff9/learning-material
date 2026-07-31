# Module 7: Pipes, Redirection & Command Chaining

## Introduction

This is where the terminal becomes truly magical! 🪄

Pipes and redirection let you:
- Send the output of one command into another
- Save command output to files
- Combine simple commands to do complex things
- Control exactly where data flows

This is one of the most powerful concepts in Unix/Linux — the idea that small, focused tools can be combined to accomplish anything.

---

## Standard Streams

Every command has three standard communication channels:

| Stream | Number | Name | Default Destination |
|--------|--------|------|---------------------|
| **stdin** | 0 | Standard Input | Keyboard |
| **stdout** | 1 | Standard Output | Terminal screen |
| **stderr** | 2 | Standard Error | Terminal screen |

Think of it like plumbing:
- **stdin** = the water pipe coming IN
- **stdout** = the clean water pipe going OUT
- **stderr** = the error/warning pipe going OUT

---

## Output Redirection (`>` and `>>`)

### `>` — Redirect stdout to a File (Overwrite)

```bash
echo "Hello, World!" > hello.txt
```

The output of `echo` goes into `hello.txt` instead of the screen. If the file exists, it's **overwritten**.

### `>>` — Redirect stdout to a File (Append)

```bash
echo "Another line" >> hello.txt
```

Adds to the end of the file without deleting existing content.

### Examples

```bash
ls > files.txt              # Save directory listing to file
cat file1.txt > combined.txt # Copy file1 to combined.txt
cat file2.txt >> combined.txt # Append file2 to combined.txt
date > timestamp.txt         # Save current date to file
```

---

## Input Redirection (`<`)

Send the contents of a file INTO a command:

```bash
sort < unsorted.txt
```

This is the same as:
```bash
sort unsorted.txt
```

But `<` is useful when a command expects input from stdin:

```bash
wc -l < bigfile.txt        # Count lines in file
cat < file.txt             # Same as cat file.txt
```

---

## Error Redirection (`2>`)

Redirect error messages (stderr) to a file:

```bash
ls /nonexistent 2> errors.txt
```

The error message goes to `errors.txt` instead of the screen.

### Redirect Both stdout and stderr

```bash
command > output.txt 2> errors.txt    # Separate files
command > output.txt 2>&1              # Both to same file
command &> output.txt                 # Both to same file (bash 4+)
```

### Discard Output

```bash
command > /dev/null                   # Discard stdout
command 2> /dev/null                  # Discard stderr
command > /dev/null 2>&1              # Discard everything
```

`/dev/null` is a special file that discards anything written to it. It's the "black hole" of Linux!

---

## Pipes (`|`)

The pipe symbol `|` takes the **stdout** of one command and sends it as **stdin** to another command.

```bash
command1 | command2
```

This is the secret sauce of the terminal!

### Simple Pipe Examples

```bash
ls -la | less              # List files, view in less
cat file.txt | wc -l        # Count lines in file
ps aux | grep firefox       # Find firefox process
history | tail -n 10        # Show last 10 commands
```

### Chaining Multiple Pipes

```bash
cat log.txt | grep ERROR | wc -l
# Read log → filter for ERROR → count lines

ps aux | grep python | grep -v grep | awk '{print $2}'
# Find python processes → exclude grep → print PIDs
```

---

## Common Pipe Partners

These commands are designed to work well in pipes:

### `grep` — Filter Lines

```bash
cat file.txt | grep "search term"
grep "search" file.txt          # Same thing, grep can read files directly
```

### `sort` — Sort Lines

```bash
cat names.txt | sort
cat names.txt | sort -r         # Reverse order
cat names.txt | sort | uniq     # Sort and remove duplicates
```

### `uniq` — Remove Duplicate Lines

```bash
sort file.txt | uniq            # Remove duplicates
sort file.txt | uniq -c         # Count occurrences
sort file.txt | uniq -d         # Show only duplicates
```

### `wc` — Word/Line/Character Count

```bash
cat file.txt | wc -l            # Count lines
cat file.txt | wc -w            # Count words
cat file.txt | wc -c            # Count bytes
```

### `head` and `tail` — First/Last Lines

```bash
cat bigfile.txt | head -n 5     # First 5 lines
cat bigfile.txt | tail -n 5     # Last 5 lines
cat bigfile.txt | tail -n +10   # From line 10 to end
```

### `cut` — Extract Columns

```bash
cat data.csv | cut -d',' -f1    # First column (comma-delimited)
cat data.csv | cut -d',' -f1,3  # First and third columns
ps aux | cut -c1-10              # First 10 characters of each line
```

### `awk` — Powerful Text Processing

```bash
ps aux | awk '{print $1, $2}'   # Print first and second columns
ps aux | awk '$3 > 50 {print}'  # Print lines where column 3 > 50
```

### `sed` — Stream Editor

```bash
cat file.txt | sed 's/old/new/g' # Replace all "old" with "new"
cat file.txt | sed '2d'          # Delete line 2
```

### `tr` — Translate Characters

```bash
echo "HELLO" | tr 'A-Z' 'a-z'    # Convert to lowercase
echo "hello world" | tr ' ' '-'  # Replace spaces with dashes
```

---

## Command Chaining

### `;` — Run Commands Sequentially

```bash
cd Documents; ls; cd ~
```

Runs each command one after another, regardless of success.

### `&&` — Run Next Only If Previous Succeeded

```bash
mkdir newfolder && cd newfolder && touch file.txt
```

If `mkdir` fails, the rest won't run. Great for dependent operations!

### `||` — Run Next Only If Previous Failed

```bash
mkdir newfolder || echo "Failed to create folder"
```

If `mkdir` fails, the echo runs. Good for error handling!

### Combining Them

```bash
command1 && command2 || command3
# If 1 succeeds, run 2. If 1 fails, run 3.
```

---

## Command Substitution

Use the output of one command as an argument to another:

### Backticks (Old Style)
```bash
echo "Today is $(date)"
```

### `$()` (Modern Style — Preferred)
```bash
echo "Today is $(date)"
files=$(ls)
echo "Files: $files"
cd $(dirname "$0")           # Go to script's directory
```

---

## Here Documents and Here Strings

### Here Document (`<<`)

Send multiple lines of text to a command:

```bash
cat << EOF
This is line 1
This is line 2
This is line 3
EOF
```

Great for creating files with multiple lines:

```bash
cat > config.txt << EOF
name=John
age=25
city=New York
EOF
```

### Here String (`<<<`)

Send a single string to a command:

```bash
wc -w <<< "Hello world this is a test"
```

---

## Tee — Split Output

`tee` sends output to both the screen AND a file:

```bash
ls -la | tee output.txt           # Show on screen AND save to file
ls -la | tee -a output.txt        # Append to file instead of overwrite
echo "config" | sudo tee /etc/config.txt   # Write to file with sudo
```

---

## Xargs — Build Commands from Input

`xargs` takes input and uses it as arguments to another command:

```bash
find . -name "*.txt" | xargs rm        # Delete all .txt files
find . -name "*.log" | xargs wc -l     # Count lines in all .log files
echo "file1 file2 file3" | xargs touch  # Create multiple files
```

With `-I` for more control:
```bash
ls *.txt | xargs -I {} cp {} backup/   # Copy each .txt to backup/
```

---

## Practice Exercises 🎯

### Exercise 1: Redirection Basics
1. Create a file with `echo`: `echo "Line 1" > test.txt`
2. Append to it: `echo "Line 2" >> test.txt`
3. View it with `cat`
4. Overwrite it: `echo "Only line" > test.txt`
5. View it again — what happened?

### Exercise 2: Pipe Power
1. List all files: `ls -la`
2. Now pipe to `wc -l`: `ls -la | wc -l`
3. Find how many files are in `/usr/bin`: `ls /usr/bin | wc -l`
4. Find all files with "bash" in the name: `ls /usr/bin | grep bash`

### Exercise 3: Log Analysis
1. Create a fake log file:
   ```bash
   cat > fake.log << EOF
   ERROR: Something broke
   INFO: All good
   ERROR: Another problem
   WARNING: Be careful
   ERROR: Critical failure
   INFO: Process complete
   EOF
   ```
2. Count how many ERROR lines: `grep ERROR fake.log | wc -l`
3. Extract just the error messages: `grep ERROR fake.log | cut -d':' -f2`
4. Sort and count unique error types

### Exercise 4: Command Chaining
1. Create a folder, enter it, and create a file — all in one line:
   ```bash
   mkdir test-chain && cd test-chain && touch success.txt
   ```
2. Try to create a folder that already exists and handle the error:
   ```bash
   mkdir test-chain || echo "Folder already exists!"
   ```

### Exercise 5: Process Pipeline
1. Find all running processes
2. Filter for your username
3. Sort by CPU usage
4. Show only the top 5

```bash
ps aux | grep $(whoami) | sort -k3 -nr | head -n 5
```

---

## Key Takeaways

- ✅ `>` overwrites a file with stdout; `>>` appends
- ✅ `<` sends file contents to a command's stdin
- ✅ `2>` redirects stderr; `2>&1` redirects both stdout and stderr
- ✅ `|` pipes stdout of one command to stdin of another
- ✅ `;` runs commands in sequence; `&&` runs if previous succeeded; `||` runs if previous failed
- ✅ `$(command)` inserts command output as text
- ✅ `tee` shows output AND saves to file
- ✅ `xargs` builds commands from piped input

---

## Next Up

In **Module 8**, we'll learn about **searching** — finding files, searching inside files, and using powerful tools like `find` and `grep` to locate anything on your system!

> 📝 **Homework**: 
> 1. Create a text file with 10 lines using a here document
> 2. Practice piping `ls` through `grep`, `sort`, `wc`, and `head`
> 3. Try to chain 3+ commands with pipes
> 4. Experiment with `>` vs `>>` and see the difference
