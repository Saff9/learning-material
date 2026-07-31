#ifndef QUEUE_H
#define QUEUE_H

// Queue Node
typedef struct QueueNode {
    int data;
    struct QueueNode* next;
} QueueNode;

// Queue Structure
typedef struct Queue {
    QueueNode* front;
    QueueNode* rear;
} Queue;

// Creates a new empty queue
Queue* queue_create();

// Destroys the queue and frees all associated memory
void queue_destroy(Queue* queue);

// Enqueues an element to the back of the queue
void queue_enqueue(Queue* queue, int data);

// Dequeues an element from the front of the queue. Returns 1 if successful, 0 otherwise.
int queue_dequeue(Queue* queue, int* out_data);

// Checks if the queue is empty. Returns 1 if empty, 0 otherwise.
int queue_is_empty(Queue* queue);

#endif // QUEUE_H
