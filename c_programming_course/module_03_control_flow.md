# Module 3: Control Flow

## Making Decisions: The `if` Statement

In Python, indentation defines blocks. In C, **curly braces `{}`** define blocks.

```python
# Python
if score >= 90:
    print("A")
elif score >= 80:
    print("B")
else:
    print("C")
```

```c
// C
if (score >= 90) {
    printf("A\n");
} else if (score >= 80) {
    printf("B\n");
} else {
    printf("C\n");
}
```

### The Dangling Else Problem

```c
if (condition1)
    if (condition2)
        statement1;
    else
        statement2;  // This else pairs with the INNER if!
```

**Always use braces** to avoid ambiguity:
```c
if (condition1) {
    if (condition2) {
        statement1;
    }
} else {
    statement2;
}
```

### The `if` Assignment Trap

A classic C bug that Python protects you from:
```c
int x = 5;
if (x = 0) {    // BUG! This assigns 0 to x, then checks if x is truthy
    printf("x is non-zero\n");
}
printf("x = %d\n", x);  // Prints: x = 0
```

In C, the assignment `x = 0` evaluates to the assigned value (`0`), which is "falsy." The `if` body doesn't execute, but `x` has been modified!

**Python prevents this:** `if x = 0:` is a syntax error in Python.

**Defense:** Some programmers write `if (0 == x)` instead of `if (x == 0)`. If you accidentally type `=` instead of `==`, the compiler catches it because you can't assign to a literal.

## The `switch` Statement

Python added `match` in 3.10. C has had `switch` for decades. It is a **jump table** — often more efficient than a chain of `if-else` for integer constants.

```c
#include <stdio.h>

int main(void)
{
    int day = 3;

    switch (day) {
        case 1:
            printf("Monday\n");
            break;  // CRITICAL: Without break, execution "falls through"
        case 2:
            printf("Tuesday\n");
            break;
        case 3:
            printf("Wednesday\n");
            break;
        case 4:
            printf("Thursday\n");
            break;
        case 5:
            printf("Friday\n");
            break;
        case 6:
        case 7:
            printf("Weekend!\n");
            break;  // Both 6 and 7 fall through to here
        default:
            printf("Invalid day\n");
            break;
    }

    return 0;
}
```

### How `switch` Works Internally

The compiler generates a **jump table** — an array of addresses indexed by the case values. For `switch(day)`, it computes `jump_table[day]` and jumps directly to that address. This is O(1), whereas `if-else` chains are O(n).

**Limitations:**
- Case values must be **integer constants** (or constant expressions)
- Cannot use ranges (e.g., `case 1..5:` is invalid)
- Cannot use strings

### Intentional Fall-Through

Sometimes fall-through is useful:
```c
switch (grade) {
    case 'A':
    case 'B':
    case 'C':
        printf("Passing grade\n");
        break;
    case 'D':
    case 'F':
        printf("Failing grade\n");
        break;
}
```

## Loops

### The `while` Loop

```c
int i = 0;
while (i < 5) {
    printf("%d\n", i);
    i++;
}
```

**Python equivalent:**
```python
i = 0
while i < 5:
    print(i)
    i += 1
```

### The `for` Loop

C's `for` loop is more flexible than Python's:

```c
for (int i = 0; i < 5; i++) {
    printf("%d\n", i);
}
```

**Structure:** `for (initialization; condition; update)`

The compiler translates this into equivalent `while` logic:
```c
int i = 0;
while (i < 5) {
    printf("%d\n", i);
    i++;
}
```

**Multiple variables:**
```c
for (int i = 0, j = 10; i < j; i++, j--) {
    printf("i=%d, j=%d\n", i, j);
}
```

**Infinite loop:**
```c
for (;;) {
    // Runs forever (until break or return)
}
```

### The `do-while` Loop

Guarantees at least one execution:

```c
int i = 0;
do {
    printf("%d\n", i);
    i++;
} while (i < 0);  // Condition is false, but loop ran once!
```

**Use case:** Menu systems where you want to show the menu at least once:
```c
int choice;
do {
    printf("1. Play\n");
    printf("2. Settings\n");
    printf("3. Quit\n");
    printf("Enter choice: ");
    scanf("%d", &choice);
} while (choice != 3);
```

## Loop Control: `break` and `continue`

### `break` — Exit the Loop
```c
for (int i = 0; i < 100; i++) {
    if (i == 42) {
        break;  // Exit loop immediately
    }
    printf("%d\n", i);
}
```

### `continue` — Skip to Next Iteration
```c
for (int i = 0; i < 10; i++) {
    if (i % 2 == 0) {
        continue;  // Skip even numbers
    }
    printf("%d\n", i);  // Only prints odd numbers
}
```

## The Comma Operator in Loops

```c
for (int i = 0, sum = 0; i < 10; sum += i, i++) {
    printf("i=%d, sum=%d\n", i, sum);
}
```

The comma operator evaluates left-to-right and returns the rightmost value. Here, `sum += i` executes before `i++` in each iteration's update step.

## Nested Loops and Complexity

```c
// Print a multiplication table
for (int i = 1; i <= 10; i++) {
    for (int j = 1; j <= 10; j++) {
        printf("%4d", i * j);
    }
    printf("\n");
}
```

## Practice Problems

### Problem 3.1: Even Numbers
Print all even numbers from 1 to 20 using a `for` loop.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    for (int i = 2; i <= 20; i += 2) {
        printf("%d ", i);
    }
    printf("\n");
    return 0;
}
```
</details>

### Problem 3.2: Sum of Digits
Write a program that takes an integer and prints the sum of its digits (e.g., 123 -> 6).

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    int n = 12345;
    int sum = 0;

    while (n > 0) {
        sum += n % 10;  // Get last digit
        n /= 10;        // Remove last digit
    }

    printf("Sum of digits: %d\n", sum);
    return 0;
}
```

**How it works:**
- `12345 % 10 = 5` (last digit)
- `12345 / 10 = 1234` (remove last digit via integer division)
- Repeat until `n` becomes 0
</details>

### Problem 3.3: Collatz Conjecture
Given a positive integer `n`, follow these rules:
- If `n` is even: `n = n / 2`
- If `n` is odd: `n = 3 * n + 1`

Repeat until `n` becomes 1. Print the sequence and count the steps.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    int n = 27;  // Famous test case: takes 111 steps
    int steps = 0;

    printf("Sequence: %d", n);
    while (n != 1) {
        if (n % 2 == 0) {
            n = n / 2;
        } else {
            n = 3 * n + 1;
        }
        printf(" -> %d", n);
        steps++;
    }
    printf("\nSteps: %d\n", steps);

    return 0;
}
```

**Mathematical note:** The Collatz conjecture states this always reaches 1, but this has never been proven for all positive integers!
</details>

### Problem 3.4: Prime Number Checker
Write a program that checks if a number is prime. Optimize by only checking up to the square root.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

bool is_prime(int n)
{
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;

    // Only check up to square root
    for (int i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) {
            return false;
        }
    }
    return true;
}

int main(void)
{
    int num = 97;
    if (is_prime(num)) {
        printf("%d is prime\n", num);
    } else {
        printf("%d is not prime\n", num);
    }
    return 0;
}
```

**Optimization explanation:** If `n` has a factor greater than its square root, it must also have a corresponding factor less than the square root. So we only need to check up to `sqrt(n)`.
</details>

### Problem 3.5: Pattern Printing
Print this pattern:
```
    *
   ***
  *****
 *******
*********
```

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    int n = 5;
    for (int i = 1; i <= n; i++) {
        // Print spaces
        for (int j = 1; j <= n - i; j++) {
            printf(" ");
        }
        // Print stars
        for (int k = 1; k <= 2 * i - 1; k++) {
            printf("*");
        }
        printf("\n");
    }
    return 0;
}
```
</details>

---

> **Professor's Note**: Control flow in C is straightforward but requires discipline. The `switch` fall-through behavior is a common source of bugs — always question whether you need `break`. The `for` loop's flexibility is powerful but can lead to unreadable code if overused. When in doubt, prefer clarity over cleverness.
