# Module 18: `<string.h>` — Comprehensive String Manipulation

## The String Header You Cannot Live Without

Every C program that handles text needs `<string.h>`. It contains ~20 functions for copying, comparing, searching, and measuring strings. **You must master these.**

---

## String Length: `strlen`

```c
size_t strlen(const char *s);
```

**Time complexity:** O(n) — scans until `\0`

```c
char str[] = "Hello";
printf("%zu\n", strlen(str));  // 5 (not counting \0)

// Common idiom: iterate with strlen
for (size_t i = 0; i < strlen(str); i++) {  // INEFFICIENT! strlen called every iteration
    // ...
}

// Better: cache the length
size_t len = strlen(str);
for (size_t i = 0; i < len; i++) {  // Efficient
    // ...
}
```

**⚠️ Trap:** `strlen` on a non-null-terminated array = **infinite loop / segfault**.

---

## String Copying

### `strcpy` — The Dangerous Classic
```c
char *strcpy(char *dest, const char *src);
```

```c
char dest[10];
strcpy(dest, "Hello World!");  // BUFFER OVERFLOW! 12 chars into 10-byte buffer
```

**Never use `strcpy` unless you KNOW the source fits!**

### `strncpy` — The "Safer" One (With Caveats)
```c
char *strncpy(char *dest, const char *src, size_t n);
```

```c
char dest[10];
strncpy(dest, "Hello World!", sizeof(dest) - 1);
dest[sizeof(dest) - 1] = '\0';  // CRITICAL: strncpy might not null-terminate!
```

**The `strncpy` trap:** If `src` is shorter than `n`, `strncpy` **pads with nulls** to fill `n` bytes. This is wasteful. If `src` is longer than `n`, it copies `n` bytes but **does NOT null-terminate**.

### The RECOMMENDED Approach: `snprintf`
```c
char dest[10];
snprintf(dest, sizeof(dest), "%s", "Hello World!");  // Always null-terminates!
// Result: "Hello Wor" + \0
```

`snprintf` is the safest way to copy strings in C. It always null-terminates and never overflows.

### `strlcpy` — The Ideal Function (BSD/Linux, not standard C)
```c
size_t strlcpy(char *dest, const char *src, size_t size);
```

Copies at most `size-1` bytes and ALWAYS null-terminates. Returns the length of `src` (so you can detect truncation).

```c
char dest[10];
size_t needed = strlcpy(dest, "Hello World!", sizeof(dest));
if (needed >= sizeof(dest)) {
    printf("String was truncated! Needed %zu, had %zu\n", needed, sizeof(dest));
}
```

**Note:** `strlcpy` is not in standard C (it's in BSD). You may need to implement it yourself or use platform-specific headers.

---

## String Concatenation

### `strcat` — Also Dangerous
```c
char *strcat(char *dest, const char *src);
```

```c
char buf[10] = "Hello";
strcat(buf, " World!");  // Buffer overflow! "Hello World!" = 12 chars
```

### `strncat` — Safer, but Tricky
```c
char *strncat(char *dest, const char *src, size_t n);
```

```c
char buf[20] = "Hello";
strncat(buf, " World!", sizeof(buf) - strlen(buf) - 1);
// Appends at most (remaining space - 1) chars, always null-terminates
```

### The Safe Way: `snprintf` Again
```c
char buf[20] = "Hello";
snprintf(buf + strlen(buf), sizeof(buf) - strlen(buf), "%s", " World!");
```

---

## String Comparison

### `strcmp` — Lexicographic Comparison
```c
int strcmp(const char *s1, const char *s2);
```

```c
strcmp("apple", "banana");   // Negative (apple < banana)
strcmp("hello", "hello");    // Zero (equal)
strcmp("zebra", "apple");    // Positive (zebra > apple)
```

**Returns:**
- `< 0` if `s1` < `s2`
- `0` if `s1` == `s2`
- `> 0` if `s1` > `s2`

### `strncmp` — Compare at Most n Characters
```c
int strncmp(const char *s1, const char *s2, size_t n);
```

```c
strncmp("apple pie", "apple juice", 5);  // 0 (first 5 chars match: "apple")
```

**Use case:** Checking prefixes, comparing fixed-width fields.

### `strcasecmp` / `strncasecmp` — Case-Insensitive (POSIX, not standard C)
```c
strcasecmp("Hello", "hello");  // 0 (equal, ignoring case)
```

---

## String Searching

### `strchr` — Find First Character
```c
char *strchr(const char *s, int c);
```

```c
char str[] = "Hello, World!";
char *p = strchr(str, 'W');
if (p != NULL) {
    printf("Found at position: %ld\n", p - str);  // 7
    printf("Remaining: %s\n", p);  // "World!"
}
```

### `strrchr` — Find Last Character
```c
char *p = strrchr("/usr/local/bin", '/');
// p points to last '/', so p+1 = "bin"
```

### `strstr` — Find Substring
```c
char *strstr(const char *haystack, const char *needle);
```

```c
char str[] = "The quick brown fox";
char *p = strstr(str, "brown");
if (p != NULL) {
    printf("Found at position: %ld\n", p - str);  // 10
}
```

### `strpbrk` — Find Any Character from Set
```c
char *strpbrk(const char *s, const char *accept);
```

```c
char str[] = "Hello, World! 123";
char *p = strpbrk(str, "0123456789");
// p points to '1' in "123"
```

### `strspn` / `strcspn` — Span/Complement Span
```c
size_t strspn(const char *s, const char *accept);    // Length of initial segment matching accept
size_t strcspn(const char *s, const char *reject);   // Length until any reject char found
```

```c
char str[] = "12345abc";
strspn(str, "0123456789");   // 5 ("12345" are all digits)
strcspn(str, "abc");         // 5 (first 'a' is at index 5)
```

**Use case:** Parsing — skip digits, then process letters.

### `strtok` — Tokenize a String (Destructive!)
```c
char *strtok(char *str, const char *delim);
```

```c
char str[] = "Hello,World,This,Is,C";  // MUST be mutable!
char *token = strtok(str, ",");

while (token != NULL) {
    printf("%s\n", token);
    token = strtok(NULL, ",");  // Pass NULL to continue
}
// Output: Hello, World, This, Is, C
```

**⚠️ DANGERS:**
1. **Modifies the original string** (replaces delimiters with `\0`)
2. **Not thread-safe** — uses internal static state
3. **Cannot handle empty tokens** (consecutive delimiters are treated as one)

### `strtok_r` — Reentrant/Thread-Safe Version (POSIX)
```c
char *strtok_r(char *str, const char *delim, char **saveptr);
```

```c
char str[] = "Hello,World,,C";
char *saveptr;
char *token = strtok_r(str, ",", &saveptr);

while (token != NULL) {
    printf("Token: '%s'\n", token);  // Can handle empty tokens!
    token = strtok_r(NULL, ",", &saveptr);
}
```

---

## Memory Operations (Also in `<string.h>`)

These work on raw bytes, not just strings:

### `memcpy` — Copy Memory Block
```c
void *memcpy(void *dest, const void *src, size_t n);
```

```c
int src[5] = {1, 2, 3, 4, 5};
int dest[5];
memcpy(dest, src, sizeof(src));  // Copies 20 bytes
```

**⚠️ Overlapping memory = undefined behavior!**

### `memmove` — Copy with Overlap Support
```c
void *memmove(void *dest, const void *src, size_t n);
```

```c
char str[] = "Hello, World!";
memmove(str + 7, str, 5);  // Overlapping copy is OK
// Result: "Hello, Hello!"
```

**Always use `memmove` when regions might overlap.**

### `memcmp` — Compare Memory Blocks
```c
int memcmp(const void *s1, const void *s2, size_t n);
```

```c
int a[5] = {1, 2, 3, 4, 5};
int b[5] = {1, 2, 3, 4, 6};
memcmp(a, b, sizeof(a));  // Negative (5 < 6 at last byte)
```

### `memset` — Fill Memory with Byte
```c
void *memset(void *s, int c, size_t n);
```

```c
int arr[100];
memset(arr, 0, sizeof(arr));  // Zero all bytes

// ⚠️ WRONG way to set all ints to 1:
memset(arr, 1, sizeof(arr));  // Sets each BYTE to 1, not each int!
// arr[0] becomes 0x01010101 = 16843009, not 1!
```

### `memchr` — Find Byte in Memory
```c
void *memchr(const void *s, int c, size_t n);
```

```c
char data[] = {0x00, 0x01, 0x02, 0x03, 0x04};
char *p = memchr(data, 0x03, sizeof(data));
// p points to data[3]
```

---

## Error Strings: `strerror`

```c
char *strerror(int errnum);
```

```c
#include <errno.h>

FILE *fp = fopen("nonexistent.txt", "r");
if (fp == NULL) {
    printf("Error: %s\n", strerror(errno));
    // Output: "Error: No such file or directory"
}
```

---

## Practice Problems

### Problem 18.1: Implement `strcpy` Using Pointers
Write your own `strcpy` without using array indexing.

<details>
<summary>Solution</summary>

```c
char *my_strcpy(char *dest, const char *src)
{
    char *orig = dest;
    while ((*dest++ = *src++) != '\0');
    return orig;
}
```
</details>

### Problem 18.2: Count Words in a String
Write a function that counts words (space-separated) in a string without modifying it.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <ctype.h>

int count_words(const char *str)
{
    int count = 0;
    int in_word = 0;

    while (*str) {
        if (isspace((unsigned char)*str)) {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            count++;
        }
        str++;
    }

    return count;
}

int main(void)
{
    printf("Words: %d\n", count_words("  Hello   World  This  Is  C  "));  // 5
    return 0;
}
```
</details>

### Problem 18.3: Safe String Copy Function
Implement a function that safely copies a string, always null-terminates, and reports truncation.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <string.h>

typedef enum { OK, TRUNCATED } CopyResult;

CopyResult safe_copy(char *dest, const char *src, size_t size)
{
    if (size == 0) return TRUNCATED;

    size_t i;
    for (i = 0; i < size - 1 && src[i] != '\0'; i++) {
        dest[i] = src[i];
    }
    dest[i] = '\0';

    return (src[i] == '\0') ? OK : TRUNCATED;
}

int main(void)
{
    char buf[10];
    CopyResult r = safe_copy(buf, "Hello World!", sizeof(buf));
    printf("Result: %s, String: '%s'\n",
           r == OK ? "OK" : "TRUNCATED", buf);
    return 0;
}
```
</details>

---

> **Professor's Note**: String handling is where most C bugs and security vulnerabilities originate. `strcpy` and `strcat` are banned in secure code. Always know your buffer sizes. Prefer `snprintf` for safe string operations. And never forget: C strings are just byte arrays ending in `\0` — no magic, no safety net.
