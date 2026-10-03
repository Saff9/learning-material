# Module 2: Data Types, Variables & Operators

## The Philosophy of Types in C

In Python, types are **dynamic** and **checked at runtime**:
```python
x = 5        # x is an int
x = "hello"  # Now x is a string — perfectly fine!
```

In C, types are **static** and **checked at compile time**:
```c
int x = 5;     // x is forever an int in this scope
x = "hello";   // COMPILE ERROR: cannot assign char* to int
```

**Why this rigidity?** Because C maps directly to hardware. When the compiler sees `int x`, it knows to allocate exactly 4 bytes (typically) and use integer CPU instructions. This predictability is what makes C fast and suitable for systems programming.

## Primitive Data Types

### Integer Types

| Type | Typical Size | Range (signed) | Use Case |
|------|-------------|----------------|----------|
| `char` | 1 byte | -128 to 127 | Characters, small integers |
| `short` | 2 bytes | -32,768 to 32,767 | Small integers |
| `int` | 4 bytes | -2,147,483,648 to 2,147,483,647 | General-purpose integers |
| `long` | 4 or 8 bytes | Platform-dependent | Large integers |
| `long long` | 8 bytes | -9 quintillion to +9 quintillion | Very large integers |

**Important:** These sizes are **platform-dependent**! The C standard only guarantees:
- `sizeof(char)` == 1
- `sizeof(short)` <= `sizeof(int)` <= `sizeof(long)` <= `sizeof(long long)`

### Fixed-Width Types (Recommended)

For portable code, use types from `<stdint.h>`:
```c
#include <stdint.h>

int32_t  exactly_32_bits;    // Guaranteed 32 bits, signed
uint64_t exactly_64_bits;    // Guaranteed 64 bits, unsigned
uint8_t  exactly_8_bits;     // Perfect for raw bytes
```

### Signed vs Unsigned

```c
int a = -5;          // Signed: can be negative
unsigned int b = 5;  // Unsigned: only positive, range doubled
```

**Warning:** Mixing signed and unsigned in comparisons causes bugs:
```c
int a = -1;
unsigned int b = 1;
if (a < b) {
    printf("-1 < 1\n");
} else {
    printf("-1 >= 1 ???\n");  // This prints! Because -1 becomes a huge unsigned number
}
```

### Floating-Point Types

| Type | Size | Precision | Use Case |
|------|------|-----------|----------|
| `float` | 4 bytes | ~7 digits | Graphics, when memory matters |
| `double` | 8 bytes | ~15 digits | Scientific computing, default choice |
| `long double` | 8-16 bytes | Extended precision | Special numerical work |

```c
float pi_approx = 3.14159f;   // 'f' suffix makes it a float literal
double pi_precise = 3.141592653589793;
```

Without the `f` suffix, `3.14159` is a `double` by default. Assigning it to a `float` causes an implicit conversion.

## Variable Declaration and Initialization

### Declaration
```c
int age;           // Declares an int variable named 'age'
float height;      // Declares a float
char initial;      // Declares a char
```

**CRITICAL:** In C, uninitialized variables contain **garbage values** — whatever was previously in that memory location. Unlike Python, which raises `NameError` if you use an undefined variable, C will happily use the garbage value.

```c
int x;
printf("%d\n", x);  // Prints garbage! Could be 0, could be -858993460, could be anything
```

### Initialization
```c
int age = 25;              // Best practice: declare and initialize
float height = 5.9f;
char grade = 'A';
```

### Multiple Declarations
```c
int a = 1, b = 2, c = 3;  // OK
int x, y, z;
x = y = z = 0;            // OK: assignment returns the assigned value
```

## Constants

### `const` Qualifier
```c
const int MAX_USERS = 100;  // Cannot be modified after initialization
// MAX_USERS = 200;         // COMPILE ERROR
```

`const` means "read-only." It tells the compiler to prevent modification. However, `const` variables still consume memory and can technically be modified through pointers (don't do this).

### `#define` Macros
```c
#define PI 3.14159
#define MAX_BUFFER_SIZE 1024
```

The preprocessor does **text substitution**. Every occurrence of `PI` is replaced with `3.14159` before compilation. No type checking, no memory allocated.

**When to use what:**
- Use `const` for typed constants that need scope
- Use `#define` for simple, global constants and configuration values

### `enum` — Enumerated Types
```c
enum Color { RED, GREEN, BLUE };
enum Color my_color = RED;  // RED = 0, GREEN = 1, BLUE = 2

// Or with explicit values:
enum Status { OK = 200, NOT_FOUND = 404, ERROR = 500 };
```

## Operators

### Arithmetic Operators
```c
int a = 10, b = 3;
int sum = a + b;     // 13
int diff = a - b;    // 7
int prod = a * b;    // 30
int quot = a / b;    // 3  (INTEGER DIVISION!)
int rem = a % b;     // 1  (modulo)
```

**Integer Division Trap:**
```c
int result = 5 / 2;       // result = 2 (not 2.5!)
double wrong = 5 / 2;     // wrong = 2.0 (still integer division!)
double right = 5.0 / 2;   // right = 2.5 (floating-point division)
double also_right = (double)5 / 2;  // Explicit cast
```

### Increment and Decrement
```c
int i = 5;
int a = ++i;  // Pre-increment: i becomes 6, a = 6
int b = i++;  // Post-increment: b = 6, then i becomes 7
```

**Python equivalent:**
```python
i = 5
a = i = i + 1  # Pre-increment equivalent
b = i; i = i + 1  # Post-increment equivalent
```

### Relational and Logical Operators
```c
int a = 5, b = 10;

// Relational
a == b   // Equal to
a != b   // Not equal to
a < b    // Less than
a > b    // Greater than
a <= b   // Less than or equal
a >= b   // Greater than or equal

// Logical
(a < b) && (a > 0)   // AND — both must be true
(a < b) || (a > 100) // OR — at least one true
!(a == b)            // NOT — negation
```

**Python vs C comparison:**
| Python | C |
|--------|---|
| `and` | `&&` |
| `or` | `\|\|` |
| `not` | `!` |
| `==` | `==` |
| `!=` | `!=` |

### Bitwise Operators

C provides direct bit manipulation — essential for systems programming:

```c
unsigned int a = 5;   // Binary: 0000...0101
unsigned int b = 3;   // Binary: 0000...0011

a & b    // AND:  0000...0001 = 1
a | b    // OR:   0000...0111 = 7
a ^ b    // XOR:  0000...0110 = 6
~a       // NOT:  1111...1010 (bitwise complement)
a << 1   // Left shift:  0000...1010 = 10
a >> 1   // Right shift: 0000...0010 = 2
```

**Common bit manipulation patterns:**
```c
// Set bit n
x |= (1 << n);

// Clear bit n
x &= ~(1 << n);

// Toggle bit n
x ^= (1 << n);

// Check bit n
if (x & (1 << n)) { /* bit is set */ }

// Clear lowest set bit
x &= (x - 1);
```

### Assignment Operators
```c
int x = 10;
x += 5;   // x = x + 5
x -= 3;   // x = x - 3
x *= 2;   // x = x * 2
x /= 4;   // x = x / 4
x %= 3;   // x = x % 3
x &= 1;   // x = x & 1
x |= 2;   // x = x | 2
x ^= 4;   // x = x ^ 4
x <<= 1;  // x = x << 1
x >>= 1;  // x = x >> 1
```

### Ternary Operator
```c
int max = (a > b) ? a : b;  // If a > b, max = a, else max = b
```
**Python equivalent:** `max = a if a > b else b`

### The Comma Operator
```c
int x = (1, 2, 3);  // x = 3 (evaluates left-to-right, returns rightmost)
```
Rarely used, but appears in `for` loops occasionally.

## Type Conversion (Casting)

### Implicit Conversion (Automatic)
```c
int i = 5;
double d = i + 2.5;  // i is promoted to double before addition
```

C promotes smaller types to larger types automatically in expressions:
```
char → short → int → long → long long
float → double → long double
```

### Explicit Conversion (Casting)
```c
int a = 5, b = 2;
double result = (double)a / b;  // Cast 'a' to double, forcing floating-point division
```

**Warning:** Casting can lose information:
```c
double pi = 3.14159;
int approx = (int)pi;  // approx = 3 (truncated, not rounded!)
```

## The `sizeof` Operator

`sizeof` returns the size in bytes of a type or variable:
```c
printf("sizeof(char) = %zu\n", sizeof(char));      // Always 1
printf("sizeof(int) = %zu\n", sizeof(int));        // Typically 4
printf("sizeof(long) = %zu\n", sizeof(long));      // 4 or 8
printf("sizeof(double) = %zu\n", sizeof(double));  // Typically 8
printf("sizeof(void*) = %zu\n", sizeof(void*));    // 4 (32-bit) or 8 (64-bit)
```

**Always use `sizeof` instead of hardcoding sizes:**
```c
int arr[10];
// WRONG: malloc(10 * 4)  // Assumes int is 4 bytes
// RIGHT: malloc(10 * sizeof(int))  // Portable and correct
```

## Practice Problems

### Problem 2.1: Variable Practice
Declare variables for your height in meters (float), birth year (int), and first initial (char). Print them with appropriate format specifiers.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    float height = 1.75f;
    int birth_year = 1998;
    char initial = 'J';

    printf("Height: %.2f meters\n", height);
    printf("Birth Year: %d\n", birth_year);
    printf("Initial: %c\n", initial);

    return 0;
}
```
</details>

### Problem 2.2: Swap Without Temporary Variable
Write a program that swaps two integers without using a temporary variable. Implement both the arithmetic method and the XOR method.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    int a = 5, b = 10;

    // Method 1: Arithmetic
    a = a + b;  // a = 15
    b = a - b;  // b = 5
    a = a - b;  // a = 10
    printf("After arithmetic swap: a=%d, b=%d\n", a, b);

    // Method 2: XOR (works only for integers)
    int x = 5, y = 10;
    x = x ^ y;
    y = x ^ y;
    x = x ^ y;
    printf("After XOR swap: x=%d, y=%d\n", x, y);

    return 0;
}
```

**Note:** The arithmetic method can overflow. The XOR method is clever but rarely used in production. The standard approach uses a temporary variable.
</details>

### Problem 2.3: Integer Overflow Investigation
Investigate what happens when you assign a `long long` value larger than `INT_MAX` to an `int`. Print both values and explain.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <limits.h>

int main(void)
{
    printf("INT_MAX = %d\n", INT_MAX);
    printf("INT_MIN = %d\n", INT_MIN);

    long long big = 3000000000LL;  // 3 billion, larger than INT_MAX (2.147 billion)
    int truncated = (int)big;

    printf("Original long long: %lld\n", big);
    printf("Truncated to int: %d\n", truncated);

    // Unsigned overflow demonstration
    unsigned int u = UINT_MAX;
    printf("UINT_MAX = %u\n", u);
    u = u + 1;
    printf("UINT_MAX + 1 = %u (wraps to 0!)\n", u);

    return 0;
}
```

**Explanation:** When a value too large for `int` is assigned, the bits are truncated. This is called **integer overflow** and results in **undefined behavior** for signed integers. For unsigned integers, it wraps around modulo 2^n.
</details>

### Problem 2.4: Temperature Converter
Write a program that converts Celsius to Fahrenheit and vice versa. Use `const` for the conversion factors.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    const double C_TO_F_FACTOR = 9.0 / 5.0;
    const double C_TO_F_OFFSET = 32.0;

    double celsius = 25.0;
    double fahrenheit = celsius * C_TO_F_FACTOR + C_TO_F_OFFSET;

    printf("%.1f°C = %.1f°F\n", celsius, fahrenheit);

    fahrenheit = 98.6;
    celsius = (fahrenheit - C_TO_F_OFFSET) / C_TO_F_FACTOR;
    printf("%.1f°F = %.1f°C\n", fahrenheit, celsius);

    return 0;
}
```
</details>

---

> **Professor's Note**: Understanding data types is foundational. In Python, you rarely think about how many bytes an integer consumes. In C, this is a constant consideration. The size of your types affects memory usage, performance, and correctness. Always use `sizeof`, prefer fixed-width types for portable code, and be vigilant about integer overflow.
