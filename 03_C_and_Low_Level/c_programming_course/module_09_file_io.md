# Module 9: File I/O

## The FILE Pointer

In Python, files are objects with methods:
```python
with open("data.txt", "r") as f:
    content = f.read()
```

In C, files are accessed through a `FILE *` pointer — an opaque structure defined in `<stdio.h>` that contains:
- File descriptor
- Buffer information
- Current position
- Error indicators

## Opening and Closing Files

### `fopen` — Open a File
```c
FILE *fp = fopen("data.txt", "r");

if (fp == NULL) {
    perror("Error opening file");  // Prints: "Error opening file: No such file or directory"
    return 1;
}

// ... use fp ...

fclose(fp);  // ALWAYS close files when done!
```

**Mode strings:**
| Mode | Meaning | File must exist? | Truncates? |
|------|---------|-----------------|------------|
| `"r"` | Read text | Yes | No |
| `"w"` | Write text | No | Yes (creates or overwrites) |
| `"a"` | Append text | No | No (creates if needed) |
| `"r+"` | Read/Write | Yes | No |
| `"w+"` | Read/Write | No | Yes |
| `"a+"` | Read/Append | No | No |
| `"rb"` | Read binary | Yes | No |
| `"wb"` | Write binary | No | Yes |

**Binary mode (`b`) is required on Windows** to prevent newline translation (`\r\n` ↔ `\n`). On Unix-like systems, it's optional but good practice.

### `fclose` — Close a File
```c
fclose(fp);
```

- Flushes any buffered output
- Releases system resources
- Returns 0 on success, EOF on error

## Text File Operations

### Reading Character by Character
```c
int ch;
while ((ch = fgetc(fp)) != EOF) {
    putchar(ch);
}
```

**Why `int` for `ch`?** Because `EOF` is typically `-1`, and `char` might be unsigned (0-255), making it impossible to distinguish `EOF` from the valid byte 255.

### Reading Line by Line
```c
char buffer[100];
while (fgets(buffer, sizeof(buffer), fp) != NULL) {
    printf("%s", buffer);  // fgets includes the newline
}
```

**`fgets` parameters:**
- `buffer`: Where to store the line
- `sizeof(buffer)`: Maximum characters to read (including `\0`)
- `fp`: File pointer

**Returns:** `NULL` on EOF or error.

**WARNING:** `fgets` reads at most `size-1` characters and ALWAYS null-terminates. It may leave part of a long line in the file for the next call.

### Reading Formatted Data
```c
int age;
float height;
char name[50];

// File contains: "Alice 25 1.75"
fscanf(fp, "%s %d %f", name, &age, &height);
```

**Note:** `fscanf` is dangerous with strings — it doesn't check buffer sizes. Use `%49s` to limit to 49 characters (leaving room for `\0`).

### Writing Text
```c
FILE *fp = fopen("output.txt", "w");
if (fp == NULL) return 1;

fprintf(fp, "Name: %s\n", "Alice");
fprintf(fp, "Age: %d\n", 25);
fprintf(fp, "Height: %.2f\n", 1.75);

fclose(fp);
```

## Binary File Operations

Binary I/O reads/writes raw bytes — no text interpretation, no newline conversion.

### Writing Structures to Binary Files
```c
typedef struct {
    int id;
    char name[50];
    float gpa;
} Student;

Student s = {1, "Alice", 3.8};

FILE *fp = fopen("student.bin", "wb");
if (fp == NULL) return 1;

fwrite(&s, sizeof(Student), 1, fp);  // Write 1 element of size sizeof(Student)
fclose(fp);
```

**`fwrite` parameters:**
- `&s`: Pointer to data
- `sizeof(Student)`: Size of each element
- `1`: Number of elements
- `fp`: File pointer

### Reading Structures from Binary Files
```c
Student s;
FILE *fp = fopen("student.bin", "rb");
if (fp == NULL) return 1;

fread(&s, sizeof(Student), 1, fp);
printf("ID: %d, Name: %s, GPA: %.2f\n", s.id, s.name, s.gpa);

fclose(fp);
```

**Important:** Binary files are **not portable** across different architectures due to:
- Endianness differences (little-endian vs big-endian)
- Structure padding differences
- Different `sizeof(int)` across platforms

For portable binary formats, use explicit serialization or libraries like Protocol Buffers.

## File Positioning

### `fseek` — Move to a Specific Position
```c
fseek(fp, 0, SEEK_SET);   // Go to beginning
fseek(fp, 0, SEEK_END);    // Go to end
fseek(fp, -10, SEEK_CUR);  // Go back 10 bytes from current position
fseek(fp, 100, SEEK_SET);  // Go to byte 100
```

### `ftell` — Get Current Position
```c
long pos = ftell(fp);  // Returns current byte offset
```

### `rewind` — Go to Beginning
```c
rewind(fp);  // Same as fseek(fp, 0, SEEK_SET)
```

## Error Handling

### `feof` — Check for End of File
```c
while (!feof(fp)) {  // Check BEFORE reading
    int ch = fgetc(fp);
    if (ch != EOF) {
        putchar(ch);
    }
}
```

**Warning:** `feof` only returns true AFTER a read operation has failed due to EOF. It's often better to check the return value of the read function directly.

### `ferror` — Check for Error
```c
if (ferror(fp)) {
    printf("Error reading file\n");
}
```

### `perror` — Print Error Message
```c
FILE *fp = fopen("nonexistent.txt", "r");
if (fp == NULL) {
    perror("fopen failed");  // Prints: "fopen failed: No such file or directory"
}
```

## Complete Example: Student Database

```c
#include <stdio.h>
#include <string.h>

typedef struct {
    int id;
    char name[50];
    float gpa;
} Student;

void save_students(const char *filename, Student students[], int count)
{
    FILE *fp = fopen(filename, "wb");
    if (fp == NULL) {
        perror("Cannot open file for writing");
        return;
    }

    fwrite(&count, sizeof(int), 1, fp);  // Write count first
    fwrite(students, sizeof(Student), count, fp);
    fclose(fp);
}

Student *load_students(const char *filename, int *count)
{
    FILE *fp = fopen(filename, "rb");
    if (fp == NULL) {
        perror("Cannot open file for reading");
        return NULL;
    }

    fread(count, sizeof(int), 1, fp);
    Student *students = malloc(*count * sizeof(Student));
    if (students == NULL) {
        fclose(fp);
        return NULL;
    }

    fread(students, sizeof(Student), *count, fp);
    fclose(fp);
    return students;
}

int main(void)
{
    Student class[] = {
        {1, "Alice", 3.8},
        {2, "Bob", 3.5},
        {3, "Charlie", 3.9}
    };

    save_students("class.bin", class, 3);

    int count;
    Student *loaded = load_students("class.bin", &count);
    if (loaded) {
        for (int i = 0; i < count; i++) {
            printf("%d: %s (%.2f)\n", loaded[i].id, loaded[i].name, loaded[i].gpa);
        }
        free(loaded);
    }

    return 0;
}
```

## Practice Problems

### Problem 9.1: Number Writer
Write a program that writes numbers 1 to 10 to a file, one per line.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

int main(void)
{
    FILE *fp = fopen("numbers.txt", "w");
    if (fp == NULL) {
        perror("Failed to open file");
        return 1;
    }

    for (int i = 1; i <= 10; i++) {
        fprintf(fp, "%d\n", i);
    }

    fclose(fp);
    printf("File written successfully.\n");
    return 0;
}
```
</details>

### Problem 9.2: Word Count (wc clone)
Write a program that reads a text file and counts lines, words, and characters.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <ctype.h>

int main(void)
{
    FILE *fp = fopen("input.txt", "r");
    if (fp == NULL) {
        perror("Cannot open file");
        return 1;
    }

    int lines = 0, words = 0, chars = 0;
    int ch;
    int in_word = 0;

    while ((ch = fgetc(fp)) != EOF) {
        chars++;

        if (ch == '\n') {
            lines++;
        }

        if (isspace(ch)) {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            words++;
        }
    }

    printf("Lines: %d\n", lines);
    printf("Words: %d\n", words);
    printf("Characters: %d\n", chars);

    fclose(fp);
    return 0;
}
```
</details>

### Problem 9.3: CSV Parser
Read a CSV file with student records and print them formatted.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <string.h>

typedef struct {
    char name[50];
    int age;
    float gpa;
} Student;

int main(void)
{
    FILE *fp = fopen("students.csv", "r");
    if (fp == NULL) {
        perror("Cannot open file");
        return 1;
    }

    char line[100];
    // Skip header
    fgets(line, sizeof(line), fp);

    printf("%-20s %5s %6s\n", "Name", "Age", "GPA");
    printf("--------------------------------------\n");

    while (fgets(line, sizeof(line), fp) != NULL) {
        Student s;
        sscanf(line, "%49[^,],%d,%f", s.name, &s.age, &s.gpa);
        printf("%-20s %5d %6.2f\n", s.name, s.age, s.gpa);
    }

    fclose(fp);
    return 0;
}
```

**CSV file format:**
```
Name,Age,GPA
Alice,20,3.80
Bob,21,3.50
Charlie,19,3.90
```
</details>

### Problem 9.4: Binary Student Database
Write a program that saves an array of `struct Student` to a binary file and reads it back.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int id;
    char name[50];
    float gpa;
} Student;

int main(void)
{
    // Write
    Student students[] = {
        {1, "Alice", 3.8},
        {2, "Bob", 3.5}
    };

    FILE *fp = fopen("students.bin", "wb");
    if (fp == NULL) return 1;

    int count = 2;
    fwrite(&count, sizeof(int), 1, fp);
    fwrite(students, sizeof(Student), count, fp);
    fclose(fp);

    // Read back
    fp = fopen("students.bin", "rb");
    if (fp == NULL) return 1;

    int read_count;
    fread(&read_count, sizeof(int), 1, fp);
    printf("Number of students: %d\n", read_count);

    Student s;
    for (int i = 0; i < read_count; i++) {
        fread(&s, sizeof(Student), 1, fp);
        printf("%d: %s (%.2f)\n", s.id, s.name, s.gpa);
    }

    fclose(fp);
    return 0;
}
```
</details>

---

> **Professor's Note**: File I/O in C is more explicit than in Python, but this explicitness gives you complete control. You choose between text (human-readable, portable) and binary (compact, fast). Always check for `NULL` after `fopen`. Always close files. And remember: `fgets` is your friend, `gets` is your enemy (it's been removed from C11 for being inherently unsafe).
