#include "slist.h"
#include <stdlib.h>
#include <stdio.h>

SList* slist_create() {
    SList* list = (SList*)malloc(sizeof(SList));
    if (list) {
        list->head = NULL;
        list->tail = NULL;
    }
    return list;
}

void slist_destroy(SList* list) {
    if (!list) return;
    SListNode* curr = list->head;
    while (curr) {
        SListNode* next = curr->next;
        free(curr);
        curr = next;
    }
    free(list);
}

void slist_push_front(SList* list, int data) {
    if (!list) return;
    SListNode* node = (SListNode*)malloc(sizeof(SListNode));
    if (!node) return; // Handle allocation failure
    node->data = data;
    node->next = list->head;
    list->head = node;
    if (!list->tail) {
        list->tail = node;
    }
}

void slist_push_back(SList* list, int data) {
    if (!list) return;
    SListNode* node = (SListNode*)malloc(sizeof(SListNode));
    if (!node) return; // Handle allocation failure
    node->data = data;
    node->next = NULL;
    if (list->tail) {
        list->tail->next = node;
    } else {
        list->head = node; // List was empty
    }
    list->tail = node;
}

int slist_pop_front(SList* list, int* out_data) {
    if (!list || !list->head) return 0;
    SListNode* node = list->head;
    if (out_data) *out_data = node->data;
    list->head = node->next;
    if (!list->head) {
        list->tail = NULL; // List became empty
    }
    free(node);
    return 1;
}

void slist_print(SList* list) {
    if (!list) return;
    SListNode* curr = list->head;
    while (curr) {
        printf("%d -> ", curr->data);
        curr = curr->next;
    }
    printf("NULL\n");
}
