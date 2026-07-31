# Module 14: Debugging, Profiling & Best Practices

## Comprehensive Debugging with `gdb`

You cannot debug C effectively with `printf` alone. The GNU Debugger (GDB) is an essential tool for inspecting what your program is doing while it runs, or what it was doing at the moment it crashed.

### Compiling for Debugging

First, compile your program with debug symbols (`-g`) and without optimizations (`-O0`):
```bash
gcc -g -O0 -o program program.c
```

### Starting GDB

```bash
gdb ./program
```
Or, if debugging a core dump (a crash file):
```bash
gdb ./program core
```

### Essential GDB Commands

**1. Breakpoints**
- `break main` (or `b main`): Stop execution when entering `main`.
- `break 42`: Stop at line 42 of the current file.
- `break file.c:10`: Stop at line 10 of `file.c`.
- `info breakpoints`: List all current breakpoints.
- `delete 1`: Delete breakpoint number 1.

**2. Execution Control**
- `run` (or `r`): Start execution. You can pass arguments like `run arg1 arg2`.
- `continue` (or `c`): Continue running until the next breakpoint or crash.
- `next` (or `n`): Execute the next line of code (steps OVER function calls).
- `step` (or `s`): Execute the next line of code (steps INTO function calls).
- `finish`: Run until the current function returns.

**3. Inspecting State**
- `print var` (or `p var`): Print the value of `var`.
- `print *ptr`: Print the value pointed to by `ptr`.
- `display var`: Automatically print `var` every time the program stops.
- `info locals`: Show all local variables in the current frame.
- `ptype var`: Show the data type of `var`.

**4. The Call Stack**
- `backtrace` (or `bt`): Show the call stack (who called what to get to the current point).
- `frame 2` (or `f 2`): Switch to frame 2 to inspect its local variables.
- `up` / `down`: Move up or down the call stack.

### Advanced GDB Tips

- **Text User Interface (TUI):** Press `Ctrl+X` then `A` in GDB, or start with `gdb -tui ./program`, to get a visual split-screen showing the source code alongside the command prompt.
- **Conditional Breakpoints:** `break 42 if x == 10` stops at line 42 only if `x` equals 10.
- **Watchpoints:** `watch my_var` stops execution whenever `my_var` is modified.

## Memory Checking with `valgrind`

Valgrind is indispensable for tracking memory issues.

```bash
valgrind --leak-check=full --track-origins=yes ./program
```

Valgrind catches:
- Memory leaks (`malloc` without `free`)
- Invalid reads/writes (buffer overflows, use-after-free)
- Uninitialized memory usage (especially with `--track-origins=yes`)

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
\n\n## Deep Dive: GDB and Production Makefiles\n\nUse `-Wall -Wextra -Werror -pedantic` in your GCC flags to catch potential issues early. GDB is essential for tracing segmentation faults.\nBasic GDB commands:\n- `run`: Start execution.\n- `break function_name`: Set a breakpoint.\n- `next`: Step over line.\n- `step`: Step into function.\n- `print var`: Inspect variable.\n- `backtrace`: Show the call stack.\n