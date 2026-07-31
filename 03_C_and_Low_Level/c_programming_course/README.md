# Complete C Programming Course — From Pythonist to Systems Programmer

**For students who have completed CS50P and want to master C.**

## Course Structure

### Foundation (Start Here)
| Module | Topic | Why It Matters |
|--------|-------|----------------|
| 00 | Mindset Shift | Python vs C mental model |
| 01 | Compilation | How C becomes machine code |
| 02 | Data Types | Static typing, sizes, overflow |
| 03 | Control Flow | if, switch, loops |
| 04 | Functions | Pass-by-value, recursion, scope |
| 05 | Arrays & Strings | Contiguous memory, null terminators |
| 06 | Pointers | The core concept of C |
| 07 | Memory Management | Stack vs heap, malloc/free |
| 08 | Structures & Unions | Composite data types |
| 09 | File I/O | Text and binary files |
| 10 | Preprocessor & Modular Programming | Headers, macros, make |

### Advanced
| Module | Topic | Why It Matters |
|--------|-------|----------------|
| 11 | Advanced Pointers | Function pointers, void*, ** |
| 12 | Data Structures | Linked lists, stacks, queues, trees |
| 13 | Advanced Topics | Bitwise, threads, modern C |
| 14 | Debugging & Best Practices | GDB, valgrind, coding standards |
| 15 | Final Projects | 4 capstone ideas |
| 16 | Appendix | Cheat sheet, tools, books |

### Standard Library Deep Dive (Most Used)
| Module | Topic | Key Functions |
|--------|-------|---------------|
| 17 | `<stdlib.h>` | malloc, strtol, qsort, rand, getenv |
| 18 | `<string.h>` | strcpy, strcmp, strstr, strtok, memcpy |
| 19 | `<ctype.h>`, `<math.h>`, `<time.h>`, `<errno.h>`, `<assert.h>`, `<limits.h>` | isalpha, sin, time, strerror, assert, INT_MAX |
| 20 | Advanced `<stdio.h>` | printf formats, scanf safety, binary I/O |
| 21 | Practical Patterns | RAII, opaque pointers, state machines, callbacks |

## How to Use This Course

1. **Start at Module 00** — Read it twice. The mindset shift is everything.
2. **Type every example** — Don't copy-paste. Muscle memory matters.
3. **Do ALL practice problems** — Solutions are hidden behind `<details>` tags.
4. **Compile with warnings:** `gcc -Wall -Wextra -Werror -std=c11`
5. **Use valgrind** for any program with `malloc`
6. **Work through to Module 21** — Then pick a final project from Module 15

## Recommended Tools

| Tool | Purpose | Install |
|------|---------|---------|
| `gcc` or `clang` | Compiler | Usually pre-installed |
| `gdb` | Debugger | `sudo apt install gdb` |
| `valgrind` | Memory checker | `sudo apt install valgrind` |
| `make` | Build automation | `sudo apt install make` |

## Recommended Books

1. **"The C Programming Language"** (K&R) — The definitive reference
2. **"C Programming: A Modern Approach"** (K.N. King) — Best for beginners
3. **"Expert C Programming"** (Peter van der Linden) — Deep dives
4. **"21st Century C"** (Ben Klemens) — Modern practices

---

> **Professor's Final Word**: C is not harder than Python — it is *honest*. It does exactly what you tell it to do, nothing more, nothing less. That honesty is what makes it the foundation of operating systems, embedded systems, and high-performance software. Master C, and you master the machine.
