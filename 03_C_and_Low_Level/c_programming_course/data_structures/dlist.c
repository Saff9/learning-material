#include "dlist.h"
#include <stdlib.h>
#include <stdio.h>

DList* dlist_create() {
    DList* list = (DList*)malloc(sizeof(DList));
    if (list) {
        list->head = NULL;
        list->tail = NULL;
    }
    return list;
}

void dlist_destroy(DList* list) {
    if (!list) return;
    DListNode* curr = list->head;
    while (curr) {
        DListNode* next = curr->next;
        free(curr);
        curr = next;
    }
    free(list);
}

void dlist_push_front(DList* list, int data) {
    if (!list) return;
    DListNode* node = (DListNode*)malloc(sizeof(DListNode));
    if (!node) return;
    node->data = data;
    node->prev = NULL;
    node->next = list->head;
    if (list->head) {
        list->head->prev = node;
    } else {
        list->tail = node;
    }
    list->head = node;
}

void dlist_push_back(DList* list, int data) {
    if (!list) return;
    DListNode* node = (DListNode*)malloc(sizeof(DListNode));
    if (!node) return;
    node->data = data;
    node->prev = list->tail;
    node->next = NULL;
    if (list->tail) {
        list->tail->next = node;
    } else {
        list->head = node;
    }
    list->tail = node;
}

int dlist_pop_front(DList* list, int* out_data) {
    if (!list || !list->head) return 0;
    DListNode* node = list->head;
    if (out_data) *out_data = node->data;
    list->head = node->next;
    if (list->head) {
        list->head->prev = NULL;
    } else {
        list->tail = NULL;
    }
    free(node);
    return 1;
}

int dlist_pop_back(DList* list, int* out_data) {
    if (!list || !list->tail) return 0;
    DListNode* node = list->tail;
    if (out_data) *out_data = node->data;
    list->tail = node->prev;
    if (list->tail) {
        list->tail->next = NULL;
    } else {
        list->head = NULL;
    }
    free(node);
    return 1;
}

void dlist_print(DList* list) {
    if (!list) return;
    DListNode* curr = list->head;
    while (curr) {
        printf("%d <-> ", curr->data);
        curr = curr->next;
    }
    printf("NULL\n");
}
