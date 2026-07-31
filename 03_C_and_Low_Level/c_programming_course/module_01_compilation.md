# Module 1: Compilation & Your First Program

## The Complete Compilation Process

When you write Python, you run `python script.py` and the interpreter executes your code line by line. With C, you must **compile** your human-readable source code into machine code that the CPU can execute directly.

### Step-by-Step Compilation

Let's trace exactly what happens when you compile a C program:

```c
// hello.c
#include <stdio.h>

#define GREETING "Hello, World!"

int main(void)
{
    printf("%s\n", GREETING);
    return 0;
}
```

**Step 1: Preprocessing** (`gcc -E hello.c`)
The preprocessor handles all lines starting with `#`:
- `#include <stdio.h>`: Copies the entire contents of `stdio.h` into your file
- `#define GREETING "Hello, World!"`: Replaces all occurrences of `GREETING` with `"Hello, World!"`

The output (`hello.i`) is a single, expanded C file — often thousands of lines long.

**Step 2: Compilation** (`gcc -S hello.i`)
The compiler translates C code into **assembly language** — human-readable (barely) machine instructions specific to your CPU architecture. The output is `hello.s`.

**Step 3: Assembly** (`gcc -c hello.s`)
The assembler converts assembly into **object code** — binary machine instructions. The output is `hello.o`. At this stage, the code is not yet executable because external references (like `printf`) are not resolved.

**Step 4: Linking** (`gcc hello.o -o hello`)
The linker combines your object file with library object files (like the C standard library) to create the final executable. It resolves all external function calls.

### The One-Command Compilation

In practice, you do all steps at once:
```bash
gcc -Wall -Wextra -Werror -pedantic -std=c11 -o hello hello.c
```

**Flag breakdown (Strict GCC Flags):**
- `gcc`: The GNU C Compiler
- `-Wall`: Enable **all** common warnings (treat warnings as errors in your mind)
- `-Wextra`: Enable extra warnings not covered by `-Wall`
- `-Werror`: Treats all warnings as errors, forcing you to fix them before the compilation succeeds. This is essential for production code.
- `-pedantic`: Enforces strict ISO C standard compliance, warning about non-standard extensions.
- `-std=c11`: Use the C11 standard (published 2011, widely supported, modern but stable)
- `-o hello`: Name the output executable `hello`
- `hello.c`: Your source file

## Production-Grade Makefiles

In real-world projects, you don't type `gcc` commands manually. You use a build system like `make`. A `Makefile` automates the compilation process.

Here is a production-grade Makefile example:

```makefile
# Compiler settings
CC = gcc
CFLAGS = -Wall -Wextra -Werror -pedantic -std=c11 -g -O2
LDFLAGS = 

# Directories
SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = bin

# Files
SRCS = $(wildcard $(SRC_DIR)/*.c)
OBJS = $(patsubst $(SRC_DIR)/%.c, $(OBJ_DIR)/%.o, $(SRCS))
TARGET = $(BIN_DIR)/program

# Default rule
all: dirs $(TARGET)

# Create necessary directories
dirs:
	mkdir -p $(OBJ_DIR) $(BIN_DIR)

# Link the final executable
$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $@ $(LDFLAGS)

# Compile source files to object files
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR)

.PHONY: all clean dirs
```

With this Makefile, simply running `make` will incrementally build your project, compiling only the files that have changed. Running `make clean` removes compiled files.

## Your First Program Explained in Depth

```c
#include <stdio.h>

int main(void)
{
    printf("Hello, World!\n");
    return 0;
}
```

### `#include <stdio.h>` — The Preprocessor Directive

This line tells the preprocessor: "Find the file named `stdio.h` and copy its entire contents here." 

### `int main(void)` — The Entry Point

Every C program starts execution at `main`. This is non-negotiable.

### `printf("Hello, World!\n");` — Formatted Output

`printf` is a **variadic function** — it can take a variable number of arguments. Its first argument is always a format string.

### `\n` — The Newline Character

Unlike Python's `print()`, C's `printf()` does NOT automatically add a newline. You must include `\n` explicitly.

## Practice Problems

### Problem 1.1: Hello, You!
Write a program that prints your name and age on separate lines using a single `printf` call.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    printf("Name: John Doe\nAge: 25\n");
    return 0;
}
```
</details>

---

> **Professor's Note**: Master the compilation process and always use strict flags like `-Wall -Wextra -Werror -pedantic`. Automate your build process with Makefiles early on to save time and prevent manual errors.
