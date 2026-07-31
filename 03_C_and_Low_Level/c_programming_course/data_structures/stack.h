#ifndef STACK_H
#define STACK_H

// Stack Node
typedef struct StackNode {
    int data;
    struct StackNode* next;
} StackNode;

// Stack Structure
typedef struct Stack {
    StackNode* top;
} Stack;

// Creates a new empty stack
Stack* stack_create();

// Destroys the stack and frees all associated memory
void stack_destroy(Stack* stack);

// Pushes an element onto the stack
void stack_push(Stack* stack, int data);

// Pops an element from the stack. Returns 1 if successful, 0 otherwise.
int stack_pop(Stack* stack, int* out_data);

// Checks if the stack is empty. Returns 1 if empty, 0 otherwise.
int stack_is_empty(Stack* stack);

#endif // STACK_H
