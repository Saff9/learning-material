# Module 10: Shell Scripting

## Introduction

This is where the real magic happens! 🎩✨

A **shell script** is a text file containing multiple terminal commands that can be executed together. Instead of typing the same commands over and over, you write them once in a script and run it whenever you need.

Think of it like a recipe — you write down the steps once, then follow the recipe every time you want to make the dish.

---

## Your First Script

### Step 1: Create the File

```bash
nano hello.sh
```

### Step 2: Write the Script

Every shell script starts with a **shebang** (`#!`) that tells the system which interpreter to use:

```bash
#!/bin/bash

# This is a comment — the shell ignores it
echo "Hello, World!"
echo "Today is $(date)"
echo "You are logged in as: $(whoami)"
```

### Step 3: Make It Executable

```bash
chmod +x hello.sh
```

### Step 4: Run It!

```bash
./hello.sh
```

> 💡 **Why `./`?** The shell only looks for executables in directories listed in your `PATH`. To run a script in the current directory, you must specify `./` (current directory).

---

## Script Structure

```bash
#!/bin/bash                      # Shebang — tells system to use bash

# Script: backup.sh
# Author: Your Name
# Description: Backs up important files
# Date: 2024-07-21

# Variables
SOURCE="~/Documents"
DEST="~/Backups"
DATE=$(date +%Y%m%d)

# Main code
echo "Starting backup..."
# ... commands here ...
echo "Backup complete!"
```

---

## Variables

### Creating Variables

```bash
#!/bin/bash

NAME="Alice"
AGE=18
PI=3.14159
IS_STUDENT=true

# No spaces around = !
# CORRECT: NAME="Alice"
# WRONG:   NAME = "Alice"
```

### Using Variables

Use `$` to access a variable:

```bash
#!/bin/bash

NAME="Alice"
echo "Hello, $NAME!"
echo "Hello, ${NAME}!"    # Curly braces are useful for clarity
```

### Special Variables

| Variable | Meaning |
|----------|---------|
| `$0` | Script name |
| `$1`, `$2`, ... | Command line arguments |
| `$#` | Number of arguments |
| `$@` | All arguments (as separate strings) |
| `$*` | All arguments (as one string) |
| `$?` | Exit status of last command |
| `$$` | Process ID of current script |
| `$!` | Process ID of last background command |

### Example with Arguments

```bash
#!/bin/bash

echo "Script name: $0"
echo "First argument: $1"
echo "Second argument: $2"
echo "Total arguments: $#"
echo "All arguments: $@"
```

Run it:
```bash
./myscript.sh hello world 123
```

Output:
```
Script name: ./myscript.sh
First argument: hello
Second argument: world
Total arguments: 3
All arguments: hello world 123
```

---

## User Input

### `read` — Get Input from User

```bash
#!/bin/bash

echo "What's your name?"
read NAME

echo "How old are you?"
read AGE

echo "Hello, $NAME! You are $AGE years old."
```

### `read` with Prompt

```bash
#!/bin/bash

read -p "Enter your name: " NAME
read -sp "Enter password: " PASSWORD    # -s = silent (hidden input)
echo

echo "Hello, $NAME!"
```

### `read` with Timeout

```bash
read -t 5 -p "Answer within 5 seconds: " ANSWER
```

---

## Conditionals (if/else)

### Basic if Statement

```bash
#!/bin/bash

if [ "$NAME" == "Alice" ]; then
    echo "Hello, Alice!"
fi
```

### if/else

```bash
#!/bin/bash

if [ "$AGE" -ge 18 ]; then
    echo "You are an adult."
else
    echo "You are a minor."
fi
```

### if/elif/else

```bash
#!/bin/bash

if [ "$AGE" -lt 13 ]; then
    echo "You are a child."
elif [ "$AGE" -lt 20 ]; then
    echo "You are a teenager."
else
    echo "You are an adult."
fi
```

### Test Operators

**String comparisons:**

| Operator | Meaning |
|----------|---------|
| `=` or `==` | Equal |
| `!=` | Not equal |
| `-z` | Empty string |
| `-n` | Non-empty string |

**Numeric comparisons:**

| Operator | Meaning |
|----------|---------|
| `-eq` | Equal |
| `-ne` | Not equal |
| `-gt` | Greater than |
| `-ge` | Greater than or equal |
| `-lt` | Less than |
| `-le` | Less than or equal |

**File tests:**

| Operator | Meaning |
|----------|---------|
| `-e` | File exists |
| `-f` | File exists and is regular file |
| `-d` | Directory exists |
| `-r` | File is readable |
| `-w` | File is writable |
| `-x` | File is executable |
| `-s` | File is not empty |

### Using `[[ ]]` (Modern, Recommended)

```bash
#!/bin/bash

if [[ "$NAME" == "Alice" ]]; then
    echo "Hello, Alice!"
fi

if [[ "$NAME" == "A"* ]]; then     # Pattern matching!
    echo "Your name starts with A"
fi

if [[ "$AGE" -gt 18 && "$AGE" -lt 30 ]]; then
    echo "You are in your 20s"
fi
```

`[[ ]]` is better than `[ ]` because:
- No need to quote variables
- Supports `&&` and `||` inside
- Supports pattern matching (`*` and `?`)
- Safer with empty strings

---

## Loops

### `for` Loop

```bash
#!/bin/bash

# Loop through numbers
for i in 1 2 3 4 5; do
    echo "Number: $i"
done

# Loop through range
for i in {1..5}; do
    echo "Number: $i"
done

# Loop through files
for file in *.txt; do
    echo "Processing: $file"
done

# C-style for loop
for ((i=0; i<5; i++)); do
    echo "Index: $i"
done
```

### `while` Loop

```bash
#!/bin/bash

COUNTER=1
while [ $COUNTER -le 5 ]; do
    echo "Counter: $COUNTER"
    COUNTER=$((COUNTER + 1))
done

# Read file line by line
while read line; do
    echo "Line: $line"
done < myfile.txt

# Infinite loop (use Ctrl+C to stop)
while true; do
    echo "Running..."
    sleep 1
done
```

### `until` Loop

```bash
#!/bin/bash

COUNTER=1
until [ $COUNTER -gt 5 ]; do
    echo "Counter: $COUNTER"
    COUNTER=$((COUNTER + 1))
done
```

### `break` and `continue`

```bash
#!/bin/bash

for i in {1..10}; do
    if [ $i -eq 5 ]; then
        continue    # Skip 5
    fi
    if [ $i -eq 8 ]; then
        break       # Stop at 8
    fi
    echo "Number: $i"
done
```

---

## Case Statements

```bash
#!/bin/bash

echo "Choose an option:"
echo "1) Start"
echo "2) Stop"
echo "3) Restart"
read -p "Enter choice: " CHOICE

case $CHOICE in
    1)
        echo "Starting..."
        ;;
    2)
        echo "Stopping..."
        ;;
    3)
        echo "Restarting..."
        ;;
    *)
        echo "Invalid choice!"
        ;;
esac
```

---

## Functions

```bash
#!/bin/bash

# Define a function
greet() {
    echo "Hello, $1!"
    echo "You are $2 years old."
}

# Call the function
greet "Alice" 18
greet "Bob" 20

# Function with return value
add() {
    local a=$1      # local variable
    local b=$2
    echo $((a + b)) # Return via echo
}

RESULT=$(add 5 3)
echo "5 + 3 = $RESULT"
```

> 💡 **Important**: Bash functions can only return integers (0-255) with `return`. To return strings or larger numbers, use `echo` and capture with `$()`.

---

## Arrays

```bash
#!/bin/bash

# Declare array
FRUITS=("apple" "banana" "cherry" "date")

# Access elements
echo "First fruit: ${FRUITS[0]}"
echo "All fruits: ${FRUITS[@]}"
echo "Number of fruits: ${#FRUITS[@]}"

# Loop through array
for fruit in "${FRUITS[@]}"; do
    echo "Fruit: $fruit"
done

# Add element
FRUITS+=("elderberry")

# Remove element
unset FRUITS[1]    # Remove banana
```

---

## Arithmetic

```bash
#!/bin/bash

A=5
B=3

# Using $(( ))
SUM=$((A + B))
DIFF=$((A - B))
PROD=$((A * B))
QUOT=$((A / B))      # Integer division
MOD=$((A % B))       # Modulo

# Using expr (older style)
SUM=$(expr $A + $B)

# Using let
let RESULT=A+B

# Increment/decrement
((A++))              # A = A + 1
((B--))              # B = B - 1
```

---

## Useful Scripting Techniques

### Exit Status

```bash
#!/bin/bash

mkdir newfolder
if [ $? -eq 0 ]; then
    echo "Directory created successfully"
else
    echo "Failed to create directory"
fi
```

Every command returns an exit status:
- `0` = success
- Non-zero = error

## Best Practices & Robust Scripts

Writing scripts that just "work" is easy. Writing scripts that are safe, predictable, and maintainable takes a bit more effort.

### 1. The Unofficial Bash Strict Mode

Always start your robust scripts with this:

```bash
#!/bin/bash
set -euo pipefail
IFS=$'\n\t'
```

- `set -e`: Exit immediately if any command returns a non-zero status.
- `set -u`: Exit if an undefined variable is used (prevents destructive commands like `rm -rf /$UNDEFINED_VAR`).
- `set -o pipefail`: Ensure that if any command in a pipeline fails, the whole pipeline fails, rather than just returning the exit status of the last command.
- `IFS=$'\n\t'`: Makes loops split only on newlines and tabs, not spaces, preventing weird issues with filenames containing spaces.

### 2. Robust Argument Parsing (`while` / `case`)

For more complex scripts, positional parameters (`$1`, `$2`) aren't enough. Use a `while` loop with a `case` statement to parse flags:

```bash
#!/bin/bash
set -euo pipefail

VERBOSE=0
FILE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -v|--verbose)
      VERBOSE=1
      shift # past argument
      ;;
    -f|--file)
      FILE="$2"
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

echo "Verbose mode: $VERBOSE"
echo "File: $FILE"
```

### 3. Bulletproof Error Handling & Traps

```bash
#!/bin/bash
set -euo pipefail

# Create a temporary directory
TEMP_DIR=$(mktemp -d)

# Cleanup function
cleanup() {
    echo "Cleaning up..."
    rm -rf "$TEMP_DIR"
}

# Run cleanup on script exit, interruption, or termination
trap cleanup EXIT INT TERM

echo "Working in $TEMP_DIR..."
# If this script fails or the user presses Ctrl+C, cleanup STILL runs!
```

### 4. Logging and Error Functions

Instead of just `echo`, define helper functions:

```bash
log_info() {
    echo "[INFO] $(date +'%Y-%m-%d %H:%M:%S') - $*"
}

log_error() {
    echo "[ERROR] $(date +'%Y-%m-%d %H:%M:%S') - $*" >&2
}

die() {
    log_error "$*"
    exit 1
}

# Usage:
log_info "Starting backup..."
cp important.txt backup.txt || die "Failed to copy file!"
```

---

## Practice Exercises 🎯

### Exercise 1: Your First Real Script
Create a script called `system-info.sh` that shows:
- Current date and time
- Your username
- Your hostname
- Current directory
- Number of files in current directory

### Exercise 2: Backup Script
Create a script called `backup.sh` that:
- Takes a directory name as argument
- Creates a tar.gz backup with timestamp
- Shows progress messages
- Checks if the directory exists first

```bash
#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

DIR=$1
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP="backup_${DIR}_${DATE}.tar.gz"

if [ ! -d "$DIR" ]; then
    echo "Error: $DIR is not a directory"
    exit 1
fi

echo "Creating backup: $BACKUP"
tar -czf "$BACKUP" "$DIR"
echo "Backup complete!"
```

### Exercise 3: Interactive Menu Script
Create a script with a menu that:
- Shows options: 1) List files 2) Show disk usage 3) Show memory 4) Exit
- Uses a `while` loop to keep showing the menu
- Uses `case` for handling choices

### Exercise 4: File Processor
Create a script that:
- Loops through all `.txt` files in a directory
- Counts lines in each file
- Reports total lines across all files
- Skips empty files

---

## Key Takeaways

- ✅ Scripts start with `#!/bin/bash` (the shebang)
- ✅ Make scripts executable with `chmod +x`
- ✅ Variables use `$` to access: `$NAME` or `${NAME}`
- ✅ `read` gets user input; `$1`, `$2`, etc. are command-line arguments
- ✅ `if [ condition ]; then ... fi` for conditionals
- ✅ `for`, `while`, `until` for loops
- ✅ `case` for multiple choice menus
- ✅ Functions group reusable code
- ✅ `set -euxo pipefail` makes scripts safer
- ✅ `trap` handles cleanup on exit

---

## Next Up

In **Module 11**, we'll explore **advanced topics** — environment variables, aliases, custom prompts, package management, and more tips to make you a terminal power user!

> 📝 **Homework**: 
> 1. Write a script that greets you by name
> 2. Write a script that backs up a folder
> 3. Write a script with a menu system
> 4. Make your scripts executable and add them to your PATH
