# Module 6: Pointers — The Core Concept

## Why Pointers Exist

In Module 4, we discovered a critical limitation: C passes all arguments by value. This means functions cannot modify their caller's variables:

```c
void swap_wrong(int a, int b)
{
    int temp = a;
    a = b;
    b = temp;
}
// main's variables remain unchanged!
```

We also saw that arrays "decay" to pointers when passed to functions, losing their size information.

**Pointers solve both problems.** They are the mechanism by which C achieves:
- Pass-by-reference behavior
- Dynamic memory allocation
- Efficient array/string manipulation
- Data structures (linked lists, trees, graphs)
- Direct hardware access and memory-mapped I/O

## What Is a Pointer?

A **pointer** is a variable that stores a **memory address**.

Recall our machine model: RAM is a giant array of bytes, each with an address (index). A pointer holds one of these indices. In a 32-bit system, a pointer is 4 bytes; in a 64-bit system, it is 8 bytes.

```c
int x = 10;       // Variable x at address 1000, value 10
int *p = &x;      // Pointer p at address 2000, value 1000 (address of x)
```

**Memory visualization:**
```
Address:    1000    1001    1002    1003    ...    2000    2001    2002    2003
Value:        10       0       0       0    ...    1000       0       0       0
Variable:      x                               ...       p
Type:        int                             ...    int *
```

## Pointer Syntax Explained

### Declaration
```c
int *p;     // p is a pointer to an int
char *c;    // c is a pointer to a char
double *d;  // d is a pointer to a double
void *v;    // v is a generic pointer (can point to anything)
```

**How to read it:** Start at the variable name, go right if possible, then left.
- `int *p` → "p is a pointer to an int"

### The Address-of Operator: `&`
```c
int x = 10;
int *p = &x;  // &x means "the address of x"
```

### The Dereference Operator: `*`
```c
int x = 10;
int *p = &x;

printf("%d\n", *p);   // *p means "the value at address p" → prints 10
*p = 20;               // "Put 20 at the address stored in p"
printf("%d\n", x);    // x is now 20!
```

**The `*` symbol has two meanings:**
1. In a declaration: "this is a pointer"
2. In an expression: "dereference" (go to the address and get the value)

## The Swap Function — Now Correct

```c
#include <stdio.h>

void swap(int *a, int *b)
{
    int temp = *a;  // Dereference to get the value
    *a = *b;        // Put b's value where a points
    *b = temp;      // Put temp's value where b points
}

int main(void)
{
    int x = 5, y = 10;
    printf("Before: x=%d, y=%d\n", x, y);
    swap(&x, &y);   // Pass the ADDRESSES of x and y
    printf("After: x=%d, y=%d\n", x, y);
    return 0;
}
```

## Advanced Pointer Arithmetic and `ptrdiff_t`

Pointers support arithmetic operations, scaled by the size of the pointed-to type. Under the hood, if `p` is a pointer to `Type`, `p + n` translates to an address of `p + (n * sizeof(Type))`.

```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;  // p points to arr[0]

printf("%d\n", *(p + 2)); // 30 (offset by 2 * 4 bytes = 8 bytes)
```

You can subtract two pointers of the same type to find the number of elements between them. The result is of type `ptrdiff_t` (defined in `<stddef.h>`), which is a signed integer type capable of representing the difference.

```c
#include <stddef.h>
int *p1 = &arr[1];
int *p2 = &arr[4];
ptrdiff_t diff = p2 - p1; // 3 elements apart
```

Negative offsets are also valid:
```c
int *end = &arr[4];
printf("%d\n", *(end - 2)); // prints 30
```

## Array-Pointer Equivalence

These are equivalent:
```c
arr[i]    ==    *(arr + i)    ==    *(i + arr)    ==    i[arr]
```

**Key difference:**
- `arr` is an array (fixed address, `sizeof(arr)` gives total bytes)
- `p` is a pointer (can be reassigned, `sizeof(p)` gives pointer size)

```c
printf("%zu\n", sizeof(arr));  // 20 (5 ints × 4 bytes)
printf("%zu\n", sizeof(p));    // 8 (pointer size on 64-bit system)
```

## Type Punning and Strict Aliasing

In low-level C, you might want to view the same bytes in memory as different types. This is called **type punning**.

```c
float f = 3.14f;
int *ip = (int *)&f; // Dangerous!
```
While this compiles, dereferencing `ip` violates the **Strict Aliasing Rule**, which states that you cannot access an object of one type through a pointer of a different, incompatible type (with a few exceptions like `char *`). Doing so invokes Undefined Behavior (UB) because the compiler optimizes assuming `f` and `*ip` don't point to the same memory.

To safely type-pun, use `memcpy` or a `union`:
```c
float f = 3.14f;
int i;
memcpy(&i, &f, sizeof(float)); // Safe!
```

## Endianness and Byte-Level Access

Using a `char *` or `unsigned char *`, you can safely inspect the individual bytes of any data type. This reveals the system's **Endianness** (byte order).

```c
int num = 0x12345678;
unsigned char *c = (unsigned char *)&num;

// On Little-Endian (x86/ARM), prints: 78 56 34 12
// On Big-Endian (Network byte order), prints: 12 34 56 78
for (size_t i = 0; i < sizeof(num); i++) {
    printf("%02x ", c[i]);
}
printf("\n");
```

## The NULL Pointer

A pointer that points to nothing:
```c
int *p = NULL;  // NULL is #defined as (void *)0 or just 0
```

Dereferencing `NULL` causes a **Segmentation Fault** (Segfault). It's a critical safety mechanism.

## The `const` Keyword with Pointers

```c
int x = 10, y = 20;

// 1. Pointer to constant data
const int *p = &x;   // Cannot modify *p, but can change p
p = &y;              // OK

// 2. Constant pointer to data
int *const q = &x;   // Cannot change q, but can modify *q
*q = 20;             // OK

// 3. Constant pointer to constant data
const int *const r = &x;  // Cannot change r or *r
```

## Common Pointer Mistakes

1. **Uninitialized Pointer:** `int *p; *p = 10; // CRASH!`
2. **Dangling Pointer:** Returning a pointer to a local stack variable.
3. **Memory Leak:** Allocating memory and losing the pointer.
4. **Double Free:** Calling `free()` twice on the same pointer.

## Practice Problems

### Problem 6.1: Endianness Checker
Write a program that determines whether your system is Little-Endian or Big-Endian using pointers.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    unsigned int x = 1;
    char *c = (char*)&x;
    if (*c) {
        printf("Little-Endian\n");
    } else {
        printf("Big-Endian\n");
    }
    return 0;
}
```
</details>

---

> **Professor's Note**: Pointers are the heart and soul of C. They are also the source of most C bugs. Draw memory diagrams. Understand strict aliasing. Respect undefined behavior. Pointers give you raw access to the machine—use it wisely.
\n\n## Deep Dive: Pointer Arithmetic & Double Pointers\n\nPointer arithmetic allows navigating arrays and memory blocks effectively. Double pointers (`**ptr`) are vital for modifying pointer values inside functions, such as updating the head of a linked list or managing 2D dynamically allocated arrays.\n