#include <stdio.h>
#include <stdlib.h>

typedef struct StackNode {
    int data;
    struct StackNode* next;
} StackNode;

StackNode* create_stack_node(int data) {
    StackNode* new_node = (StackNode*)malloc(sizeof(StackNode));
    if (!new_node) return NULL;
    new_node->data = data;
    new_node->next = NULL;
    return new_node;
}

void push(StackNode** root, int data) {
    StackNode* new_node = create_stack_node(data);
    if (!new_node) return;
    new_node->next = *root;
    *root = new_node;
}

int pop(StackNode** root) {
    if (root == NULL || *root == NULL) return -1;
    StackNode* temp = *root;
    int data = temp->data;
    *root = (*root)->next;
    free(temp);
    return data;
}

int peek(StackNode** root) {
    if (root == NULL || *root == NULL) return -1;
    return (*root)->data;
}

void free_stack(StackNode* root) {
    while (root != NULL) {
        StackNode* temp = root;
        root = root->next;
        free(temp);
    }
}
