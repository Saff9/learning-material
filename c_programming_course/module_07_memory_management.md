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

The stack is a **LIFO (Last-In-First-Out)** data structure managed automatically by the compiler.

### What Lives on the Stack?
- Local variables
- Function parameters
- Return addresses
- Temporary values

### Stack Characteristics
| Feature | Description |
|---------|-------------|
| **Allocation** | Automatic — compiler generates code to push/pop |
| **Speed** | Very fast — just adjusts the stack pointer |
| **Size** | Limited (typically 1-8 MB) |
| **Lifetime** | Variables exist only during function execution |
| **Scope** | Local to the function/block |

### Stack Frame Example
```c
void foo(int x)
{
    int y = x + 1;  // y lives on foo's stack frame
    bar(y);
}

void bar(int z)
{
    int w = z * 2;  // w lives on bar's stack frame
}

int main(void)
{
    int a = 5;
    foo(a);
    return 0;
}
```

**Stack trace during `bar(y)` execution:**
```
┌─────────────────┐
│ bar's frame     │  z=6, w=12
│                 │
├─────────────────┤
│ foo's frame     │  x=5, y=6
│                 │
├─────────────────┤
│ main's frame    │  a=5
│                 │
├─────────────────┤
│ ...             │
└─────────────────┘
```

When `bar` returns, its frame is popped off the stack. All its local variables are destroyed.

### The Dangling Pointer Problem
```c
int *bad_idea(void)
{
    int x = 10;   // x lives on the stack
    return &x;    // Returns address of local variable!
}

int main(void)
{
    int *p = bad_idea();  // p now points to freed stack memory!
    *p = 20;              // UNDEFINED BEHAVIOR!
    return 0;
}
```

When `bad_idea` returns, its stack frame is destroyed. The memory that held `x` may be reused by the next function call. Accessing `p` is like using a key to a house that has been demolished.

## The Heap

The heap is a large pool of memory for **dynamic allocation** — memory requested at runtime.

### Heap Characteristics
| Feature | Description |
|---------|-------------|
| **Allocation** | Manual — you request it with `malloc` |
| **Speed** | Slower — requires system calls and bookkeeping |
| **Size** | Large (limited only by available RAM) |
| **Lifetime** | Persists until explicitly freed |
| **Scope** | Global — accessible from anywhere if you have the pointer |

## Dynamic Memory Functions

### `malloc` — Memory Allocation
```c
#include <stdlib.h>

int *arr = malloc(5 * sizeof(int));  // Request 20 bytes (5 ints)

if (arr == NULL) {
    fprintf(stderr, "Memory allocation failed!\n");
    return 1;
}

// Use the memory...
for (int i = 0; i < 5; i++) {
    arr[i] = i * 10;
}

free(arr);   // CRITICAL: Return memory to the OS
arr = NULL;  // Good practice: prevent dangling pointer
```

**Key points:**
- `malloc` returns `void *` — a generic pointer. C automatically converts it to the target type.
- `malloc` does NOT initialize memory — it contains garbage values.
- Always check for `NULL` return — allocation can fail!
- `sizeof` is a compile-time operator that returns the size of a type in bytes.

### `calloc` — Contiguous Allocation with Zeroing
```c
int *arr = calloc(5, sizeof(int));  // 5 elements, each sizeof(int) bytes
// All bytes are initialized to 0!
```

Use `calloc` when you need zero-initialized memory (e.g., counting arrays).

### `realloc` — Resize Allocated Memory
```c
int *arr = malloc(5 * sizeof(int));
// ... fill arr ...

// Need more space?
int *new_arr = realloc(arr, 10 * sizeof(int));

if (new_arr == NULL) {
    // realloc failed, but arr is still valid!
    free(arr);
    return 1;
}

arr = new_arr;  // Update pointer (may have moved!)
// Now arr has space for 10 ints
```

**Important:** `realloc` may move the memory block to a new location. Always use its return value!

### `free` — Deallocation
```c
free(ptr);
```

- Returns memory to the heap manager
- Does NOT set `ptr` to `NULL` — you must do this manually
- Double-freeing crashes your program
- Freeing `NULL` is safe (no-op)

## Common Memory Bugs

### 1. Memory Leak
```c
void leaky(void)
{
    int *p = malloc(sizeof(int));
    *p = 42;
    // Forgot to free! Memory is lost forever (until program exits)
}
```

**Detection:** Use `valgrind --leak-check=full ./program`

### 2. Use-After-Free
```c
int *p = malloc(sizeof(int));
*p = 42;
free(p);
*p = 100;  // CRASH! Writing to freed memory
```

### 3. Double Free
```c
int *p = malloc(sizeof(int));
free(p);
free(p);  // CRASH!
```

### 4. Buffer Overflow on Heap
```c
int *arr = malloc(5 * sizeof(int));
arr[10] = 999;  // Writes past allocated memory! Corrupts heap metadata
```

### 5. Mismatched Allocation/Deallocation
```c
int *arr = calloc(10, sizeof(int));
// ...
free(arr);  // OK

// But don't do this:
int local[10];
free(local);  // CRASH! Can't free stack memory
```

## Memory Management Best Practices

### 1. Always Check `malloc` Return
```c
int *p = malloc(sizeof(int));
if (p == NULL) {
    // Handle error gracefully
}
```

### 2. Free Memory in the Same Scope That Allocated It
```c
// Good: caller allocates, caller frees
int *create_array(int size)
{
    return malloc(size * sizeof(int));
}

int main(void)
{
    int *arr = create_array(10);
    // ... use arr ...
    free(arr);  // Caller frees
    return 0;
}
```

### 3. Set Pointers to NULL After Free
```c
free(ptr);
ptr = NULL;  // Prevents accidental use-after-free
```

### 4. Use `valgrind` Regularly
```bash
valgrind --leak-check=full --track-origins=yes ./program
```

## Python Comparison

| Operation | Python | C |
|-----------|--------|---|
| Allocate array | `arr = [0] * 100` | `arr = calloc(100, sizeof(int))` |
| Resize array | `arr.append(x)` | `arr = realloc(arr, new_size)` |
| Free memory | Automatic (GC) | `free(arr)` |
| Memory leak | Rare (circular refs) | Common (forgot `free`) |
| Bounds check | Yes (IndexError) | No (segfault or corruption) |

## Practice Problems

### Problem 7.1: Basic Heap Allocation
Allocate an array of 10 doubles on the heap, initialize them to 0.5, 1.0, 1.5, ..., 5.0, print them, and free the memory.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int n = 10;
    double *arr = malloc(n * sizeof(double));

    if (arr == NULL) {
        fprintf(stderr, "Allocation failed!\n");
        return 1;
    }

    for (int i = 0; i < n; i++) {
        arr[i] = (i + 1) * 0.5;
    }

    for (int i = 0; i < n; i++) {
        printf("arr[%d] = %.1f\n", i, arr[i]);
    }

    free(arr);
    arr = NULL;

    return 0;
}
```
</details>

### Problem 7.2: Create and Return Array
Write a function `int *create_initialized_array(int n, int value)` that returns a heap-allocated array of `n` integers, all initialized to `value`.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <stdlib.h>

int *create_initialized_array(int n, int value)
{
    int *arr = calloc(n, sizeof(int));  // Zero-initialized
    if (arr == NULL) return NULL;

    for (int i = 0; i < n; i++) {
        arr[i] = value;
    }

    return arr;
}

int main(void)
{
    int *arr = create_initialized_array(5, 42);
    if (arr == NULL) return 1;

    for (int i = 0; i < 5; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");

    free(arr);
    return 0;
}
```
</details>

### Problem 7.3: Dynamic Array (Like Python List)
Implement a dynamic array that grows automatically. Start with capacity 2. When full, double the capacity using `realloc`.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int *data;
    int size;
    int capacity;
} DynamicArray;

DynamicArray *da_create(void)
{
    DynamicArray *da = malloc(sizeof(DynamicArray));
    if (da == NULL) return NULL;

    da->capacity = 2;
    da->size = 0;
    da->data = malloc(da->capacity * sizeof(int));

    if (da->data == NULL) {
        free(da);
        return NULL;
    }

    return da;
}

void da_append(DynamicArray *da, int value)
{
    if (da->size >= da->capacity) {
        da->capacity *= 2;
        int *new_data = realloc(da->data, da->capacity * sizeof(int));
        if (new_data == NULL) {
            fprintf(stderr, "Realloc failed!\n");
            return;
        }
        da->data = new_data;
    }
    da->data[da->size++] = value;
}

void da_free(DynamicArray *da)
{
    free(da->data);
    free(da);
}

int main(void)
{
    DynamicArray *da = da_create();
    if (da == NULL) return 1;

    for (int i = 0; i < 10; i++) {
        da_append(da, i * 10);
        printf("Appended %d, size=%d, capacity=%d\n",
               i * 10, da->size, da->capacity);
    }

    printf("Final array: ");
    for (int i = 0; i < da->size; i++) {
        printf("%d ", da->data[i]);
    }
    printf("\n");

    da_free(da);
    return 0;
}
```

**Amortized analysis:** Doubling the capacity means the average cost per append is O(1), even though individual `realloc` operations are O(n).
</details>

### Problem 7.4: Detect Memory Leak
Run the following program under `valgrind`. Fix the memory leak.

```c
#include <stdlib.h>

void process(void)
{
    int *data = malloc(100 * sizeof(int));
    // ... process data ...
    // Oops, forgot to free!
}

int main(void)
{
    for (int i = 0; i < 1000; i++) {
        process();
    }
    return 0;
}
```

<details>
<summary>Solution</summary>

Add `free(data);` at the end of `process()`:

```c
void process(void)
{
    int *data = malloc(100 * sizeof(int));
    // ... process data ...
    free(data);  // Fixed!
}
```

Run with: `valgrind --leak-check=full ./program` to verify.
</details>

---

> **Professor's Note**: Memory management is where C separates the professionals from the beginners. In Python, you create objects and forget about them. In C, every `malloc` is a contract — you promise to `free` that memory. Break the contract, and you get memory leaks, segfaults, or security vulnerabilities. Use `valgrind` religiously. Draw stack diagrams. And remember: with great power comes great responsibility.
