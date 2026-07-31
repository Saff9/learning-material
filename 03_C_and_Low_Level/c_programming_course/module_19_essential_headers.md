# Module 19: Essential Standard Library Headers

## `<ctype.h>` — Character Classification

Every program that processes text needs these functions. They handle locales, whitespace, digits, letters, and case conversion.

### Character Testing Functions
All return non-zero (true) if the condition is met, 0 (false) otherwise.

```c
#include <ctype.h>

isalpha('A');    // Non-zero: it's a letter
isdigit('5');    // Non-zero: it's a digit
isalnum('a');    // Non-zero: letter OR digit
isspace(' ');    // Non-zero: space, tab, newline, etc.
isupper('A');    // Non-zero: uppercase letter
islower('a');    // Non-zero: lowercase letter
isprint('!');    // Non-zero: printable character
iscntrl('\n');  // Non-zero: control character
ispunct('!');    // Non-zero: punctuation
isxdigit('F');   // Non-zero: hex digit (0-9, A-F, a-f)
```

### Case Conversion
```c
toupper('a');    // Returns 'A'
tolower('Z');    // Returns 'z'
```

**⚠️ Important:** Pass `unsigned char` to these functions, not plain `char`!
```c
char c = 'A';
if (isalpha((unsigned char)c)) {  // Correct
    // ...
}
```

On systems where `char` is signed, characters with values > 127 can cause undefined behavior when passed to `ctype` functions.

### Practical Example: String Normalization
```c
#include <ctype.h>
#include <stdio.h>

void to_uppercase(char *str)
{
    while (*str) {
        *str = toupper((unsigned char)*str);
        str++;
    }
}

void to_lowercase(char *str)
{
    while (*str) {
        *str = tolower((unsigned char)*str);
        str++;
    }
}

int is_valid_identifier(const char *str)
{
    if (!str || !*str) return 0;

    // First char must be letter or underscore
    if (!isalpha((unsigned char)*str) && *str != '_') return 0;
    str++;

    // Rest can be letter, digit, or underscore
    while (*str) {
        if (!isalnum((unsigned char)*str) && *str != '_') return 0;
        str++;
    }
    return 1;
}

int main(void)
{
    char str[] = "Hello World";
    to_uppercase(str);
    printf("%s\n", str);  // "HELLO WORLD"

    printf("is_valid('var_1'): %d\n", is_valid_identifier("var_1"));  // 1
    printf("is_valid('1var'): %d\n", is_valid_identifier("1var"));    // 0

    return 0;
}
```

---

## `<math.h>` — Mathematical Functions

### Constants
```c
M_PI      // 3.14159265358979323846
M_E       // 2.71828182845904523536
M_LOG2E   // log2(e)
M_LOG10E  // log10(e)
M_LN2     // ln(2)
M_LN10    // ln(10)
M_SQRT2   // sqrt(2)
```

**Note:** These may require `#define _USE_MATH_DEFINES` on Windows before including `<math.h>`.

### Trigonometric Functions
```c
sin(x);    // Sine (x in radians)
cos(x);    // Cosine
tan(x);    // Tangent
asin(x);   // Arcsine (inverse sine)
acos(x);   // Arccosine
atan(x);   // Arctangent
atan2(y, x);  // Arctangent of y/x (handles all quadrants correctly!)
```

```c
// Convert degrees to radians
#define DEG_TO_RAD (M_PI / 180.0)
double angle = 45.0 * DEG_TO_RAD;
printf("sin(45°) = %.4f\n", sin(angle));  // 0.7071
```

### Hyperbolic Functions
```c
sinh(x);   // Hyperbolic sine
cosh(x);   // Hyperbolic cosine
tanh(x);   // Hyperbolic tangent
```

### Exponential & Logarithmic
```c
exp(x);     // e^x
log(x);     // Natural log (ln)
log10(x);   // Base-10 log
log2(x);    // Base-2 log (C99)
pow(x, y);  // x^y
sqrt(x);    // Square root
cbrt(x);    // Cube root (C99)
```

```c
// Compound interest: A = P * (1 + r/n)^(nt)
double compound_interest(double P, double r, int n, int t)
{
    return P * pow(1 + r / n, n * t);
}
```

### Rounding Functions
```c
ceil(x);    // Round up to nearest integer
floor(x);   // Round down to nearest integer
round(x);   // Round to nearest integer (away from zero on .5)
trunc(x);   // Truncate toward zero
```

```c
printf("%.1f %.1f %.1f\n", ceil(2.3), floor(2.7), round(2.5));
// Output: 3.0 2.0 3.0
```

### Other Useful Functions
```c
fabs(x);     // Absolute value for doubles
fmod(x, y);  // Floating-point remainder (like % for integers)
fdim(x, y);  // Positive difference: max(x-y, 0)
fmax(x, y);  // Maximum
fmin(x, y);  // Minimum
hypot(x, y); // sqrt(x² + y²) without overflow
```

### Floating-Point Classification (C99)
```c
#include <math.h>

double x = 0.0 / 0.0;  // NaN

if (isnan(x)) printf("Not a number\n");
if (isinf(x)) printf("Infinity\n");
if (isfinite(x)) printf("Finite\n");
if (isnormal(x)) printf("Normal (not zero, subnormal, inf, or NaN)\n");
```

---

## `<time.h>` — Date and Time

### Core Types
```c
time_t     // Calendar time (usually seconds since epoch)
clock_t    // Processor time
tm         // Broken-down time structure
```

### The `tm` Structure
```c
struct tm {
    int tm_sec;    // 0-60 (60 for leap seconds)
    int tm_min;    // 0-59
    int tm_hour;   // 0-23
    int tm_mday;   // 1-31
    int tm_mon;    // 0-11 (JANUARY IS 0!)
    int tm_year;   // Years since 1900
    int tm_wday;   // 0-6 (Sunday = 0)
    int tm_yday;   // 0-365
    int tm_isdst;  // Daylight saving flag
};
```

**⚠️ Common bug:** `tm_mon` is 0-based (January = 0), but `tm_mday` is 1-based!

### Getting Current Time
```c
#include <stdio.h>
#include <time.h>

int main(void)
{
    time_t now = time(NULL);  // Get current calendar time
    printf("Seconds since epoch: %ld\n", (long)now);

    // Convert to local time
    struct tm *local = localtime(&now);
    printf("Local: %04d-%02d-%02d %02d:%02d:%02d\n",
           local->tm_year + 1900,
           local->tm_mon + 1,  // Add 1 because tm_mon is 0-based!
           local->tm_mday,
           local->tm_hour,
           local->tm_min,
           local->tm_sec);

    // Convert to UTC/GMT
    struct tm *utc = gmtime(&now);

    // Format as string
    char buf[100];
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", local);
    printf("Formatted: %s\n", buf);

    return 0;
}
```

### `strftime` Format Specifiers
| Specifier | Meaning | Example |
|-----------|---------|---------|
| `%Y` | Year (4 digits) | 2026 |
| `%m` | Month (01-12) | 07 |
| `%d` | Day (01-31) | 19 |
| `%H` | Hour (00-23) | 14 |
| `%M` | Minute (00-59) | 30 |
| `%S` | Second (00-60) | 45 |
| `%A` | Full weekday | Sunday |
| `%B` | Full month | July |
| `%p` | AM/PM | PM |
| `%Z` | Timezone | UTC, PST |

### Measuring Elapsed Time
```c
#include <time.h>

clock_t start = clock();
// ... do work ...
clock_t end = clock();

double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
printf("Elapsed: %.4f seconds\n", elapsed);
```

**Note:** `clock()` measures CPU time, not wall-clock time. For wall-clock time, use `time()` or `gettimeofday()` (POSIX).

### Sleeping
```c
#include <unistd.h>  // POSIX

sleep(5);      // Sleep for 5 seconds
usleep(500000); // Sleep for 500,000 microseconds (0.5 seconds)
```

---

## `<errno.h>` — Error Handling

```c
#include <errno.h>
```

`errno` is a global integer that system calls and library functions set when they fail.

### Common Error Codes
| Code | Meaning |
|------|---------|
| `EPERM` | Operation not permitted |
| `ENOENT` | No such file or directory |
| `EINTR` | Interrupted system call |
| `EIO` | I/O error |
| `ENOMEM` | Out of memory |
| `EACCES` | Permission denied |
| `EINVAL` | Invalid argument |
| `ERANGE` | Result too large |

### Proper Error Handling Pattern
```c
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

FILE *safe_fopen(const char *path, const char *mode)
{
    errno = 0;  // Clear before call
    FILE *fp = fopen(path, mode);

    if (fp == NULL) {
        fprintf(stderr, "Failed to open '%s': %s (errno=%d)\n",
                path, strerror(errno), errno);
        return NULL;
    }

    return fp;
}
```

---

## `<assert.h>` — Assertions for Debugging

```c
#include <assert.h>

assert(condition);
```

If `condition` is false, the program prints an error message and aborts.

```c
void divide(int a, int b)
{
    assert(b != 0);  // Programmer error if b is 0
    printf("%d\n", a / b);
}
```

**When to use assertions:**
- Internal invariants ("this should never happen")
- Pre/post-conditions on functions
- Debugging builds only

**When NOT to use:**
- User input validation (use normal error handling)
- Runtime errors that could actually happen

**Disable assertions in release builds:**
```bash
gcc -DNDEBUG -o program program.c  # assert() becomes a no-op
```

### Static Assertions (C11)
```c
_Static_assert(sizeof(int) == 4, "int must be 4 bytes");
```

Compile-time check. If the condition is false, compilation fails with the message.

---

## `<limits.h>` & `<float.h>` — Type Limits

### Integer Limits (`<limits.h>`)
```c
CHAR_BIT    // Bits in a char (usually 8)
CHAR_MIN    // Minimum char value
CHAR_MAX    // Maximum char value
SCHAR_MIN   // Minimum signed char
SCHAR_MAX   // Maximum signed char
UCHAR_MAX   // Maximum unsigned char
SHRT_MIN    // Minimum short
SHRT_MAX    // Maximum short
USHRT_MAX   // Maximum unsigned short
INT_MIN     // Minimum int (-2147483648)
INT_MAX     // Maximum int (2147483647)
UINT_MAX    // Maximum unsigned int
LONG_MIN    // Minimum long
LONG_MAX    // Maximum long
LLONG_MIN   // Minimum long long
LLONG_MAX   // Maximum long long
```

```c
#include <stdio.h>
#include <limits.h>

int main(void)
{
    printf("int range: %d to %d\n", INT_MIN, INT_MAX);
    printf("long long range: %lld to %lld\n", LLONG_MIN, LLONG_MAX);
    return 0;
}
```

### Floating-Point Limits (`<float.h>`)
```c
FLT_MIN     // Minimum positive float
FLT_MAX     // Maximum float
FLT_EPSILON // Smallest x where 1.0 + x != 1.0
DBL_MIN     // Minimum positive double
DBL_MAX     // Maximum double
DBL_EPSILON // Smallest x where 1.0 + x != 1.0
```

```c
#include <float.h>
#include <stdio.h>

int main(void)
{
    printf("Float epsilon: %.10e\n", FLT_EPSILON);
    printf("Double epsilon: %.20e\n", DBL_EPSILON);
    return 0;
}
```

**Use case:** Comparing floating-point numbers:
```c
#include <math.h>

#define EPSILON 1e-9

int double_equals(double a, double b)
{
    return fabs(a - b) < EPSILON;
}
```

---

## Practice Problems

### Problem 19.1: Validate Password
Write a function that checks if a password is strong (at least 8 chars, contains uppercase, lowercase, digit, and special character).

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <ctype.h>
#include <string.h>

typedef enum { WEAK, STRONG } PasswordStrength;

PasswordStrength check_password(const char *pwd)
{
    if (strlen(pwd) < 8) return WEAK;

    int has_upper = 0, has_lower = 0, has_digit = 0, has_special = 0;

    for (const char *p = pwd; *p; p++) {
        if (isupper((unsigned char)*p)) has_upper = 1;
        else if (islower((unsigned char)*p)) has_lower = 1;
        else if (isdigit((unsigned char)*p)) has_digit = 1;
        else if (ispunct((unsigned char)*p)) has_special = 1;
    }

    return (has_upper && has_lower && has_digit && has_special) ? STRONG : WEAK;
}

int main(void)
{
    printf("'Hello1!': %s\n", check_password("Hello1!") == STRONG ? "STRONG" : "WEAK");
    printf("'hello': %s\n", check_password("hello") == STRONG ? "STRONG" : "WEAK");
    return 0;
}
```
</details>

### Problem 19.2: Calculate Age from Birth Date
Given a birth year, month, and day, calculate the current age accurately.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <time.h>

int calculate_age(int birth_year, int birth_month, int birth_day)
{
    time_t now = time(NULL);
    struct tm *today = localtime(&now);

    int age = today->tm_year + 1900 - birth_year;

    // Adjust if birthday hasn't occurred yet this year
    if (today->tm_mon + 1 < birth_month ||
        (today->tm_mon + 1 == birth_month && today->tm_mday < birth_day)) {
        age--;
    }

    return age;
}

int main(void)
{
    printf("Age: %d\n", calculate_age(1998, 7, 19));
    return 0;
}
```
</details>

### Problem 19.3: Floating-Point Comparison
Write a robust function to compare two doubles for equality, handling edge cases (NaN, infinity).

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <math.h>
#include <float.h>

int double_equal(double a, double b)
{
    // Handle NaN
    if (isnan(a) && isnan(b)) return 1;
    if (isnan(a) || isnan(b)) return 0;

    // Handle infinities
    if (isinf(a) && isinf(b)) return (a > 0) == (b > 0);
    if (isinf(a) || isinf(b)) return 0;

    // Relative comparison for large numbers, absolute for small
    double diff = fabs(a - b);
    double max_val = fmax(fabs(a), fabs(b));

    return diff <= DBL_EPSILON * fmax(1.0, max_val);
}

int main(void)
{
    printf("0.1+0.2 == 0.3: %d\n", double_equal(0.1 + 0.2, 0.3));  // Should be 1
    printf("1.0 == 1.0: %d\n", double_equal(1.0, 1.0));              // 1
    return 0;
}
```
</details>

---

> **Professor's Note**: These headers are the tools you'll reach for daily. `<ctype.h>` for text processing, `<math.h>` for calculations, `<time.h>` for timestamps and profiling, `<errno.h>` for robust error handling, and `<assert.h>` for catching your own bugs. Memorize the common functions — they are the vocabulary of C programming.
