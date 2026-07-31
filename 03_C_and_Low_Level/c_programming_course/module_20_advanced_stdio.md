# Module 20: Advanced `<stdio.h>` — Formatted I/O, `scanf`, and Binary Patterns

## Beyond `printf` and `fopen`

You know the basics of `<stdio.h>`. Now let's master the parts you'll use every day as a professional C programmer.

---

## `printf` Format Specifiers — Complete Reference

### Integer Types
```c
printf("%d", 42);       // int (also %i)
printf("%u", 42);       // unsigned int
printf("%ld", 42L);     // long
printf("%lu", 42UL);    // unsigned long
printf("%lld", 42LL);   // long long
printf("%llu", 42ULL);  // unsigned long long
printf("%zu", sizeof(x)); // size_t
printf("%td", ptrdiff);   // ptrdiff_t (pointer difference)
```

### Floating Point
```c
printf("%f", 3.14);     // double (default)
printf("%e", 3.14);     // Scientific notation: 3.140000e+00
printf("%g", 3.14);     // Auto-select %f or %e (shorter)
printf("%a", 3.14);     // Hexadecimal float (C99)
printf("%Lf", 3.14L);   // long double
```

### Width, Precision, and Flags
```c
printf("[%10d]\n", 42);      // [        42] — right-aligned, width 10
printf("[%-10d]\n", 42);     // [42        ] — left-aligned
printf("[%010d]\n", 42);     // [0000000042] — zero-padded
printf("[%.2f]\n", 3.14159); // [3.14] — 2 decimal places
printf("[%8.2f]\n", 3.14159); // [    3.14] — width 8, 2 decimals
printf("[%-8.2f]\n", 3.14159); // [3.14    ] — left-aligned
printf("[%+d]\n", 42);        // [+42] — always show sign
printf("[% d]\n", 42);        // [ 42] — space for positive
```

### String Formatting
```c
printf("%.5s\n", "Hello World");  // "Hello" — max 5 chars
printf("%10.5s\n", "Hello World"); // "     Hello" — width 10, max 5 chars
```

### Escape Sequences
```c
\n   // Newline
\t   // Tab
\r   // Carriage return
\\   // Backslash
\"   // Double quote
\'   // Single quote
\0   // Null terminator
\a   // Bell/alert
\b   // Backspace
\f   // Form feed
\v   // Vertical tab
```

---

## `sprintf` and `snprintf` — String Formatting

### `sprintf` — DANGEROUS (No Buffer Size Check)
```c
char buf[10];
int x = 123456789;
sprintf(buf, "%d", x);  // Buffer overflow! Needs 9 chars, writes 9 + \0 = 10 (barely fits)
// But if x was larger, OVERFLOW!
```

### `snprintf` — THE SAFE WAY
```c
char buf[10];
snprintf(buf, sizeof(buf), "%d", x);  // Always null-terminates, never overflows
```

**Returns:** The number of characters that WOULD have been written (not counting `\0`), or a negative value on error.

```c
char buf[10];
int n = snprintf(buf, sizeof(buf), "Value: %d", 12345);
// n = 12 ("Value: 12345" is 12 chars)
// buf contains "Value: 123" + \0 (truncated to fit)

if (n >= sizeof(buf)) {
    printf("Truncated! Need %d bytes, have %zu\n", n + 1, sizeof(buf));
}
```

### `asprintf` — Dynamic String Allocation (GNU extension)
```c
char *str;
asprintf(&str, "Error code: %d", errno);  // Automatically allocates right size
// ... use str ...
free(str);  // Don't forget to free!
```

---

## `scanf` — The Tricky Beast

`scanf` is powerful but dangerous. Here's how to use it safely.

### Basic Usage
```c
int age;
float height;
char name[50];

scanf("%d", &age);        // Read integer
scanf("%f", &height);     // Read float
scanf("%49s", name);      // Read string (MAX 49 chars + \0)
```

**⚠️ CRITICAL:** Always pass the ADDRESS (`&`) for numeric types. For arrays (strings), the array name IS the address, so no `&` needed.

### The `%s` Trap
```c
char name[10];
scanf("%s", name);  // DANGER! No size limit. User types 100 chars = BUFFER OVERFLOW!
```

**Always specify width:**
```c
char name[50];
scanf("%49s", name);  // Safe: reads at most 49 chars
```

### Reading Lines with `scanf` (Tricky)
```c
char line[100];
scanf(" %99[^\n]", line);  // Read until newline, skip leading whitespace
```

**Explanation:**
- ` ` (space): Skip leading whitespace
- `%99[^\n]`: Read up to 99 chars that are NOT newline

### Better: `fgets` for Line Input
```c
char line[100];
if (fgets(line, sizeof(line), stdin) != NULL) {
    // Remove trailing newline if present
    size_t len = strlen(line);
    if (len > 0 && line[len - 1] == '\n') {
        line[len - 1] = '\0';
    }
    printf("You entered: %s\n", line);
}
```

### `sscanf` — Parse Strings
```c
const char *input = "Alice 25 1.75";
char name[50];
int age;
float height;

sscanf(input, "%49s %d %f", name, &age, &height);
```

**Returns:** Number of items successfully parsed, or EOF on error.

```c
int n = sscanf(input, "%49s %d %f", name, &age, &height);
if (n != 3) {
    fprintf(stderr, "Parse error: only matched %d items\n", n);
}
```

---

## Binary I/O Patterns

### Reading/Writing Arrays
```c
// Write array of 1000 doubles
FILE *fp = fopen("data.bin", "wb");
double data[1000];
// ... fill data ...
size_t written = fwrite(data, sizeof(double), 1000, fp);
if (written != 1000) {
    fprintf(stderr, "Write error\n");
}
fclose(fp);

// Read back
FILE *fp = fopen("data.bin", "rb");
double data[1000];
size_t read = fread(data, sizeof(double), 1000, fp);
if (read != 1000) {
    if (feof(fp)) {
        printf("Only %zu items read (EOF)\n", read);
    } else if (ferror(fp)) {
        fprintf(stderr, "Read error\n");
    }
}
fclose(fp);
```

### Portable Binary Serialization
For cross-platform compatibility, serialize explicitly:

```c
#include <stdint.h>

// Write int32_t in little-endian (portable)
void write_int32_le(FILE *fp, int32_t val)
{
    uint8_t bytes[4] = {
        (val >> 0) & 0xFF,
        (val >> 8) & 0xFF,
        (val >> 16) & 0xFF,
        (val >> 24) & 0xFF
    };
    fwrite(bytes, 1, 4, fp);
}

int32_t read_int32_le(FILE *fp)
{
    uint8_t bytes[4];
    fread(bytes, 1, 4, fp);
    return ((int32_t)bytes[3] << 24) |
           ((int32_t)bytes[2] << 16) |
           ((int32_t)bytes[1] << 8) |
           ((int32_t)bytes[0] << 0);
}
```

---

## Temporary Files

```c
#include <stdio.h>

FILE *tmpfile(void);  // Create anonymous temp file (deleted on close)

char *tmpnam(char *s);  // Generate unique filename (NOT secure, deprecated)

// Better (POSIX):
char template[] = "/tmp/myfileXXXXXX";
int fd = mkstemp(template);  // Creates and opens file securely
FILE *fp = fdopen(fd, "w+");
// ... use fp ...
fclose(fp);
unlink(template);  // Delete when done
```

---

## Practice Problems

### Problem 20.1: Safe User Input
Write a function that safely reads a line from stdin, handling buffer overflow and removing the newline.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <string.h>

// Returns 1 on success, 0 on EOF/error
int read_line(char *buf, size_t size)
{
    if (fgets(buf, size, stdin) == NULL) {
        return 0;
    }

    size_t len = strlen(buf);
    if (len > 0 && buf[len - 1] == '\n') {
        buf[len - 1] = '\0';  // Remove newline
    } else if (len == size - 1) {
        // Line was too long — discard rest
        int c;
        while ((c = getchar()) != '\n' && c != EOF);
    }

    return 1;
}

int main(void)
{
    char line[100];
    printf("Enter something: ");
    if (read_line(line, sizeof(line))) {
        printf("You entered: '%s'\n", line);
    }
    return 0;
}
```
</details>

### Problem 20.2: Parse CSV Line
Parse a comma-separated line into fields using `sscanf` and `%[^,]`.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <string.h>

int parse_csv(const char *line, char fields[][50], int max_fields)
{
    int count = 0;
    const char *p = line;

    while (*p && count < max_fields) {
        int n;
        if (sscanf(p, "%49[^,]", fields[count]) == 1) {
            count++;
        }

        // Skip to next comma or end
        p = strchr(p, ',');
        if (p) p++; else break;
    }

    return count;
}

int main(void)
{
    const char *line = "Alice,25,Engineer,USA";
    char fields[10][50];
    int n = parse_csv(line, fields, 10);

    for (int i = 0; i < n; i++) {
        printf("Field %d: '%s'\n", i, fields[i]);
    }

    return 0;
}
```
</details>

---

> **Professor's Note**: `printf` and `scanf` families are the most used and most misused functions in C. Master the format specifiers. Never use `sprintf` — always use `snprintf`. Never use `scanf("%s", buf)` — always specify width. And for line input, `fgets` is almost always better than `scanf`. These habits will save you from countless buffer overflows.
