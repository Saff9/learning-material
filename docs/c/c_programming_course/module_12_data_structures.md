# Module 12: Data Structures in C

## Linked List

```c
typedef struct Node {
    int data;
    struct Node *next;
} Node;

Node* create_node(int data)
{
    Node *new_node = malloc(sizeof(Node));
    if (new_node == NULL) return NULL;
    new_node->data = data;
    new_node->next = NULL;
    return new_node;
}

void append(Node **head, int data)
{
    Node *new_node = create_node(data);
    if (*head == NULL) {
        *head = new_node;
        return;
    }
    Node *temp = *head;
    while (temp->next != NULL) {
        temp = temp->next;
    }
    temp->next = new_node;
}
```

**Why `Node **head`?** Because we might need to modify the head pointer itself (if the list was empty).

## Stack (Array-based)

```c
#define MAX 100
typedef struct {
    int arr[MAX];
    int top;
} Stack;

void push(Stack *s, int val)
{
    if (s->top == MAX - 1) {
        printf("Stack Overflow\n");
        return;
    }
    s->arr[++(s->top)] = val;
}

int pop(Stack *s)
{
    if (s->top == -1) {
        printf("Stack Underflow\n");
        return -1;
    }
    return s->arr[(s->top)--];
}
```

## Queue (Circular Array)

```c
#define MAX 100
typedef struct {
    int arr[MAX];
    int front;
    int rear;
    int count;
} Queue;

void enqueue(Queue *q, int val)
{
    if (q->count == MAX) {
        printf("Queue Full\n");
        return;
    }
    q->rear = (q->rear + 1) % MAX;
    q->arr[q->rear] = val;
    q->count++;
}

int dequeue(Queue *q)
{
    if (q->count == 0) {
        printf("Queue Empty\n");
        return -1;
    }
    int val = q->arr[q->front];
    q->front = (q->front + 1) % MAX;
    q->count--;
    return val;
}
```

## Binary Search Tree

```c
typedef struct TreeNode {
    int data;
    struct TreeNode *left;
    struct TreeNode *right;
} TreeNode;

TreeNode* create_tree_node(int data)
{
    TreeNode *node = malloc(sizeof(TreeNode));
    node->data = data;
    node->left = node->right = NULL;
    return node;
}

TreeNode* insert(TreeNode *root, int data)
{
    if (root == NULL) return create_tree_node(data);
    if (data < root->data) root->left = insert(root->left, data);
    else if (data > root->data) root->right = insert(root->right, data);
    return root;
}

void inorder(TreeNode *root)
{
    if (root != NULL) {
        inorder(root->left);
        printf("%d ", root->data);
        inorder(root->right);
    }
}
```

## Practice Problems

### Problem 12.1: Linked List with Free
Implement a singly linked list with `insert`, `delete`, `print`, and `free_list` functions.

<details>
<summary>Solution</summary>

```c
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node *next;
} Node;

void insert(Node **head, int data)
{
    Node *new_node = malloc(sizeof(Node));
    new_node->data = data;
    new_node->next = *head;
    *head = new_node;
}

void delete(Node **head, int key)
{
    Node *temp = *head, *prev = NULL;

    if (temp != NULL && temp->data == key) {
        *head = temp->next;
        free(temp);
        return;
    }

    while (temp != NULL && temp->data != key) {
        prev = temp;
        temp = temp->next;
    }

    if (temp == NULL) return;

    prev->next = temp->next;
    free(temp);
}

void print_list(Node *head)
{
    while (head != NULL) {
        printf("%d -> ", head->data);
        head = head->next;
    }
    printf("NULL\n");
}

void free_list(Node *head)
{
    Node *temp;
    while (head != NULL) {
        temp = head;
        head = head->next;
        free(temp);
    }
}

int main(void)
{
    Node *head = NULL;
    insert(&head, 3);
    insert(&head, 7);
    insert(&head, 1);
    print_list(head);
    delete(&head, 7);
    print_list(head);
    free_list(head);
    return 0;
}
```
</details>
