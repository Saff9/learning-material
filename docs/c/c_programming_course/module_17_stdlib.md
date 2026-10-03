# Module 17: `<stdlib.h>` — The General Utilities Library

## Why This Header Matters

`<stdlib.h>` is arguably the second most important header after `<stdio.h>`. It contains functions for:
- **Memory allocation** (`malloc`, `calloc`, `realloc`, `free`)
- **String conversion** (`atoi`, `atol`, `atof`, `strtol`, `strtod`)
- **Random numbers** (`rand`, `srand`)
- **Searching & sorting** (`bsearch`, `qsort`)
- **Environment & process control** (`getenv`, `exit`, `system`, `abort`)
- **Integer arithmetic** (`abs`, `labs`, `div`)

You will use functions from this header in **every single C program** you write.

---

## Memory Allocation (Review + Deep Dive)

You already know these from Module 7, but let's look at them with the full context of `<stdlib.h>`.

### `malloc` — Allocate Uninitialized Memory
```c
void *malloc(size_t size);
```

```c
int *arr = malloc(10 * sizeof(int));
if (arr == NULL) {
    fprintf(stderr, "malloc failed\n");
    exit(EXIT_FAILURE);  // Clean exit with error code
}
```

### `calloc` — Allocate Zero-Initialized Memory
```c
void *calloc(size_t nmemb, size_t size);
```

```c
// Allocate 100 integers, all initialized to 0
int *counts = calloc(100, sizeof(int));

// Perfect for frequency counting:
counts[42]++;  // Safe, because all start at 0
```

**When to use `calloc` over `malloc`:**
- Counting arrays (frequency tables)
- Boolean flag arrays
- Anytime you need zero-initialized memory
- **Security note:** `calloc` is safer because it prevents reading uninitialized data

### `realloc` — Resize Allocated Memory
```c
void *realloc(void *ptr, size_t size);
```

```c
int *arr = malloc(5 * sizeof(int));
// ... later need more space ...
int *new_arr = realloc(arr, 10 * sizeof(int));

if (new_arr == NULL) {
    // realloc failed, but arr is STILL VALID!
    free(arr);
    exit(EXIT_FAILURE);
}
arr = new_arr;
```

**Critical rule:** Always assign `realloc`'s return value to a temporary pointer first. If it fails, you don't lose the original pointer.

### `free` — Deallocate Memory
```c
void free(void *ptr);
```

```c
free(ptr);
ptr = NULL;  // Defensive programming
```

**What happens if you `free(NULL)`?** Nothing. It's safe. This is why setting pointers to NULL after free is a good habit.

---

## String Conversion

These functions convert strings to numbers. **They are essential** when reading numeric input from files, command-line arguments, or user input.

### The Dangerous Ones (Avoid When Possible)

```c
int atoi(const char *str);      // "123" → 123
long atol(const char *str);     // "123" → 123L
double atof(const char *str);   // "3.14" → 3.14
```

**Why dangerous?** They have **NO error checking**:
```c
int x = atoi("not_a_number");  // Returns 0 — but is it really zero?
int y = atoi("999999999999");  // Overflow — undefined behavior!
```

### The Safe Ones (Always Use These)

```c
long strtol(const char *str, char **endptr, int base);
double strtod(const char *str, char **endptr);
unsigned long strtoul(const char *str, char **endptr, int base);
```

**`strtol` explained:**
- `str`: The string to convert
- `endptr`: Points to the first invalid character (set to NULL if you don't care)
- `base`: Number base (2-36, or 0 for auto-detect)

```c
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <limits.h>

int safe_atoi(const char *str, int *result)
{
    char *endptr;
    errno = 0;  // Clear errno before call

    long val = strtol(str, &endptr, 10);

    // Check for conversion errors
    if (errno == ERANGE) {
        fprintf(stderr, "Value out of range\n");
        return -1;
    }

    // Check if entire string was consumed
    if (*endptr != '\0') {
        fprintf(stderr, "Invalid characters: %s\n", endptr);
        return -1;
    }

    // Check if value fits in int
    if (val > INT_MAX || val < INT_MIN) {
        fprintf(stderr, "Value doesn't fit in int\n");
        return -1;
    }

    *result = (int)val;
    return 0;
}

int main(void)
{
    const char *input = "42";
    int num;

    if (safe_atoi(input, &num) == 0) {
        printf("Successfully parsed: %d\n", num);
    }

    return 0;
}
```

**Parsing different bases:**
```c
strtol("1010", NULL, 2);   // Binary → 10
strtol("FF", NULL, 16);    // Hex → 255
strtol("077", NULL, 8);    // Octal → 63
strtol("0x1A", NULL, 0);   // Auto-detect → 26 (detects 0x prefix)
```

---

## Random Numbers

```c
int rand(void);           // Returns pseudo-random integer (0 to RAND_MAX)
void srand(unsigned int seed);  // Seed the random number generator
```

```c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main(void)
{
    // Seed with current time (call ONCE at program start)
    srand(time(NULL));

    // Random integer 0 to 99
    int r = rand() % 100;
    printf("Random: %d\n", r);

    // Random float 0.0 to 1.0
    double f = (double)rand() / RAND_MAX;
    printf("Random float: %.4f\n", f);

    // Random in range [min, max]
    int min = 10, max = 50;
    int in_range = min + rand() % (max - min + 1);

    return 0;
}
```

**⚠️ Warning:** `rand()` is **not cryptographically secure**. For security (passwords, tokens), use OS-specific APIs like `getrandom()` (Linux) or `CryptGenRandom` (Windows).

---

## Searching & Sorting

### `qsort` — Quick Sort

```c
void qsort(void *base, size_t nmemb, size_t size,
           int (*compar)(const void *, const void *));
```

You saw this in Module 11. Here's a more practical example:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char name[50];
    int age;
} Person;

// Compare by age (ascending)
int compare_by_age(const void *a, const void *b)
{
    const Person *pa = a;
    const Person *pb = b;
    return pa->age - pb->age;  // Negative if a < b
}

// Compare by name (alphabetical)
int compare_by_name(const void *a, const void *b)
{
    const Person *pa = a;
    const Person *pb = b;
    return strcmp(pa->name, pb->name);
}

int main(void)
{
    Person people[] = {
        {"Charlie", 25},
        {"Alice", 30},
        {"Bob", 20}
    };
    int n = sizeof(people) / sizeof(people[0]);

    qsort(people, n, sizeof(Person), compare_by_age);
    // Now sorted by age: Bob(20), Charlie(25), Alice(30)

    qsort(people, n, sizeof(Person), compare_by_name);
    // Now sorted by name: Alice, Bob, Charlie

    return 0;
}
```

### `bsearch` — Binary Search

```c
void *bsearch(const void *key, const void *base,
              size_t nmemb, size_t size,
              int (*compar)(const void *, const void *));
```

**Requires sorted array!**

```c
int numbers[] = {10, 20, 30, 40, 50};
int key = 30;
int *found = bsearch(&key, numbers, 5, sizeof(int), compare_ints);

if (found != NULL) {
    printf("Found %d at index %ld\n", *found, found - numbers);
} else {
    printf("Not found\n");
}
```

**Time complexity:** O(log n) — much faster than linear search for large arrays.

---

## Integer Arithmetic

### `abs` / `labs` / `llabs` — Absolute Value
```c
int abs(int x);
long labs(long x);
long long llabs(long long x);
```

### `div` / `ldiv` — Division with Remainder
```c
div_t div(int numer, int denom);
```

```c
div_t result = div(17, 5);
printf("Quotient: %d, Remainder: %d\n", result.quot, result.rem);
// Output: Quotient: 3, Remainder: 2
```

**Why use `div` instead of `/` and `%`?** On some systems, `div` is more efficient because it computes both in one CPU instruction.

---

## Environment & Process Control

### `getenv` — Read Environment Variables
```c
char *getenv(const char *name);
```

```c
char *path = getenv("PATH");
if (path != NULL) {
    printf("PATH = %s\n", path);
}

char *home = getenv("HOME");
char *user = getenv("USER");
```

**Common use:** Configuration via environment variables instead of hardcoding values.

### `exit` / `atexit` — Program Termination
```c
void exit(int status);           // Normal termination, calls atexit handlers
void _Exit(int status);          // Immediate termination, no cleanup
void abort(void);                // Abnormal termination (SIGABRT)
int atexit(void (*func)(void));  // Register function to call on exit
```

```c
void cleanup(void)
{
    printf("Cleaning up before exit...\n");
}

int main(void)
{
    atexit(cleanup);  // Register cleanup function

    // ... do work ...

    exit(EXIT_SUCCESS);  // Calls cleanup(), then exits
}
```

**Exit codes:**
- `EXIT_SUCCESS` (0) — Program succeeded
- `EXIT_FAILURE` (1) — Program failed

### `system` — Execute Shell Command
```c
int system(const char *command);
```

```c
system("ls -la");           // List files
system("clear");            // Clear screen
int status = system("./other_program");  // Run another program
```

**⚠️ Security warning:** Never use `system()` with user input — it's a command injection vulnerability!

---

## Practice Problems

### Problem 17.1: Safe Number Parser
Write a program that reads a string and safely converts it to a `double`, handling all error cases.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <math.h>

int safe_atod(const char *str, double *result)
{
    char *endptr;
    errno = 0;

    *result = strtod(str, &endptr);

    if (errno == ERANGE) {
        fprintf(stderr, "Value out of range\n");
        return -1;
    }
    if (*endptr != '\0') {
        fprintf(stderr, "Invalid trailing characters\n");
        return -1;
    }
    return 0;
}

int main(void)
{
    const char *tests[] = {"3.14159", "-2.5", "abc", "1e309", "42.0abc"};

    for (int i = 0; i < 5; i++) {
        double val;
        printf("Parsing '%s': ", tests[i]);
        if (safe_atod(tests[i], &val) == 0) {
            printf("%.4f\n", val);
        } else {
            printf("FAILED\n");
        }
    }

    return 0;
}
```
</details>

### Problem 17.2: Random Array Shuffle
Create an array of numbers 1-52, shuffle them randomly (Fisher-Yates), and print.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void shuffle(int *arr, int n)
{
    for (int i = n - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}

int main(void)
{
    srand(time(NULL));

    int deck[52];
    for (int i = 0; i < 52; i++) deck[i] = i + 1;

    shuffle(deck, 52);

    for (int i = 0; i < 52; i++) {
        printf("%2d ", deck[i]);
        if ((i + 1) % 13 == 0) printf("\n");
    }

    return 0;
}
```
</details>

### Problem 17.3: Sort Students by GPA
Create an array of students, sort by GPA descending using `qsort`.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char name[50];
    float gpa;
} Student;

int compare_gpa_desc(const void *a, const void *b)
{
    const Student *sa = a;
    const Student *sb = b;

    if (sa->gpa > sb->gpa) return -1;
    if (sa->gpa < sb->gpa) return 1;
    return strcmp(sa->name, sb->name);
}

int main(void)
{
    Student class[] = {
        {"Alice", 3.8},
        {"Bob", 3.5},
        {"Charlie", 3.9},
        {"Diana", 3.8}
    };
    int n = sizeof(class) / sizeof(class[0]);

    qsort(class, n, sizeof(Student), compare_gpa_desc);

    for (int i = 0; i < n; i++) {
        printf("%s: %.2f\n", class[i].name, class[i].gpa);
    }

    return 0;
}
```
</details>

---

> **Professor's Note**: `<stdlib.h>` is your Swiss Army knife. Master `strtol` over `atoi`, always check `malloc`'s return value, and understand that `qsort`/`bsearch` are your friends for array operations. These functions separate hobbyist C programmers from professionals.
