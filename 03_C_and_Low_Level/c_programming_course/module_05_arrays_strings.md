# Module 5: Arrays & Strings

## Arrays: Contiguous Memory Blocks

An array is a **contiguous block of memory** storing elements of the **same type**.

```c
int scores[5] = {90, 85, 78, 92, 88};
```

**Memory layout:**
```
Address:  1000  1004  1008  1012  1016
Value:      90    85    78    92    88
Index:       0     1     2     3     4
```

Each `int` occupies 4 bytes (typically), so the addresses are 4 bytes apart. The array name `scores` is essentially a pointer to the first element (address 1000).

### Array Declaration and Initialization

```c
// Method 1: Declare then initialize
int arr[5];
arr[0] = 10;
arr[1] = 20;
// ... etc

// Method 2: Initialize at declaration
int arr[5] = {10, 20, 30, 40, 50};

// Method 3: Let compiler count elements
int arr[] = {10, 20, 30, 40, 50};  // Compiler infers size 5

// Method 4: Partial initialization (rest are zero)
int arr[5] = {10, 20};  // {10, 20, 0, 0, 0}

// Method 5: All zeros
int arr[5] = {0};  // {0, 0, 0, 0, 0}
```

### Array Indexing

```c
int arr[5] = {10, 20, 30, 40, 50};
printf("%d\n", arr[0]);   // 10
printf("%d\n", arr[4]);   // 50
```

**CRITICAL WARNING:** C does NOT perform bounds checking!
```c
int arr[5] = {10, 20, 30, 40, 50};
printf("%d\n", arr[10]);  // COMPILES! But reads garbage/crashes
arr[10] = 999;             // COMPILES! But corrupts memory!
```

This is called a **buffer overflow** — one of the most common and dangerous security vulnerabilities in C programs.

### Arrays and Functions

When you pass an array to a function, something subtle happens:

```c
void print_array(int arr[], int size)
{
    // 'arr' here is actually a POINTER to the first element!
    printf("sizeof(arr) inside function: %zu\n", sizeof(arr));  // 8 (pointer size), not 20!
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}
```

**This is called "array decay"** — the array "decays" into a pointer to its first element when passed to a function. The function loses all knowledge of the array's size. This is why you MUST pass the size as a separate parameter.

**Python comparison:**
```python
def print_list(lst):
    # Python lists know their own length
    for item in lst:
        print(item)
    print(f"Length: {len(lst)}")  # Works!
```

```c
void print_array(int arr[], int size)
{
    // C arrays don't know their length
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    // Cannot determine size from arr alone!
}
```

### Multidimensional Arrays

```c
int matrix[3][4] = {
    {1, 2, 3, 4},
    {5, 6, 7, 8},
    {9, 10, 11, 12}
};

printf("%d\n", matrix[1][2]);  // 7
```

**Memory layout:** Stored in **row-major order** (all of row 0, then all of row 1, etc.):
```
Address: 1000  1004  1008  1012  1016  1020  1024  1028  ...
Value:      1     2     3     4     5     6     7     8   ...
            ↑ row 0 ↑         ↑ row 1 ↑
```

When passing 2D arrays to functions, you MUST specify the column dimension:
```c
void print_matrix(int rows, int cols, int matrix[][4])  // cols must be known!
{
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            printf("%d ", matrix[i][j]);
        }
        printf("\n");
    }
}
```

## Strings in C

**There is no string type in C.** A string is a null-terminated array of characters.

```c
char name[] = "Alice";  // Compiler creates: {'A', 'l', 'i', 'c', 'e', '\0'}
```

**Memory layout:**
```
Address:  1000  1001  1002  1003  1004  1005
Value:    'A'   'l'   'i'   'c'   'e'   '\0'
Index:      0     1     2     3     4     5
```

The null terminator `\0` (ASCII value 0) marks the end of the string. Without it, string functions don't know where the string ends.

### String Declaration Methods

```c
// Method 1: Array notation (modifiable copy)
char str1[] = "Hello";      // 6 bytes: 'H','e','l','l','o','\0'
str1[0] = 'J';              // OK! str1 becomes "Jello"

// Method 2: Pointer notation (read-only!)
char *str2 = "Hello";       // Points to string literal in read-only memory
// str2[0] = 'J';           // UNDEFINED BEHAVIOR! Likely segfault.

// Method 3: Explicit size
char str3[20] = "Hello";    // 20 bytes allocated, only 6 used
str3[0] = 'J';              // OK
```

**Critical distinction:**
- `char str[] = "Hello"` → Creates a **mutable copy** on the stack
- `char *str = "Hello"` → Creates a **pointer** to read-only memory

### String Functions from `<string.h>`

| Function | Purpose | Danger Level |
|----------|---------|-------------|
| `strlen(s)` | Returns length (not counting `\0`) | Safe |
| `strcpy(dest, src)` | Copies `src` to `dest` | **DANGEROUS** — no bounds check |
| `strncpy(dest, src, n)` | Copies at most `n` chars | Safer, but tricky |
| `strcat(dest, src)` | Appends `src` to `dest` | **DANGEROUS** — no bounds check |
| `strncat(dest, src, n)` | Appends at most `n` chars | Safer |
| `strcmp(a, b)` | Compares strings lexicographically | Safe |
| `strncmp(a, b, n)` | Compares at most `n` chars | Safe |
| `strchr(s, c)` | Finds first occurrence of `c` | Safe |
| `strstr(haystack, needle)` | Finds substring | Safe |

### `strcpy` — The Dangerous Classic

```c
char dest[10];
char *src = "This is a very long string";
strcpy(dest, src);  // BUFFER OVERFLOW! Writes past dest[9]
```

**Never use `strcpy` without ensuring the destination is large enough!**

### Safer Alternatives

```c
// Using strncpy (but be careful!)
char dest[10];
strncpy(dest, src, sizeof(dest) - 1);
dest[sizeof(dest) - 1] = '\0';  // strncpy might not null-terminate!

// Or use snprintf (RECOMMENDED)
snprintf(dest, sizeof(dest), "%s", src);  // Always null-terminates
```

### String Comparison

```c
char *s1 = "apple";
char *s2 = "banana";

if (s1 == s2) {  // WRONG! Compares addresses, not content
    // ...
}

if (strcmp(s1, s2) == 0) {  // RIGHT! Compares character by character
    // Strings are equal
}

if (strcmp(s1, s2) < 0) {   // s1 comes before s2 alphabetically
    // "apple" < "banana"
}
```

**Python comparison:**
```python
s1 = "apple"
s2 = "banana"
if s1 == s2:      # Python compares content
    pass
if s1 < s2:       # Python compares lexicographically
    pass
```

### String Length

```c
char str[] = "Hello";
size_t len = strlen(str);  // Returns 5, not 6
```

**Time complexity:** O(n) — must scan until `\0`

**Python equivalent:** `len(string)` — also O(n), but Python caches the length.

## Practice Problems

### Problem 5.1: Array Average
Declare an array of 5 floats, initialize it, and print the average.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    float scores[] = {85.5f, 90.0f, 78.5f, 92.0f, 88.0f};
    int n = sizeof(scores) / sizeof(scores[0]);
    float sum = 0.0f;

    for (int i = 0; i < n; i++) {
        sum += scores[i];
    }

    printf("Average: %.2f\n", sum / n);
    return 0;
}
```

**Note:** `sizeof(scores) / sizeof(scores[0])` is the idiomatic way to get array length. This ONLY works where the array is declared, not inside functions (where arrays decay to pointers).
</details>

### Problem 5.2: Manual String Length
Write a function `size_t my_strlen(const char *str)` that calculates string length without using `strlen`.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

size_t my_strlen(const char *str)
{
    size_t len = 0;
    while (str[len] != '\0') {
        len++;
    }
    return len;
}

// Or using pointer arithmetic:
size_t my_strlen_v2(const char *str)
{
    const char *s = str;
    while (*s != '\0') {
        s++;
    }
    return s - str;  // Pointer subtraction gives element count
}

int main(void)
{
    char str[] = "Hello, World!";
    printf("Length: %zu\n", my_strlen(str));
    printf("Length v2: %zu\n", my_strlen_v2(str));
    return 0;
}
```
</details>

### Problem 5.3: Reverse String In-Place
Write a function `void reverse_string(char *str)` that reverses a string in place (no extra array).

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <string.h>

void reverse_string(char *str)
{
    int len = strlen(str);
    for (int i = 0; i < len / 2; i++) {
        char temp = str[i];
        str[i] = str[len - 1 - i];
        str[len - 1 - i] = temp;
    }
}

int main(void)
{
    char str[] = "Hello";  // Must be mutable array, not pointer!
    printf("Before: %s\n", str);
    reverse_string(str);
    printf("After: %s\n", str);
    return 0;
}
```

**Important:** `char str[] = "Hello"` creates a mutable copy. `char *str = "Hello"` would point to read-only memory and crash.
</details>

### Problem 5.4: Matrix Transpose
Write a program that transposes a 3x3 matrix.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

#define SIZE 3

void transpose(int matrix[SIZE][SIZE])
{
    for (int i = 0; i < SIZE; i++) {
        for (int j = i + 1; j < SIZE; j++) {
            int temp = matrix[i][j];
            matrix[i][j] = matrix[j][i];
            matrix[j][i] = temp;
        }
    }
}

void print_matrix(int matrix[SIZE][SIZE])
{
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            printf("%d ", matrix[i][j]);
        }
        printf("\n");
    }
}

int main(void)
{
    int matrix[SIZE][SIZE] = {
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };

    printf("Original:\n");
    print_matrix(matrix);

    transpose(matrix);

    printf("Transposed:\n");
    print_matrix(matrix);

    return 0;
}
```
</details>

### Problem 5.5: Safe String Copy
Implement a safe version of `strcpy` that takes a destination size and never overflows.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

// Safe string copy — like strlcpy
size_t safe_strcpy(char *dest, const char *src, size_t size)
{
    size_t src_len = 0;
    while (src[src_len] != '\0') {
        src_len++;
    }

    if (size > 0) {
        size_t copy_len = (src_len >= size) ? size - 1 : src_len;
        for (size_t i = 0; i < copy_len; i++) {
            dest[i] = src[i];
        }
        dest[copy_len] = '\0';
    }

    return src_len;  // Return length of src (like strlcpy)
}

int main(void)
{
    char dest[10];
    const char *src = "Hello, World! This is too long";

    size_t needed = safe_strcpy(dest, src, sizeof(dest));
    printf("Copied: %s\n", dest);
    printf("Source length: %zu, Buffer size: %zu\n", needed, sizeof(dest));

    return 0;
}
```
</details>

---

> **Professor's Note**: Arrays and strings are where C's "honesty" becomes most apparent. Python's lists and strings are sophisticated objects with bounds checking, length tracking, and memory management. C's arrays are just raw memory. This power comes with responsibility — every buffer overflow is a potential security vulnerability. Always know your array sizes, always null-terminate strings, and never trust input lengths.
