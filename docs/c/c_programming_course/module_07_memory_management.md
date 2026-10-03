# Module 7: Memory Management — Stack vs. Heap

## The Memory Layout of a C Program

When your C program runs, the operating system gives it a chunk of memory organized into several segments:

```
High Address
┌─────────────────┐
│   Stack         │  ← Local variables, function parameters, return addresses
│   (grows down)  │     Grows toward lower addresses
├─────────────────┤
│   Heap          │  ← Dynamically allocated memory (malloc, calloc, realloc)
│   (grows up)    │     Grows toward higher addresses
├─────────────────┤
│   BSS           │  ← Uninitialized global/static variables (zeroed)
├─────────────────┤
│   Data          │  ← Initialized global/static variables
├─────────────────┤
│   Text/Code     │  ← Machine instructions (read-only)
└─────────────────┘
Low Address
```

## The Stack

The stack is a **LIFO (Last-In-First-Out)** data structure managed automatically by the compiler. Fast, but limited in size.

## The Heap and Deep `malloc` Internals

The heap is a large pool of memory for **dynamic allocation**. 

When you call `malloc`, it doesn't immediately ask the OS for memory every single time. Instead, the standard C library (like glibc) implements a **memory allocator**. 

- **Syscalls:** The allocator uses OS-level system calls like `brk`/`sbrk` (to move the program break, extending the heap) or `mmap` (to request distinct pages of memory, typically for large allocations).
- **Arenas and Chunks:** glibc organizes memory into arenas and chunks. A chunk contains a header with metadata (size, whether it's free or in-use) followed by the actual payload you get a pointer to.
- **Fragmentation:** Allocating and freeing various sizes can lead to memory fragmentation.

Because of this bookkeeping, writing past the bounds of an allocated block often corrupts the chunk header of the *next* block, causing `free()` or the next `malloc()` to crash mysteriously!

## Dynamic Memory Functions Best Practices

### `malloc` — Memory Allocation
```c
#include <stdlib.h>

// BEST PRACTICE: Use sizeof(*arr) instead of sizeof(int).
// This prevents bugs if you change the type of arr later.
int *arr = malloc(5 * sizeof(*arr)); 

if (!arr) { // Check for NULL!
    fprintf(stderr, "Memory allocation failed!\n");
    return 1;
}
```

### `calloc` — Contiguous Allocation with Zeroing
```c
// BEST PRACTICE: When dealing with security or cryptographic
// data, zeroing memory is crucial. calloc does this.
int *arr = calloc(5, sizeof(*arr)); 
```

### `realloc` — Resize Allocated Memory
```c
// BEST PRACTICE: Never do `arr = realloc(arr, size);` directly.
// If realloc fails, it returns NULL and the original pointer is lost (memory leak).
int *new_arr = realloc(arr, 10 * sizeof(*arr));
if (new_arr) {
    arr = new_arr;
} else {
    // Handle error; arr is still valid and needs freeing!
    free(arr);
    return 1;
}
```

### `free` — Deallocation
```c
// BEST PRACTICE: Avoid use-after-free by NULLing pointers.
free(ptr);
ptr = NULL; 
```

## Memory Leak Prevention and Valgrind

A memory leak occurs when memory is allocated on the heap but never freed, rendering it unreachable. In long-running programs (like servers), leaks will eventually consume all RAM, invoking the OS's OOM (Out Of Memory) killer.

### Advanced Valgrind Usage

Valgrind is a dynamic binary instrumentation framework. The default tool, **Memcheck**, is a memory error detector.

```bash
valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes ./program
```

- `--leak-check=full`: Shows exactly where memory was leaked.
- `--show-leak-kinds=all`: Shows all kinds of leaks, including "definitely lost" and "indirectly lost".
- `--track-origins=yes`: If you use uninitialized memory, this tells you exactly where that memory came from, rather than just where it crashed.

**Common Valgrind Errors:**
- `Invalid read/write of size X`: Buffer overflow, use-after-free, or out-of-bounds access.
- `Conditional jump or move depends on uninitialised value(s)`: You forgot to initialize a variable or memory block.
- `Definitely lost`: You have a memory leak. You lost the pointer to allocated memory.

## Common Memory Bugs

1. **Memory Leak:** Forgetting to free.
2. **Use-After-Free:** Reading/writing to a pointer after `free()`. Highly exploitable security vulnerability.
3. **Double Free:** Freeing the same memory twice corrupts the allocator's free list.
4. **Buffer Overflow:** Writing past the allocated size. Corrupts adjacent metadata.

## Practice Problems

### Problem 7.1: Safe Realloc Wrapper
Write a safe realloc function wrapper that avoids the common memory leak trap.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <stdlib.h>

void *safe_realloc(void *ptr, size_t size) {
    void *new_ptr = realloc(ptr, size);
    if (!new_ptr && size != 0) {
        fprintf(stderr, "Fatal: memory allocation failed\n");
        free(ptr);
        exit(EXIT_FAILURE);
    }
    return new_ptr;
}
```
</details>

---

> **Professor's Note**: Memory management is where C separates the professionals from the beginners. Understand how the allocator works under the hood. Treat Valgrind as your co-pilot. Never blindly cast `malloc`, and always check for `NULL`.
\n\n## Deep Dive: Advanced Memory Management\n\nUnderstanding `malloc`, `calloc`, `realloc`, and `free` is essential.\n- `malloc`: Allocates uninitialized memory.\n- `calloc`: Allocates and zero-initializes memory.\n- `realloc`: Resizes an existing memory block.\n- `free`: Deallocates memory to prevent leaks.\n\nAlways check for `NULL` returns and use Valgrind to ensure no memory leaks occur (`valgrind --leak-check=full ./program`).\n