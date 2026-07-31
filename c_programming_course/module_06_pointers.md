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
- Direct hardware access

## What Is a Pointer?

A **pointer** is a variable that stores a **memory address**.

Recall our machine model: RAM is a giant array of bytes, each with an address (index). A pointer holds one of these indices.

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

**Memory trace:**
```
Before swap:
  main's frame:  x=5 (addr 1000), y=10 (addr 1004)

swap(&x, &y) is called:
  swap's frame:  a=1000 (addr 2000), b=1004 (addr 2004)

Inside swap:
  temp = *a = value at 1000 = 5
  *a = *b → value at 1000 = value at 1004 = 10
  *b = temp → value at 1004 = 5

After swap returns:
  main's frame:  x=10 (addr 1000), y=5 (addr 1004)  ← MODIFIED!
```

## The NULL Pointer

A pointer that points to nothing:
```c
int *p = NULL;  // NULL is #defined as (void *)0 or just 0
```

Dereferencing `NULL` causes a **Segmentation Fault** (Segfault) — your program tries to access memory address 0, which the operating system has marked as inaccessible.

**Segfaults are good!** They tell you immediately that your pointer is invalid. The real danger is **invalid non-NULL pointers** — pointers that contain garbage addresses.

```c
int *p;           // UNINITIALIZED! Contains garbage address
*p = 10;          // WRITES TO RANDOM MEMORY! May or may not crash
```

**Always initialize pointers:**
```c
int *p = NULL;    // Safe
int *p = &x;      // Safe
```

## Pointer Arithmetic

Pointers support arithmetic operations, scaled by the size of the pointed-to type:

```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;  // p points to arr[0]

printf("%d\n", *p);       // 10
printf("%d\n", *(p + 1)); // 20
printf("%d\n", *(p + 2)); // 30
```

**Why does `p + 1` skip 4 bytes?**
Because `p` is an `int *`, and `sizeof(int)` is 4. The compiler automatically multiplies the offset by `sizeof(int)`.

```c
char *c = "Hello";
printf("%c\n", *(c + 1));  // 'e' (skips 1 byte because sizeof(char) is 1)
```

### Array-Pointer Equivalence

These are equivalent:
```c
arr[i]    ==    *(arr + i)    ==    *(i + arr)    ==    i[arr]
```

Yes, `i[arr]` is valid C! (Don't use it — it's confusing.)

## Pointers and Arrays

An array name is essentially a pointer to its first element:
```c
int arr[5] = {10, 20, 30, 40, 50};
int *p = arr;  // Same as: int *p = &arr[0];

// All of these are equivalent:
printf("%d\n", arr[2]);
printf("%d\n", p[2]);
printf("%d\n", *(arr + 2));
printf("%d\n", *(p + 2));
```

**Key difference:**
- `arr` is an array (fixed address, `sizeof(arr)` gives total bytes)
- `p` is a pointer (can be reassigned, `sizeof(p)` gives pointer size)

```c
printf("%zu\n", sizeof(arr));  // 20 (5 ints × 4 bytes)
printf("%zu\n", sizeof(p));    // 8 (pointer size on 64-bit system)

// p = p + 1;  // OK, pointers are mutable
// arr = arr + 1;  // ERROR! Array names are not modifiable
```

## Pointers to Pointers

If a pointer stores an address, a pointer-to-pointer stores the address of a pointer:

```c
int x = 10;
int *p = &x;
int **pp = &p;

printf("x = %d\n", x);       // 10
printf("*p = %d\n", *p);     // 10
printf("**pp = %d\n", **pp); // 10

printf("Address of x: %p\n", (void *)&x);   // 1000
printf("Value of p: %p\n", (void *)p);      // 1000
printf("Address of p: %p\n", (void *)&p);   // 2000
printf("Value of pp: %p\n", (void *)pp);    // 2000
```

**Use case:** Modifying a pointer inside a function (e.g., linked list insertion, dynamic array resizing).

## The `const` Keyword with Pointers

```c
int x = 10, y = 20;

// 1. Pointer to constant data
const int *p = &x;   // Cannot modify *p, but can change p
// *p = 20;  // ERROR!
p = &y;              // OK

// 2. Constant pointer to data
int *const q = &x;   // Cannot change q, but can modify *q
*q = 20;             // OK
// q = &y;   // ERROR!

// 3. Constant pointer to constant data
const int *const r = &x;  // Cannot change r or *r
```

**How to read:**
- Read from right to left (or use the "clockwise spiral rule")
- `const int *p` → "p is a pointer to an int that is const"
- `int *const p` → "p is a const pointer to an int"

## Common Pointer Mistakes

### 1. Uninitialized Pointer
```c
int *p;
*p = 10;  // CRASH! p contains garbage
```

### 2. Dangling Pointer
```c
int *p;
{
    int x = 10;
    p = &x;
}  // x is destroyed here!
*p = 20;  // UNDEFINED BEHAVIOR! p points to freed stack memory
```

### 3. Memory Leak
```c
int *p = malloc(sizeof(int));
p = NULL;  // Lost the address! Memory can never be freed.
```

### 4. Double Free
```c
int *p = malloc(sizeof(int));
free(p);
free(p);  // CRASH! Already freed.
```

## Practice Problems

### Problem 6.1: Basic Pointer Operations
Declare an `int`, a pointer to it, and print both the value and the address. Then modify the value through the pointer.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    int num = 42;
    int *ptr = &num;

    printf("Value of num: %d\n", num);
    printf("Address of num: %p\n", (void *)&num);
    printf("Value of ptr: %p\n", (void *)ptr);
    printf("Value pointed to by ptr: %d\n", *ptr);

    *ptr = 100;
    printf("After modification through pointer: %d\n", num);

    return 0;
}
```
</details>

### Problem 6.2: Increment by Pointer
Write a function `void increment_by_pointer(int *n)` that increments the value at the address.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

void increment_by_pointer(int *n)
{
    (*n)++;  // Parentheses are important! *n++ would increment the pointer
}

int main(void)
{
    int x = 5;
    increment_by_pointer(&x);
    printf("x = %d\n", x);  // 6
    return 0;
}
```

**Note on precedence:** `*n++` is parsed as `*(n++)` because `++` has higher precedence than `*`. To increment the value, use `(*n)++`.
</details>

### Problem 6.3: Pointer Arithmetic with Arrays
Write a function that prints an array using only pointer arithmetic (no array indexing).

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

void print_with_pointer(const int *arr, int size)
{
    const int *end = arr + size;
    while (arr < end) {
        printf("%d ", *arr);
        arr++;
    }
    printf("\n");
}

int main(void)
{
    int nums[] = {10, 20, 30, 40, 50};
    print_with_pointer(nums, 5);
    return 0;
}
```
</details>

### Problem 6.4: Find Maximum Using Pointers
Write a function `int *find_max(int *arr, int n)` that returns a pointer to the maximum element.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int *find_max(int *arr, int n)
{
    if (n <= 0 || arr == NULL) return NULL;

    int *max_ptr = arr;
    for (int i = 1; i < n; i++) {
        if (arr[i] > *max_ptr) {
            max_ptr = &arr[i];
        }
    }
    return max_ptr;
}

int main(void)
{
    int nums[] = {45, 12, 78, 23, 67};
    int *max = find_max(nums, 5);
    printf("Max value: %d at index %ld\n", *max, max - nums);
    return 0;
}
```
</details>

### Problem 6.5: Draw the Memory Diagram
Given:
```c
int a = 5;
int b = 10;
int *p = &a;
int **pp = &p;
*p = 20;
*pp = &b;
**pp = 30;
```
Draw the memory layout after each line and determine the final values of `a` and `b`.

<details>
<summary>Solution</summary>

```
After int a = 5; int b = 10;
  Address 1000: a = 5
  Address 1004: b = 10

After int *p = &a;
  Address 2000: p = 1000 (points to a)

After int **pp = &p;
  Address 3000: pp = 2000 (points to p)

After *p = 20;
  Address 1000: a = 20 (dereferenced p, modified a)

After *pp = &b;
  Address 2000: p = 1004 (pp points to p, so we modified p to point to b)

After **pp = 30;
  pp → p → b, so b = 30

Final values: a = 20, b = 30
```
</details>

---

> **Professor's Note**: Pointers are the heart and soul of C. They are also the source of most C bugs. The key to mastering pointers is understanding the memory model — every variable lives at an address, and a pointer is just a variable that stores one of those addresses. Draw memory diagrams. Always initialize pointers. When in doubt, add parentheses around dereference operations. Pointers are not magic; they are simply integers that the compiler treats specially.
