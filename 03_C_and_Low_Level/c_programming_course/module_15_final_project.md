# Module 15: Final Project Guidelines

To cement your knowledge, build one of these projects from scratch:

## Project A: Custom String Library

Implement your own version of `<string.h>` functions: `strlen`, `strcpy`, `strcat`, `strcmp`, `strchr`, `strstr`. Use only pointers, no array indexing. Write comprehensive tests.

## Project B: Student Database

- Use a `struct Student` array (or linked list).
- Support adding, deleting, searching, and sorting students.
- Save/load the database to/from a binary file.
- Use modular programming (separate `.h` and `.c` files).

## Project C: Simple Shell

- Read a line of input.
- Parse it into arguments.
- Use `fork()` and `execvp()` to run the command.
- Handle basic piping and redirection (advanced).
- This teaches you how Python's `subprocess` module works under the hood.

## Project D: Memory Allocator

- Implement `malloc`, `free`, `realloc`, and `calloc` yourself.
- Request a large chunk of memory from the OS using `sbrk()` or `mmap()`.
- Manage a free list.
- This is the ultimate test of pointer and memory management skills.
