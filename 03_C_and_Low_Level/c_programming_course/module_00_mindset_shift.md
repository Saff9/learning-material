# Module 0: The Mindset Shift

## Welcome, Student

You have completed **CS50P** and are fluent in Python. Now you are entering the world of C — the language that powers operating systems, embedded devices, databases, and virtually every piece of critical infrastructure on Earth.

## The Fundamental Difference: Python vs. C

### Python's World View
In Python, everything is an **object**. Variables are **names** that **refer to** objects in memory. Python handles memory allocation and deallocation automatically through garbage collection. Types are checked at runtime.

```python
x = 5        # x is a name referring to an int object
y = x        # y now refers to the SAME object
x = "hello"  # x now refers to a string object — no problem!
```

### C's World View
In C, a variable is a **named location in memory** that **contains** a value. You must tell the compiler exactly how much memory to reserve, what type of data will live there, and (usually) when to free that memory.

```c
int x = 5;   // Reserve 4 bytes, label them 'x', store binary 5
int y = x;   // Reserve 4 MORE bytes, label them 'y', COPY the value 5
// x = "hello";  // ERROR! x is forever an int in this scope
```

## The Machine Model

Imagine your computer's RAM as a **giant array of bytes**, indexed from 0 to several billion. Every byte has an **address** (its index number). A C program is essentially a set of instructions to manipulate these bytes directly.

```
Memory Address:  1000  1001  1002  1003  1004  1005  1006  1007
Value:           0000  0000  0000  0000  0000  0000  0000  0000
                 ↑
                 Address 1000
```

When you write `int x = 5;`, the compiler:
1. Finds 4 contiguous free bytes (say, addresses 1000-1003)
2. Labels this block as `x` in the symbol table
3. Writes the binary representation of 5 into those 4 bytes

## Why C Requires This Honesty

C was designed in 1972 by Dennis Ritchie at Bell Labs. Its goal was to provide **low-level access to memory** while being **portable across different hardware architectures**. This design philosophy means:

- **No hidden costs**: You see every memory allocation
- **No magic**: The compiler does exactly what you tell it
- **Direct hardware access**: You can manipulate individual bits, addresses, and CPU registers
- **Predictable performance**: No garbage collector pausing your program

## The Compilation Pipeline

Unlike Python (interpreted), C is **compiled**. This means your source code goes through several transformations before becoming an executable:

```
hello.c → [Preprocessor] → hello.i → [Compiler] → hello.s → [Assembler] → hello.o → [Linker] → hello
```

1. **Preprocessing**: Handles `#include`, `#define`, macros
2. **Compilation**: Translates C to assembly language
3. **Assembly**: Translates assembly to machine code (binary object file)
4. **Linking**: Combines your object files with library code (like `printf`)

## Your New Toolkit

| Tool | Purpose | Python Equivalent |
|------|---------|-------------------|
| `gcc` or `clang` | Compiler | CPython interpreter |
| `gdb` | Debugger | `pdb` |
| `valgrind` | Memory leak detector | None (GC handles this) |
| `make` | Build automation | None needed |

## Common Pitfalls for Python Programmers

1. **Forgetting semicolons**: Every statement ends with `;`
2. **Integer division**: `5 / 2` equals `2`, not `2.5`
3. **Array bounds**: C does NOT check if you're accessing valid indices
4. **String handling**: Strings are NOT objects — they're null-terminated byte arrays
5. **Memory leaks**: Every `malloc` needs a `free`

## Practice: Your First C Program

Before moving to Module 1, type and compile this:

```c
#include <stdio.h>

int main(void)
{
    printf("Hello from C!\n");
    printf("An int is %zu bytes\n", sizeof(int));
    printf("A pointer is %zu bytes\n", sizeof(void *));
    return 0;
}
```

Compile with:
```bash
gcc -Wall -Wextra -std=c11 -o hello hello.c
./hello
```

**Study the output.** The sizes may differ based on your system (32-bit vs 64-bit). This is your first lesson in C's close relationship with hardware.

---

> **Professor's Note**: Do not rush through this module. The mental model shift from Python to C is the biggest hurdle. Once you truly understand that variables are memory boxes, not name tags, everything else becomes logical.
