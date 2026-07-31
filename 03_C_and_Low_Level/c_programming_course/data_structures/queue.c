#include <stdio.h>
#include <stdlib.h>

typedef struct QueueNode {
    int data;
    struct QueueNode* next;
} QueueNode;

typedef struct Queue {
    QueueNode *front, *rear;
} Queue;

QueueNode* create_queue_node(int data) {
    QueueNode* new_node = (QueueNode*)malloc(sizeof(QueueNode));
    if (!new_node) return NULL;
    new_node->data = data;
    new_node->next = NULL;
    return new_node;
}

Queue* create_queue() {
    Queue* q = (Queue*)malloc(sizeof(Queue));
    if (!q) return NULL;
    q->front = q->rear = NULL;
    return q;
}

void enqueue(Queue* q, int data) {
    QueueNode* new_node = create_queue_node(data);
    if (!new_node) return;
    if (q->rear == NULL) {
        q->front = q->rear = new_node;
        return;
    }
    q->rear->next = new_node;
    q->rear = new_node;
}

int dequeue(Queue* q) {
    if (q->front == NULL) return -1;
    QueueNode* temp = q->front;
    int data = temp->data;
    q->front = q->front->next;
    if (q->front == NULL) q->rear = NULL;
    free(temp);
    return data;
}

void free_queue(Queue* q) {
    while (q->front != NULL) dequeue(q);
    free(q);
}
