# Module 11: Advanced Pointers

## Pointer to Pointer (`**`)

If a pointer stores an address, a pointer-to-pointer stores the address of a pointer.

```c
int x = 10;
int *p = &x;
int **pp = &p;

printf("%d\n", **pp);  // 10
```

**Use case:** Modifying a pointer inside a function (e.g., linked list insertion, dynamic array resizing).

## Function Pointers

Functions live in memory too. You can store their addresses.

```c
#include <stdio.h>

int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }

int main(void)
{
    int (*operation)(int, int);  // Declare function pointer

    operation = add;
    printf("%d\n", operation(5, 3));  // 8

    operation = sub;
    printf("%d\n", operation(5, 3));  // 2

    return 0;
}
```

**Read the declaration:** `operation` is a pointer (`*`) to a function (`(...)`) that takes two `int`s and returns an `int`.

**Use case:** Callback functions, sorting with custom comparators (`qsort`).

## `qsort` with Function Pointers

```c
#include <stdio.h>
#include <stdlib.h>

int compare_ints(const void *a, const void *b)
{
    int arg1 = *(const int *)a;
    int arg2 = *(const int *)b;
    return (arg1 > arg2) - (arg1 < arg2);  // Returns -1, 0, or 1
}

int main(void)
{
    int arr[] = {3, 1, 4, 1, 5, 9, 2, 6};
    int n = sizeof(arr) / sizeof(arr[0]);

    qsort(arr, n, sizeof(int), compare_ints);

    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    return 0;
}
```

**`qsort` parameters:**
- `arr`: Array to sort
- `n`: Number of elements
- `sizeof(int)`: Size of each element
- `compare_ints`: Comparison function

## `void*` — The Generic Pointer

A pointer that can point to any data type.

```c
void *ptr;
int x = 10;
ptr = &x;

// To use it, you MUST cast it back:
printf("%d\n", *(int*)ptr);
```

`malloc` returns `void*` because it doesn't know what type you need.

## Complex Declarations (The "Clockwise Spiral Rule")

```c
int *arr[10];     // Array of 10 pointers to int
int (*arr)[10];   // Pointer to an array of 10 ints
int *(*fp)(int);  // Pointer to a function that takes int and returns int*
```

## Practice Problems

### Problem 11.1: Apply Function
Write a function `void apply(int *arr, int n, void (*func)(int *))` that applies a given function to every element.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

void apply(int *arr, int n, void (*func)(int *))
{
    for (int i = 0; i < n; i++) {
        func(&arr[i]);
    }
}

void increment(int *x) { (*x)++; }
void square(int *x) { *x = *x * *x; }

int main(void)
{
    int arr[] = {1, 2, 3, 4, 5};
    apply(arr, 5, increment);
    // arr is now {2, 3, 4, 5, 6}
    apply(arr, 5, square);
    // arr is now {4, 9, 16, 25, 36}
    return 0;
}
```
</details>

### Problem 11.2: 2D Array Allocation
Write a function `void allocate_matrix(int ***mat, int rows, int cols)` that allocates a 2D array on the heap.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <stdlib.h>

void allocate_matrix(int ***mat, int rows, int cols)
{
    *mat = malloc(rows * sizeof(int *));
    for (int i = 0; i < rows; i++) {
        (*mat)[i] = malloc(cols * sizeof(int));
    }
}

void free_matrix(int **mat, int rows)
{
    for (int i = 0; i < rows; i++) {
        free(mat[i]);
    }
    free(mat);
}

int main(void)
{
    int **matrix;
    allocate_matrix(&matrix, 3, 3);

    matrix[1][2] = 42;
    printf("%d\n", matrix[1][2]);

    free_matrix(matrix, 3);
    return 0;
}
```
</details>
