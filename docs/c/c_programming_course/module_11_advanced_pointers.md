# Module 11: Advanced Pointers

## Pointer to Pointer (`**`) and N-Level Pointers

If a pointer stores an address, a pointer-to-pointer stores the address of a pointer. This concept can theoretically be extended infinitely (`***`, `****`), though going beyond triple pointers is incredibly rare and usually a sign of poor design.

```c
int x = 10;
int *p = &x;
int **pp = &p;
int ***ppp = &pp; // Triple pointer

printf("%d\n", ***ppp);  // 10
```

**Memory Layout:**
```
[ x : 10 ]  <-- [ p : &x ]  <-- [ pp : &p ]  <-- [ ppp : &pp ]
```

**Use case for Double Pointers:** Modifying a pointer inside a function. For instance, when allocating a 2D array or inserting a node into a linked list where the head pointer itself might need to change.

```c
void allocate_int(int **ptr) {
    *ptr = malloc(sizeof(int)); // Modify the caller's pointer!
}

int main() {
    int *p = NULL;
    allocate_int(&p);
    *p = 5;
    free(p);
}
```

## Function Pointers and Callbacks

Functions exist as machine instructions in the Text/Code segment of memory. A function pointer holds the memory address of the first instruction of a function.

### Declaration Syntax
```c
return_type (*pointer_name)(parameter_types);
```

```c
#include <stdio.h>

int add(int a, int b) { return a + b; }

int main(void)
{
    int (*operation)(int, int) = add;
    printf("%d\n", operation(5, 3));  // 8
    return 0;
}
```

### Callbacks
Function pointers allow C to implement **callbacks** — passing executable code as an argument to another function. This is how `qsort` works in the standard library.

```c
#include <stdlib.h>

int compare_ints(const void *a, const void *b)
{
    int arg1 = *(const int *)a;
    int arg2 = *(const int *)b;
    return (arg1 > arg2) - (arg1 < arg2);
}

// Usage: qsort(arr, n, sizeof(int), compare_ints);
```

## Simulating OOP in C: Virtual Tables (vtables)

Function pointers are the bedrock of Object-Oriented Programming (OOP) in C. You can simulate polymorphism by placing function pointers inside `struct`s. This acts as a "vtable" (virtual method table) in C++.

```c
#include <stdio.h>

// Base "class" interface
typedef struct Animal {
    void (*speak)(void);
} Animal;

void dog_speak(void) { printf("Woof!\n"); }
void cat_speak(void) { printf("Meow!\n"); }

int main(void) {
    Animal dog = { .speak = dog_speak };
    Animal cat = { .speak = cat_speak };

    Animal *animals[] = { &dog, &cat };

    for(int i = 0; i < 2; i++) {
        animals[i]->speak(); // Polymorphism in C!
    }
    return 0;
}
```

## `void*` — The Generic Pointer

A `void*` is a pointer with no associated type. It represents a raw memory address. It cannot be dereferenced or used in pointer arithmetic directly because the compiler does not know the size of the underlying type.

**Use cases:**
- Generic data structures (e.g., a linked list node that can hold any data type).
- Generic APIs like `malloc`, `qsort`, and `pthread_create`.

```c
void *ptr;
int x = 10;
ptr = &x;

// To use it, you MUST cast it back to the proper type:
printf("%d\n", *(int*)ptr);
```

### Implementing Generic Data Structures
Using `void*`, you can build data structures that hold anything.

```c
typedef struct Node {
    void *data;
    struct Node *next;
} Node;

// But you must remember the type!
int val = 42;
Node n = { .data = &val, .next = NULL };
printf("%d\n", *(int*)n.data);
```

## Complex Declarations (The "Clockwise Spiral Rule")

Deciphering complex C declarations is notorious. Start at the identifier and move spirally outwards, prioritizing parentheses and arrays/functions on the right over pointers on the left.

```c
int *arr[10];     // arr is an array of 10 pointers to int
int (*arr)[10];   // arr is a pointer to an array of 10 ints
int *(*fp)(int);  // fp is a pointer to a function taking int, returning int*
void (*(*f[])(void))(); // f is an array of pointers to functions that take void and return a pointer to a function that takes void and returns void. (Yes, really).
```

## Practice Problems

### Problem 11.1: 2D Array Allocation via Double Pointers
Write a function `void allocate_matrix(int ***mat, int rows, int cols)` that allocates a contiguous 2D array on the heap (an array of pointers pointing to rows within a single large block).

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <stdlib.h>

void allocate_matrix(int ***mat, int rows, int cols)
{
    *mat = malloc(rows * sizeof(int *));
    (*mat)[0] = malloc(rows * cols * sizeof(int));
    
    for (int i = 1; i < rows; i++) {
        (*mat)[i] = (*mat)[0] + (i * cols);
    }
}

void free_matrix(int **mat)
{
    free(mat[0]); // Free the data block
    free(mat);    // Free the row pointers
}
```
This contiguous allocation method is vastly superior for CPU cache locality compared to allocating each row individually!
</details>
