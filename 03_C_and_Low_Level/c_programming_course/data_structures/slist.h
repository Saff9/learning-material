#ifndef SLIST_H
#define SLIST_H

// Singly Linked List Node
typedef struct SListNode {
    int data;
    struct SListNode* next;
} SListNode;

// Singly Linked List Structure
typedef struct SList {
    SListNode* head;
    SListNode* tail;
} SList;

// Creates a new empty singly linked list
SList* slist_create();

// Destroys the list and frees all associated memory
void slist_destroy(SList* list);

// Pushes a new element to the front of the list
void slist_push_front(SList* list, int data);

// Pushes a new element to the back of the list
void slist_push_back(SList* list, int data);

// Pops an element from the front of the list. Returns 1 if successful, 0 otherwise.
int slist_pop_front(SList* list, int* out_data);

// Prints the contents of the list
void slist_print(SList* list);

#endif // SLIST_H
