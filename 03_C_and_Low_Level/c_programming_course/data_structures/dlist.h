#ifndef DLIST_H
#define DLIST_H

// Doubly Linked List Node
typedef struct DListNode {
    int data;
    struct DListNode* prev;
    struct DListNode* next;
} DListNode;

// Doubly Linked List Structure
typedef struct DList {
    DListNode* head;
    DListNode* tail;
} DList;

// Creates a new empty doubly linked list
DList* dlist_create();

// Destroys the list and frees all associated memory
void dlist_destroy(DList* list);

// Pushes a new element to the front of the list
void dlist_push_front(DList* list, int data);

// Pushes a new element to the back of the list
void dlist_push_back(DList* list, int data);

// Pops an element from the front of the list. Returns 1 if successful, 0 otherwise.
int dlist_pop_front(DList* list, int* out_data);

// Pops an element from the back of the list. Returns 1 if successful, 0 otherwise.
int dlist_pop_back(DList* list, int* out_data);

// Prints the contents of the list
void dlist_print(DList* list);

#endif // DLIST_H
