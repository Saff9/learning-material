#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TABLE_SIZE 100

typedef struct HTNode {
    char* key;
    int value;
    struct HTNode* next;
} HTNode;

typedef struct HashTable {
    HTNode** table;
} HashTable;

HashTable* create_table() {
    HashTable* ht = (HashTable*)malloc(sizeof(HashTable));
    ht->table = (HTNode**)calloc(TABLE_SIZE, sizeof(HTNode*));
    return ht;
}

unsigned int hash(const char* key) {
    unsigned int hash = 0;
    while (*key) {
        hash = (hash << 5) + *key++;
    }
    return hash % TABLE_SIZE;
}

void insert_ht(HashTable* ht, const char* key, int value) {
    unsigned int idx = hash(key);
    HTNode* new_node = (HTNode*)malloc(sizeof(HTNode));
    new_node->key = strdup(key);
    new_node->value = value;
    new_node->next = ht->table[idx];
    ht->table[idx] = new_node;
}

void free_table(HashTable* ht) {
    for (int i = 0; i < TABLE_SIZE; i++) {
        HTNode* curr = ht->table[i];
        while (curr != NULL) {
            HTNode* temp = curr;
            curr = curr->next;
            free(temp->key);
            free(temp);
        }
    }
    free(ht->table);
    free(ht);
}
