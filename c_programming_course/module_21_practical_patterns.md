# Module 21: Practical C Patterns & Idioms

## Patterns You'll Use Every Day

This module teaches you the idiomatic ways to solve common problems in C. These are the patterns that experienced C programmers reach for automatically.

---

## Pattern 1: Resource Acquisition Is Initialization (RAII-like)

C doesn't have destructors, but you can use `goto` for cleanup:

```c
int process_file(const char *path)
{
    FILE *fp = NULL;
    char *buffer = NULL;
    int result = -1;

    fp = fopen(path, "r");
    if (fp == NULL) {
        perror("fopen");
        goto cleanup;
    }

    buffer = malloc(1024);
    if (buffer == NULL) {
        fprintf(stderr, "Out of memory\n");
        goto cleanup;
    }

    // ... do work ...
    result = 0;  // Success

cleanup:
    if (buffer) free(buffer);
    if (fp) fclose(fp);
    return result;
}
```

**Why `goto` here is good:** It centralizes cleanup, prevents code duplication, and makes resource management obvious. This is the ONE valid use of `goto` in C.

---

## Pattern 2: Opaque Pointers / Information Hiding

Hide implementation details from users of your library:

**list.h** (Public interface)
```c
#ifndef LIST_H
#define LIST_H

typedef struct List List;  // Opaque type — users can't see inside

List *list_create(void);
void list_destroy(List *list);
void list_append(List *list, int value);
int list_get(const List *list, size_t index);
size_t list_size(const List *list);

#endif
```

**list.c** (Private implementation)
```c
#include "list.h"
#include <stdlib.h>

struct Node {
    int data;
    struct Node *next;
};

struct List {
    struct Node *head;
    size_t size;
};

List *list_create(void)
{
    List *list = calloc(1, sizeof(List));
    return list;
}

// ... rest of implementation ...
```

**Users of `list.h` cannot access `list->head` directly** — they must use the API. This is C's version of encapsulation.

---

## Pattern 3: Flexible Array Members (C99)

For structs with variable-length data at the end:

```c
typedef struct {
    size_t len;
    char data[];  // Flexible array member — no size specified
} String;

String *create_string(const char *src)
{
    size_t len = strlen(src);
    String *s = malloc(sizeof(String) + len + 1);
    s->len = len;
    strcpy(s->data, src);
    return s;
}
```

**Benefits:**
- One allocation instead of two (struct + string)
- Better cache locality
- No pointer indirection

---

## Pattern 4: State Machines with Function Pointers

```c
typedef enum { STATE_IDLE, STATE_RUNNING, STATE_PAUSED, STATE_STOPPED } State;

typedef struct {
    State state;
    void (*on_enter)(void);
    void (*on_exit)(void);
} StateMachine;

void idle_enter(void) { printf("Entering idle\n"); }
void idle_exit(void) { printf("Exiting idle\n"); }
void running_enter(void) { printf("Starting...\n"); }

void transition(StateMachine *sm, State new_state)
{
    if (sm->on_exit) sm->on_exit();
    sm->state = new_state;
    // In real code, look up new state's functions
}
```

---

## Pattern 5: Callback Pattern

```c
typedef void (*ProgressCallback)(int percent, void *user_data);

void process_large_file(const char *path, ProgressCallback cb, void *user_data)
{
    for (int i = 0; i <= 100; i++) {
        // ... process chunk ...
        if (cb) cb(i, user_data);  // Call user's progress function
    }
}

// User's callback
void my_progress(int percent, void *user_data)
{
    (void)user_data;  // Explicitly unused
    printf("Progress: %d%%\r", percent);
    fflush(stdout);
}

// Usage
process_large_file("data.bin", my_progress, NULL);
```

---

## Pattern 6: Sentinel Values

```c
// Return sentinel on error
int find_index(const int *arr, int n, int target)
{
    for (int i = 0; i < n; i++) {
        if (arr[i] == target) return i;
    }
    return -1;  // Sentinel: not found
}
```

---

## Pattern 7: Counted Loops with Sizeof

```c
int arr[] = {10, 20, 30, 40, 50};

// WRONG inside a function (array decays to pointer):
// for (int i = 0; i < sizeof(arr)/sizeof(arr[0]); i++)  // Only works where arr is declared!

// RIGHT: Pass size as parameter
void print_array(const int *arr, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        printf("%d\n", arr[i]);
    }
}

// Call with:
print_array(arr, sizeof(arr) / sizeof(arr[0]));
```

---

## Pattern 8: The `container_of` Macro (Linux Kernel)

Get the parent struct from a pointer to one of its members:

```c
#define container_of(ptr, type, member)     ((type *)((char *)(ptr) - offsetof(type, member)))

typedef struct {
    int id;
    char name[50];
} Person;

typedef struct {
    Person person;
    float gpa;
} Student;

// Given a pointer to the Person member, get the Student
Student s = {{1, "Alice"}, 3.8};
Person *p = &s.person;
Student *sp = container_of(p, Student, person);
// sp now points to s
```

---

## Pattern 9: Defensive Programming with Asserts

```c
#include <assert.h>

void *safe_malloc(size_t size)
{
    void *p = malloc(size);
    assert(p != NULL);  // Catch allocation failures in debug builds
    return p;
}

void process_array(const int *arr, size_t n)
{
    assert(arr != NULL);
    assert(n > 0);
    // ... process ...
}
```

---

## Pattern 10: String Builder Pattern

Build strings dynamically without repeated reallocations:

```c
typedef struct {
    char *data;
    size_t len;
    size_t capacity;
} StringBuilder;

StringBuilder *sb_create(void)
{
    StringBuilder *sb = malloc(sizeof(StringBuilder));
    sb->capacity = 64;
    sb->data = malloc(sb->capacity);
    sb->data[0] = '\0';
    sb->len = 0;
    return sb;
}

void sb_append(StringBuilder *sb, const char *str)
{
    size_t needed = sb->len + strlen(str) + 1;
    if (needed > sb->capacity) {
        sb->capacity *= 2;
        if (sb->capacity < needed) sb->capacity = needed;
        sb->data = realloc(sb->data, sb->capacity);
    }
    strcpy(sb->data + sb->len, str);
    sb->len += strlen(str);
}

char *sb_to_string(StringBuilder *sb)
{
    return sb->data;  // User must free later
}

void sb_free(StringBuilder *sb)
{
    free(sb->data);
    free(sb);
}
```

---

> **Professor's Note**: These patterns are the difference between a C programmer and a GOOD C programmer. The `goto` cleanup pattern is universally used in systems code (Linux kernel, etc.). Opaque pointers give you the power of encapsulation. Flexible array members save memory and improve performance. Study these patterns, internalize them, and use them in your own code.
