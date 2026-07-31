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
gcc -Wall -Wextra -std=c11 -o hello hello.c
```

**Flag breakdown:**
- `gcc`: The GNU C Compiler
- `-Wall`: Enable **all** warnings (treat warnings as errors in your mind)
- `-Wextra`: Enable extra warnings not covered by `-Wall`
- `-std=c11`: Use the C11 standard (published 2011, widely supported, modern but stable)
- `-o hello`: Name the output executable `hello`
- `hello.c`: Your source file

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

**Why is this necessary?**
In Python, `print()` is a built-in function — it's always available. In C, `printf()` is just a regular function defined in the C Standard Library. The compiler needs to know:
1. What arguments `printf` takes
2. What type it returns
3. Where to find its implementation (handled by the linker)

The file `stdio.h` (standard input/output header) contains **function declarations** (also called prototypes) for I/O functions. Without it, the compiler would see `printf(...)` and say: "I don't know what `printf` is."

### `int main(void)` — The Entry Point

Every C program starts execution at `main`. This is non-negotiable.

- `int`: `main` returns an integer to the operating system. By convention:
  - `0` means "success"
  - Non-zero means "some error occurred"
- `void`: Explicitly states that `main` takes no command-line arguments. You can also write `int main(int argc, char *argv[])` to accept arguments.

**Why return 0?**
In shell scripting, you check a program's exit status with `$?`. A C program's return value from `main` becomes this exit status:
```bash
./hello
echo $?   # Prints 0
```

### `printf("Hello, World!\n");` — Formatted Output

`printf` is a **variadic function** — it can take a variable number of arguments. Its first argument is always a format string.

**Key difference from Python's `print()`:**
- Python: `print("Hello", name, "you are", age, "years old")`
- C: `printf("Hello %s, you are %d years old\n", name, age);`

C requires **format specifiers**:
| Specifier | Type | Example |
|-----------|------|---------|
| `%d` or `%i` | `int` | `printf("%d", 42);` |
| `%f` | `float` / `double` | `printf("%f", 3.14);` |
| `%c` | `char` | `printf("%c", 'A');` |
| `%s` | `char *` (string) | `printf("%s", "hello");` |
| `%p` | pointer | `printf("%p", ptr);` |
| `%zu` | `size_t` | `printf("%zu", sizeof(int));` |
| `%%` | literal `%` | `printf("100%%");` |

**Precision and width:**
```c
printf("[%10d]\n", 42);     // [        42] — right-aligned in 10 spaces
printf("[%-10d]\n", 42);    // [42        ] — left-aligned
printf("[%.2f]\n", 3.14159); // [3.14] — 2 decimal places
```

### `\n` — The Newline Character

Unlike Python's `print()`, C's `printf()` does NOT automatically add a newline. You must include `\n` explicitly. Without it:
```c
printf("Hello");
printf("World");
// Output: HelloWorld (on the same line!)
```

## Compilation Variations

### Separate Compilation
For larger projects, compile files separately:
```bash
gcc -c math.c        # Produces math.o
gcc -c main.c        # Produces main.o
gcc math.o main.o -o program   # Links them together
```

### Debug Build
```bash
gcc -g -O0 -o program program.c
```
- `-g`: Include debug symbols (for gdb)
- `-O0`: No optimization (easier to debug)

### Release Build
```bash
gcc -O3 -o program program.c
```
- `-O3`: Maximum optimization (can make debugging confusing)

## Common Compiler Errors and What They Mean

| Error Message | Meaning | Fix |
|---------------|---------|-----|
| `implicit declaration of function` | Missing `#include` or function prototype | Add the correct header |
| `expected ';' before '}'` | Missing semicolon | Add `;` |
| `undefined reference to 'printf'` | Missing library during linking | Usually means missing `#include` |
| `segmentation fault` | Accessing invalid memory | Check pointers and array bounds |

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

### Problem 1.2: ASCII Art Box
Write a program that prints a box using ASCII characters:
```
+--------+
|        |
|        |
+--------+
```

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    printf("+--------+\n");
    printf("|        |\n");
    printf("|        |\n");
    printf("+--------+\n");
    return 0;
}
```
</details>

### Problem 1.3: Formatting Practice
Write a program that prints a table of squares and cubes for numbers 1 through 5, nicely aligned:
```
Number  Square  Cube
     1       1     1
     2       4     8
     3       9    27
     4      16    64
     5      25   125
```

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    printf("%-7s %-7s %-7s\n", "Number", "Square", "Cube");
    for (int i = 1; i <= 5; i++) {
        printf("%-7d %-7d %-7d\n", i, i * i, i * i * i);
    }
    return 0;
}
```
</details>

### Problem 1.4: Explore the Preprocessor
Create a file with `#define PI 3.14159` and use it in a program. Then compile with `gcc -E` to see the preprocessed output. What happens to `PI`?

---

> **Professor's Note**: Master the compilation process. Understanding that C is compiled, not interpreted, explains why many errors are caught at compile time rather than runtime. The compiler is your first line of defense — always compile with `-Wall -Wextra`.
