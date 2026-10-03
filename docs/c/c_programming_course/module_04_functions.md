# Module 4: Functions

## Why Functions Matter

Functions are the building blocks of structured programming. They allow you to:
- Break complex problems into manageable pieces
- Reuse code without copy-pasting
- Test individual components in isolation
- Hide implementation details

In C, **all functions are global** — you cannot define a function inside another function (unlike Python's nested functions or lambdas).

## Function Declaration vs Definition

### Declaration (Prototype)
Tells the compiler: "This function exists, here's its signature."
```c
int add(int a, int b);  // Declaration/prototype
```

### Definition
The actual implementation:
```c
int add(int a, int b)   // Definition
{
    return a + b;
}
```

### Complete Example
```c
#include <stdio.h>

// Function declarations (prototypes) — typically in header files
int add(int a, int b);
double average(int arr[], int size);

int main(void)
{
    int result = add(5, 3);
    printf("5 + 3 = %d\n", result);

    int scores[] = {90, 85, 78, 92, 88};
    double avg = average(scores, 5);
    printf("Average: %.2f\n", avg);

    return 0;
}

// Function definitions
int add(int a, int b)
{
    return a + b;
}

double average(int arr[], int size)
{
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return (double)sum / size;
}
```

## Pass-by-Value: The Critical Concept

This is the most important concept in C functions. **In C, all arguments are passed by value by default.**

### What Does "Pass-by-Value" Mean?

When you call a function, the **values** of the arguments are **copied** into new local variables (the parameters). The original variables are never touched.

```c
#include <stdio.h>

void increment(int x)
{
    x = x + 1;  // Modifies the LOCAL COPY
    printf("Inside function: x = %d\n", x);  // Prints 6
}

int main(void)
{
    int a = 5;
    increment(a);
    printf("In main: a = %d\n", a);  // Prints 5!
    return 0;
}
```

### Memory Diagram

```
main's stack frame:
  a = 5  (address 1000)

When increment(a) is called:
  A NEW stack frame is created for increment:
    x = 5  (address 2000)  ← COPY of a's value

  x = x + 1 modifies address 2000:
    x = 6  (address 2000)

  increment returns, its stack frame is destroyed.
  a at address 1000 is still 5.
```

**Python comparison:**
```python
def increment(x):
    x = x + 1  # Rebinds local x to a new int object
    print(f"Inside: {x}")  # 6

a = 5
increment(a)
print(f"Outside: {a}")  # 5 (same behavior for immutable ints!)

# But for mutable objects:
def append_item(lst):
    lst.append(42)  # Modifies the SAME object

my_list = [1, 2, 3]
append_item(my_list)
print(my_list)  # [1, 2, 3, 42] — modified!
```

In Python, mutable objects can be modified because you're passing a reference. In C, there are no "references" — only values. To modify the original, you need **pointers** (covered in Module 6).

## The `void` Return Type

Functions that don't return a value use `void`:
```c
void print_greeting(const char *name)
{
    printf("Hello, %s!\n", name);
    // No return statement needed (but you can use "return;" to exit early)
}
```

## Recursion

A function that calls itself. C supports recursion just like Python.

### Factorial
```c
int factorial(int n)
{
    // Base case
    if (n <= 1) {
        return 1;
    }
    // Recursive case
    return n * factorial(n - 1);
}
```

**Call stack for factorial(4):**
```
factorial(4) calls factorial(3)
  factorial(3) calls factorial(2)
    factorial(2) calls factorial(1)
      factorial(1) returns 1
    factorial(2) returns 2 * 1 = 2
  factorial(3) returns 3 * 2 = 6
factorial(4) returns 4 * 6 = 24
```

### Fibonacci (Inefficient)
```c
int fibonacci(int n)
{
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}
```

**Time complexity:** O(2^n) — exponential! Each call branches into two more calls.

### Fibonacci (Efficient — Iterative)
```c
int fibonacci_iterative(int n)
{
    if (n <= 1) return n;

    int prev2 = 0, prev1 = 1;
    int current;

    for (int i = 2; i <= n; i++) {
        current = prev1 + prev2;
        prev2 = prev1;
        prev1 = current;
    }
    return current;
}
```

**Time complexity:** O(n), **Space complexity:** O(1)

### Tail Recursion

Some compilers can optimize tail-recursive functions (where the recursive call is the last operation):
```c
int factorial_tail(int n, int accumulator)
{
    if (n <= 1) return accumulator;
    return factorial_tail(n - 1, n * accumulator);
}

// Wrapper
int factorial(int n)
{
    return factorial_tail(n, 1);
}
```

**Note:** C compilers are NOT required to optimize tail recursion. Don't rely on it.

## Variable Scope and Lifetime

### Local (Automatic) Variables
```c
void func(void)
{
    int x = 10;  // Created when func is called, destroyed when it returns
}
```

### Static Local Variables
```c
void counter(void)
{
    static int count = 0;  // Initialized ONCE, persists between calls
    count++;
    printf("Called %d times\n", count);
}
```

**Python equivalent:** Using a function attribute:
```python
def counter():
    if not hasattr(counter, 'count'):
        counter.count = 0
    counter.count += 1
    print(f"Called {counter.count} times")
```

### Global Variables
```c
int global_count = 0;  // Visible to all functions in this file

void increment(void)
{
    global_count++;
}
```

**Best practice:** Minimize global variables. They make code hard to reason about and test.

### The `static` Keyword on Global Variables

```c
static int internal_counter = 0;  // Only visible in this file
```

This creates **file scope** — the variable cannot be accessed from other source files. This is C's way of implementing encapsulation.

## Function Pointers (Preview)

Functions live in memory too. You can store their addresses:
```c
#include <stdio.h>

int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }

int main(void)
{
    int (*operation)(int, int);  // Declare function pointer

    operation = add;
    printf("5 + 3 = %d\n", operation(5, 3));  // 8

    operation = sub;
    printf("5 - 3 = %d\n", operation(5, 3));  // 2

    return 0;
}
```

**Read the declaration:** `operation` is a pointer (`*`) to a function (`(...)`) that takes two `int`s and returns an `int`.

## Practice Problems

### Problem 4.1: Maximum of Two
Write a function `int max(int a, int b)` that returns the larger of two integers.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int max(int a, int b)
{
    return (a > b) ? a : b;
}

int main(void)
{
    printf("Max of 10 and 20: %d\n", max(10, 20));
    return 0;
}
```
</details>

### Problem 4.2: Fibonacci Comparison
Write both recursive and iterative versions of Fibonacci. Time them for `n = 30, 35, 40`. Explain the performance difference.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <time.h>

// Recursive (inefficient)
int fib_recursive(int n)
{
    if (n <= 1) return n;
    return fib_recursive(n - 1) + fib_recursive(n - 2);
}

// Iterative (efficient)
int fib_iterative(int n)
{
    if (n <= 1) return n;
    int a = 0, b = 1, temp;
    for (int i = 2; i <= n; i++) {
        temp = a + b;
        a = b;
        b = temp;
    }
    return b;
}

int main(void)
{
    clock_t start;
    int n = 40;

    start = clock();
    printf("Recursive fib(%d) = %d\n", n, fib_recursive(n));
    printf("Time: %.3f seconds\n", (double)(clock() - start) / CLOCKS_PER_SEC);

    start = clock();
    printf("Iterative fib(%d) = %d\n", n, fib_iterative(n));
    printf("Time: %.6f seconds\n", (double)(clock() - start) / CLOCKS_PER_SEC);

    return 0;
}
```

**Explanation:** The recursive version has exponential time complexity O(2^n) because it recomputes the same values repeatedly. The iterative version is O(n) with O(1) space.
</details>

### Problem 4.3: Swap That Fails
Write a function `void swap_wrong(int a, int b)` and demonstrate that it fails to swap values in `main`. Draw a memory diagram explaining why.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

void swap_wrong(int a, int b)
{
    int temp = a;
    a = b;
    b = temp;
    printf("Inside swap: a=%d, b=%d\n", a, b);
}

int main(void)
{
    int x = 5, y = 10;
    printf("Before swap: x=%d, y=%d\n", x, y);
    swap_wrong(x, y);
    printf("After swap: x=%d, y=%d\n", x, y);  // Unchanged!
    return 0;
}
```

**Memory diagram:**
```
main's frame:          swap_wrong's frame:
  x = 5 (addr 1000)     a = 5 (addr 2000)  ← COPY of x
  y = 10 (addr 1004)    b = 10 (addr 2004) ← COPY of y
                        temp = 5 (addr 2008)

After swap_wrong executes:
  a = 10, b = 5 (at addresses 2000, 2004)
  But x and y at 1000, 1004 are UNCHANGED!
```

**The fix:** Use pointers (Module 6).
</details>

### Problem 4.4: Static Counter
Write a function that returns how many times it has been called, using a static local variable.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int call_count(void)
{
    static int count = 0;  // Initialized only ONCE
    return ++count;
}

int main(void)
{
    for (int i = 0; i < 5; i++) {
        printf("Call %d\n", call_count());
    }
    return 0;
}
```
</details>

---

> **Professor's Note**: Functions in C are simpler than in Python — no default arguments, no keyword arguments, no type hints (though you can use comments). But this simplicity forces discipline. The pass-by-value rule is the foundation upon which pointers (Module 6) are built. Understanding why `swap_wrong` fails is more important than memorizing syntax.
