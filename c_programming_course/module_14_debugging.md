# Module 14: Debugging, Profiling & Best Practices

## Debugging with `gdb`

You cannot debug C effectively with `printf` alone.

```bash
gcc -g -o program program.c   # -g includes debug symbols
gdb ./program
```

Inside GDB:
- `break main`: Set breakpoint at main
- `run`: Run program
- `next`: Execute next line (step over)
- `step`: Step into functions
- `print var`: Inspect variable
- `backtrace`: Show call stack
- `continue`: Continue execution
- `quit`: Exit GDB

## Memory Checking with `valgrind`

```bash
valgrind --leak-check=full ./program
```

Valgrind catches:
- Memory leaks (`malloc` without `free`)
- Invalid reads/writes (buffer overflows, use-after-free)
- Uninitialized memory usage

## Best Practices

1. **Always initialize variables.** Uninitialized variables contain garbage.
2. **Check `malloc` return value.** It can fail.
3. **Free what you allocate.** Every `malloc` should have a corresponding `free`.
4. **Keep functions small.** Just like Python.
5. **Use `const` aggressively.** It prevents accidental modifications.
6. **Prefer `enum` over magic numbers.**
7. **Never use `gets()`.** Removed from C11. Use `fgets`.
8. **Compile with `-Wall -Wextra -Werror`.** Treat warnings as errors.
9. **Use `size_t` for sizes and indices.** It's the right type for memory-related values.
10. **Avoid global variables.** They make testing and reasoning difficult.

## Practice Problems

### Problem 14.1: Debug a Segfault
Find and fix the bug:

```c
#include <stdio.h>

int main(void)
{
    int *p;
    *p = 42;
    printf("%d\n", *p);
    return 0;
}
```

<details>
<summary>Solution</summary>

`p` is uninitialized. It contains a garbage address. Fix:

```c
int x = 0;
int *p = &x;
*p = 42;
```

Or use `malloc`.
</details>
