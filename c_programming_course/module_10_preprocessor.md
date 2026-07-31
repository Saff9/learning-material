# Module 10: The Preprocessor & Modular Programming

## The Preprocessor

Before the compiler sees your code, a separate program called the **preprocessor** runs. It handles all lines starting with `#`.

```
Source Code → [Preprocessor] → Preprocessed Code → [Compiler] → Object Code
```

## `#include` — File Inclusion

```c
#include <stdio.h>   // System header (searches system directories)
#include "myheader.h" // User header (searches current directory first)
```

**What it does:** The preprocessor literally copies the entire contents of the header file and pastes it where the `#include` line is.

**Why headers?**
- Declarations shared across multiple source files
- Interface definitions (what functions exist, not how they work)
- Type definitions (structs, enums, typedefs)

## `#define` — Macro Definition

### Simple Constants
```c
#define PI 3.14159
#define MAX_BUFFER_SIZE 1024
#define DEBUG 1
```

The preprocessor replaces every occurrence of `PI` with `3.14159` before compilation. No type checking, no memory allocation.

### Function-like Macros
```c
#define SQUARE(x) ((x) * (x))
#define MAX(a, b) ((a) > (b) ? (a) : (b))
```

**Parentheses are CRITICAL:**
```c
#define BAD_SQUARE(x) x * x
int result = BAD_SQUARE(3 + 2);  // Expands to: 3 + 2 * 3 + 2 = 11 (not 25!)

#define GOOD_SQUARE(x) ((x) * (x))
int result = GOOD_SQUARE(3 + 2);  // Expands to: ((3 + 2) * (3 + 2)) = 25
```

### Multi-line Macros
```c
#define SWAP(a, b) do {     typeof(a) temp = a;     a = b;     b = temp; } while(0)
```

The `do { ... } while(0)` idiom ensures the macro behaves like a single statement even in contexts like `if`.

### Macro Pitfalls

```c
#define MAX(a, b) ((a) > (b) ? (a) : (b))

int x = 5, y = 3;
int m = MAX(x++, y++);  // x++ is evaluated TWICE! x becomes 7, not 6
```

**Prefer inline functions over complex macros** (C99 `inline` keyword).

## Conditional Compilation

### `#ifdef`, `#ifndef`, `#endif`
```c
#ifdef DEBUG
    printf("Debug: x = %d\n", x);
#endif
```

Compile with: `gcc -DDEBUG program.c` (defines DEBUG macro)

### `#if`, `#elif`, `#else`
```c
#if PLATFORM == LINUX
    #include <linux.h>
#elif PLATFORM == WINDOWS
    #include <windows.h>
#else
    #error "Unsupported platform"
#endif
```

## Include Guards

When a header is included in multiple files, you get **duplicate declarations** — compile errors!

**Solution: Include Guards**
```c
// math_utils.h
#ifndef MATH_UTILS_H
#define MATH_UTILS_H

// Declarations go here
int add(int a, int b);
int factorial(int n);

#endif // MATH_UTILS_H
```

**How it works:**
1. First inclusion: `MATH_UTILS_H` is not defined, so define it and process the content
2. Second inclusion: `MATH_UTILS_H` IS defined, so skip everything

**Modern alternative:** `#pragma once` (widely supported but not standard C)
```c
#pragma once
// Declarations...
```

## Splitting Code Across Files

### The Header File (`math_utils.h`) — The Interface
```c
#ifndef MATH_UTILS_H
#define MATH_UTILS_H

// Function declarations (prototypes)
int add(int a, int b);
int subtract(int a, int b);
int factorial(int n);

// Type definitions
typedef struct {
    double real;
    double imag;
} Complex;

// Constants
#define PI 3.14159265359

#endif
```

### The Source File (`math_utils.c`) — The Implementation
```c
#include "math_utils.h"

int add(int a, int b)
{
    return a + b;
}

int subtract(int a, int b)
{
    return a - b;
}

int factorial(int n)
{
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
```

### The Main File (`main.c`) — The Client
```c
#include <stdio.h>
#include "math_utils.h"

int main(void)
{
    printf("5 + 3 = %d\n", add(5, 3));
    printf("5! = %d\n", factorial(5));
    return 0;
}
```

### Compilation
```bash
# Compile each source file separately
gcc -c -Wall math_utils.c   # Produces math_utils.o
gcc -c -Wall main.c         # Produces main.o

# Link them together
gcc math_utils.o main.o -o program

# Or in one command:
gcc -Wall -o program main.c math_utils.c
```

## The `static` Keyword on Functions

```c
// In math_utils.c
static int helper_function(int x)
{
    // Only visible within this file
    return x * 2;
}
```

This creates **internal linkage** — the function cannot be called from other source files. This is C's way of creating private functions.

## The `extern` Keyword

```c
// In file1.c
int global_counter = 0;  // Definition

// In file2.c
extern int global_counter;  // Declaration (says "this exists elsewhere")
```

**Best practice:** Put `extern` declarations in headers, definitions in one source file.

## Practice Problems

### Problem 10.1: Create a Header File
Create a header file `geometry.h` with circle and rectangle functions, then implement them in `geometry.c` and use them in `main.c`.

<details>
<summary>Solution</summary>

**geometry.h:**
```c
#ifndef GEOMETRY_H
#define GEOMETRY_H

#define PI 3.14159265359

double circle_area(double radius);
double circle_circumference(double radius);
double rectangle_area(double width, double height);

#endif
```

**geometry.c:**
```c
#include "geometry.h"

double circle_area(double radius)
{
    return PI * radius * radius;
}

double circle_circumference(double radius)
{
    return 2 * PI * radius;
}

double rectangle_area(double width, double height)
{
    return width * height;
}
```

**main.c:**
```c
#include <stdio.h>
#include "geometry.h"

int main(void)
{
    printf("Circle area (r=5): %.2f\n", circle_area(5.0));
    printf("Rectangle area (3x4): %.2f\n", rectangle_area(3.0, 4.0));
    return 0;
}
```

**Compile:** `gcc -o program main.c geometry.c`
</details>

### Problem 10.2: Debug Macro
Create a debug macro that prints file name, line number, and a message only when `DEBUG` is defined.

<details>
<summary>Solution</summary>

```c
#ifndef DEBUG_H
#define DEBUG_H

#ifdef DEBUG
    #define DEBUG_PRINT(msg) printf("[DEBUG %s:%d] %s\n", __FILE__, __LINE__, msg)
#else
    #define DEBUG_PRINT(msg)  // Empty — does nothing
#endif

#endif
```

**Usage:**
```c
#include "debug.h"

int main(void)
{
    DEBUG_PRINT("Starting program");
    int x = 42;
    DEBUG_PRINT("x initialized");
    return 0;
}
```

**Compile with:** `gcc -DDEBUG -o program main.c`
</details>

### Problem 10.3: Platform Detection
Write a header that detects the operating system and defines appropriate macros.

<details>
<summary>Solution</summary>

```c
#ifndef PLATFORM_H
#define PLATFORM_H

#if defined(_WIN32) || defined(_WIN64)
    #define PLATFORM_WINDOWS
    #define PLATFORM_NAME "Windows"
#elif defined(__APPLE__) && defined(__MACH__)
    #define PLATFORM_MACOS
    #define PLATFORM_NAME "macOS"
#elif defined(__linux__)
    #define PLATFORM_LINUX
    #define PLATFORM_NAME "Linux"
#else
    #define PLATFORM_UNKNOWN
    #define PLATFORM_NAME "Unknown"
#endif

#endif
```
</details>

### Problem 10.4: Makefile Basics
Create a simple Makefile for a multi-file project.

<details>
<summary>Solution</summary>

```makefile
CC = gcc
CFLAGS = -Wall -Wextra -std=c11
TARGET = program
SRCS = main.c math_utils.c geometry.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $(TARGET)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
```

**Usage:**
- `make` — builds the project
- `make clean` — removes object files and executable
- Only recompiles files that have changed!
</details>

---

> **Professor's Note**: Modular programming is essential for any serious C project. Headers define the contract (what functions exist), source files implement the contract, and the build system ties everything together. The preprocessor is powerful but dangerous — macros can have subtle bugs. Prefer typed constants (`const`, `enum`) over `#define` when possible, and prefer inline functions over complex macros. Master `make` or `cmake` early — they are as important as the language itself.
