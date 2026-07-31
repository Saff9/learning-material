# Module 13: Advanced Topics

## Bit Manipulation

C is used for systems programming because it can manipulate individual bits.

```c
unsigned int flags = 0;

flags |= (1 << 2);    // Set bit 2
flags &= ~(1 << 2);   // Clear bit 2
if (flags & (1 << 2)) { /* bit 2 is set */ }
flags ^= (1 << 2);    // Toggle bit 2
```

## `const` with Pointers (Review)

```c
int x = 10, y = 20;

const int *p = &x;   // Pointer to constant int: cannot change *p, but can change p
int *const q = &x;   // Constant pointer to int: cannot change q, but can change *q
const int *const r = &x; // Neither can change
```

## Multi-threading (C11)

C11 introduced standard threads via `<threads.h>`.

```c
#include <threads.h>
#include <stdio.h>

int thread_func(void *arg)
{
    printf("Hello from thread\n");
    return 0;
}

int main(void)
{
    thrd_t t;
    thrd_create(&t, thread_func, NULL);
    thrd_join(t, NULL);
    return 0;
}
```

*(Note: On some systems, you may need to link with `-lpthread` or use POSIX `pthread` instead).*

## Modern C (C23)

The latest standard, C23, introduces:
- `nullptr` constant and `nullptr_t` type
- `auto` for type inference (like C++): `auto x = 5;`
- New keywords: `constexpr`, `typeof`, etc.
- Better Unicode support

Most compilers are still catching up to C23. Learn C11/C17 first.

## Practice Problems

### Problem 13.1: Print Binary
Write a function `void print_binary(unsigned int n)` that prints the binary representation.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

void print_binary(unsigned int n)
{
    if (n > 1) print_binary(n >> 1);
    putchar('0' + (n & 1));
}

int main(void)
{
    print_binary(42);  // 101010
    printf("\n");
    return 0;
}
```
</details>

### Problem 13.2: Race Condition Fix
Write a multi-threaded program where two threads increment a shared counter 1,000,000 times each. Observe the race condition. Then fix it.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <threads.h>

#define COUNT 1000000

int counter = 0;
mtx_t mutex;

int increment(void *arg)
{
    for (int i = 0; i < COUNT; i++) {
        mtx_lock(&mutex);
        counter++;
        mtx_unlock(&mutex);
    }
    return 0;
}

int main(void)
{
    mtx_init(&mutex, mtx_plain);

    thrd_t t1, t2;
    thrd_create(&t1, increment, NULL);
    thrd_create(&t2, increment, NULL);

    thrd_join(t1, NULL);
    thrd_join(t2, NULL);

    printf("Counter: %d (expected: %d)\n", counter, 2 * COUNT);

    mtx_destroy(&mutex);
    return 0;
}
```

Compile with: `gcc -std=c11 -o program program.c -lpthread`
</details>
