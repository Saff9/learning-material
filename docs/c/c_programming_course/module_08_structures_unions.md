# Module 8: Structures & Unions

## Why Structures?

In Python, you group related data using dictionaries or classes:
```python
student = {
    "name": "Alice",
    "age": 20,
    "gpa": 3.8
}
```

In C, you use `struct` to group related variables under one name:
```c
struct Student {
    char name[50];
    int age;
    float gpa;
};
```

## Defining and Using Structures

### Basic Structure
```c
#include <stdio.h>
#include <string.h>

struct Student {
    char name[50];
    int age;
    float gpa;
};

int main(void)
{
    // Method 1: Declare then initialize members
    struct Student s1;
    strcpy(s1.name, "Alice");  // Cannot assign strings directly!
    s1.age = 20;
    s1.gpa = 3.8;

    // Method 2: Initialize at declaration
    struct Student s2 = {"Bob", 21, 3.5};

    // Method 3: Designated initializers (C99)
    struct Student s3 = {
        .name = "Charlie",
        .age = 19,
        .gpa = 3.9
    };

    printf("%s is %d years old with GPA %.2f\n", s1.name, s1.age, s1.gpa);
    return 0;
}
```

## The `typedef` Shortcut

Typing `struct Student` everywhere is tedious. Use `typedef`:

```c
typedef struct {
    char name[50];
    int age;
    float gpa;
} Student;

// Now you can use just 'Student'
Student s1;
Student s2 = {"Alice", 20, 3.8};
```

**Alternative style (common in libraries):**
```c
typedef struct Student {
    char name[50];
    int age;
    float gpa;
} Student;
// Both 'struct Student' and 'Student' work
```

## Pointers to Structures

```c
Student s1 = {"Alice", 20, 3.8};
Student *ptr = &s1;

// Accessing members through pointer:
printf("%s\n", (*ptr).name);   // Dereference, then access member
printf("%s\n", ptr->name);    // Arrow operator: cleaner syntax
```

**The arrow operator `->` is syntactic sugar for `(*ptr).member`.** Always prefer `->` for pointers.

## Structures and Functions

### Pass by Value (Copies the entire structure!)
```c
void print_student(Student s)  // Copies all fields!
{
    printf("%s, %d, %.2f\n", s.name, s.age, s.gpa);
}
```

**Problem:** For large structures, this is expensive. A `Student` with a 50-byte name array copies 50 + 4 + 4 = 58 bytes.

### Pass by Pointer (Efficient)
```c
void print_student(const Student *s)  // Pass pointer, don't modify
{
    printf("%s, %d, %.2f\n", s->name, s->age, s->gpa);
}

void birthday(Student *s)  // Will modify
{
    s->age++;
}
```

**Best practice:** Always pass structures by pointer, using `const` when you don't intend to modify.

## Arrays of Structures

```c
Student class[30];  // Array of 30 students

class[0].age = 20;
strcpy(class[0].name, "Alice");

// Initialize at declaration
Student class[] = {
    {"Alice", 20, 3.8},
    {"Bob", 21, 3.5},
    {"Charlie", 19, 3.9}
};
```

## Nested Structures

```c
typedef struct {
    int day;
    int month;
    int year;
} Date;

typedef struct {
    char name[50];
    Date birth_date;
    float gpa;
} Student;

Student s = {"Alice", {15, 3, 2000}, 3.8};
printf("Born: %d/%d/%d\n", s.birth_date.day, s.birth_date.month, s.birth_date.year);
```

## Self-Referential Structures (Linked Lists)

A structure can contain a pointer to itself:
```c
typedef struct Node {
    int data;
    struct Node *next;  // Pointer to another Node
} Node;
```

**Why `struct Node *next` and not `Node *next`?**
Because at the point of declaration, `Node` is not yet fully defined. The compiler only knows about `struct Node` at this point.

## Memory Alignment and Padding

Structures are padded to align members on appropriate boundaries for performance:

```c
struct Example {
    char c;    // 1 byte
    int i;     // 4 bytes (aligned to 4-byte boundary)
    char d;    // 1 byte
};
```

**Actual memory layout:**
```
Offset:  0    1    2    3    4    5    6    7    8    9   10   11
Value:   c    pad  pad  pad    i    i    i    i    d    pad  pad  pad
Size: 1 byte + 3 bytes padding + 4 bytes + 1 byte + 3 bytes padding = 12 bytes
```

**Expected:** 1 + 4 + 1 = 6 bytes
**Actual:** 12 bytes (due to alignment)

Check with:
```c
printf("sizeof(struct Example) = %zu\n", sizeof(struct Example));
```

**Pack structures** (use sparingly — hurts performance):
```c
#pragma pack(push, 1)  // Pack tightly, no padding
struct Packed {
    char c;
    int i;
    char d;
};
#pragma pack(pop)
// sizeof(struct Packed) = 6
```

## Unions

A `union` is like a `struct`, but all members share the **same memory**. Its size equals its largest member.

```c
union Data {
    int i;
    float f;
    char str[20];
};

union Data d;
d.i = 10;       // Access as integer
printf("%d\n", d.i);  // 10
d.f = 3.14f;    // Overwrites the same memory!
printf("%d\n", d.i);  // Garbage! (same bytes interpreted as int)
```

**Use cases:**
1. **Memory-efficient storage** when you only need one of several types at a time
2. **Type punning** (viewing the same bytes as different types)
3. **Hardware register access** (different fields overlay the same hardware register)

### Tagged Union (Discriminated Union)
```c
typedef enum { INT, FLOAT, STRING } DataType;

typedef struct {
    DataType type;
    union {
        int i;
        float f;
        char str[20];
    } value;
} Variant;

Variant v;
v.type = INT;
v.value.i = 42;
```

## Bit Fields

Store data in individual bits within a structure:
```c
struct Flags {
    unsigned int flag1 : 1;  // 1 bit
    unsigned int flag2 : 1;  // 1 bit
    unsigned int flag3 : 1;  // 1 bit
    unsigned int value : 5;  // 5 bits (0-31)
};
```

**Use case:** Hardware registers, protocol headers, memory-constrained systems.

## Practice Problems

### Problem 8.1: Point Structure
Define a `struct Point` with `x` and `y` coordinates. Write a function to calculate the distance between two points.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <math.h>

typedef struct {
    double x;
    double y;
} Point;

double distance(Point a, Point b)
{
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return sqrt(dx * dx + dy * dy);
}

int main(void)
{
    Point p1 = {0.0, 0.0};
    Point p2 = {3.0, 4.0};
    printf("Distance: %.2f\n", distance(p1, p2));  // 5.00
    return 0;
}
```
</details>

### Problem 8.2: Book Database
Create a `struct Book` with title, author, and year. Make an array of 3 books and print them.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <string.h>

typedef struct {
    char title[100];
    char author[50];
    int year;
} Book;

void print_book(const Book *b)
{
    printf(""%s" by %s (%d)\n", b->title, b->author, b->year);
}

int main(void)
{
    Book library[] = {
        {"The C Programming Language", "K&R", 1988},
        {"Clean Code", "Robert Martin", 2008},
        {"Design Patterns", "Gang of Four", 1994}
    };

    int n = sizeof(library) / sizeof(library[0]);
    for (int i = 0; i < n; i++) {
        print_book(&library[i]);
    }

    return 0;
}
```
</details>

### Problem 8.3: Linked List Node
Implement a linked list node using `struct Node { int data; struct Node *next; };`. Create a list of 3 nodes manually and print their values.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node *next;
} Node;

int main(void)
{
    // Create nodes on the heap
    Node *first = malloc(sizeof(Node));
    Node *second = malloc(sizeof(Node));
    Node *third = malloc(sizeof(Node));

    first->data = 10;
    first->next = second;

    second->data = 20;
    second->next = third;

    third->data = 30;
    third->next = NULL;

    // Traverse and print
    Node *current = first;
    while (current != NULL) {
        printf("%d -> ", current->data);
        current = current->next;
    }
    printf("NULL\n");

    // Free memory
    free(first);
    free(second);
    free(third);

    return 0;
}
```
</details>

### Problem 8.4: Union Size Investigation
Create a union with `int`, `float`, and `char[4]`. Set the integer to a known value, then print the bytes as characters to observe endianness.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>

union EndianTest {
    int i;
    char c[4];
};

int main(void)
{
    union EndianTest e;
    e.i = 0x12345678;  // Hex: 12 34 56 78

    printf("Bytes: ");
    for (int i = 0; i < 4; i++) {
        printf("%02x ", (unsigned char)e.c[i]);
    }
    printf("\n");

    // On little-endian systems (x86): 78 56 34 12
    // On big-endian systems: 12 34 56 78

    if (e.c[0] == 0x78) {
        printf("Little-endian system\n");
    } else {
        printf("Big-endian system\n");
    }

    return 0;
}
```

**Explanation:** On little-endian systems, the least significant byte is stored at the lowest address. On big-endian, the most significant byte is stored first. This matters for network protocols and binary file formats.
</details>

---

> **Professor's Note**: Structures are C's way of creating composite data types. They are the foundation of all data structures in C — linked lists, trees, hash tables, and more. Understanding memory layout, alignment, and padding is crucial for systems programming and performance optimization. The `->` operator will become second nature with practice.
