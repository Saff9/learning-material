# Module 16: Appendix & Quick Reference

## Python-to-C Cheat Sheet

| Python | C |
|--------|---|
| `x = 5` | `int x = 5;` |
| `x = 5.5` | `double x = 5.5;` |
| `s = "hello"` | `char s[] = "hello";` |
| `len(lst)` | `sizeof(arr)/sizeof(arr[0])` (only at declaration scope) |
| `lst.append(x)` | Use dynamic array with `realloc` |
| `print(x)` | `printf("%d\n", x);` |
| `range(10)` | `for (int i = 0; i < 10; i++)` |
| `if x == 5:` | `if (x == 5) {` |
| `while True:` | `while (1) {` |
| `def f(x):` | `int f(int x) {` |
| `None` | `NULL` |
| `True/False` | `1/0` or `<stdbool.h>` |
| `class Point:` | `struct Point { int x; int y; };` |
| `list[i]` | `arr[i]` |
| `with open(f):` | `FILE *fp = fopen(...); ... fclose(fp);` |

## Common Compiler Flags

```bash
gcc -Wall -Wextra -Werror -std=c11 -g -O0 -o program program.c
```

## Essential Tools

| Tool | Use |
|------|-----|
| `gcc` | Compile C programs |
| `gdb` | Debug programs |
| `valgrind` | Check for memory leaks |
| `make` | Build automation |
| `clang` | Alternative compiler with better diagnostics |

## Books for Further Study

1. **"The C Programming Language"** by Kernighan & Ritchie (K&R) — The bible
2. **"C Programming: A Modern Approach"** by K. N. King — Best for beginners
3. **"Expert C Programming"** by Peter van der Linden — Deep dives
4. **"21st Century C"** by Ben Klemens — Modern C practices

---

> **Final Professor's Note**: You have now been equipped with a comprehensive foundation in C programming. The journey from Python to C is challenging because C demands that you understand every layer of abstraction. But this understanding is precisely what makes you a true software developer. You now know how memory works, how the stack and heap operate, how pointers connect data structures, and how compilation transforms source code into executable machine code. These concepts transcend any single language — they are the foundation of computing itself. Go build something amazing.
