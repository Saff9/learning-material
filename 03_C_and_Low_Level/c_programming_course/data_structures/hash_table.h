#ifndef HASH_TABLE_H
#define HASH_TABLE_H

// Hash Table Node (for chaining)
typedef struct HashNode {
    char* key;
    int value;
    struct HashNode* next;
} HashNode;

// Hash Table Structure
typedef struct HashTable {
    HashNode** buckets;
    int num_buckets;
} HashTable;

// Creates a new hash table with the specified number of buckets
HashTable* hash_table_create(int num_buckets);

// Destroys the hash table and frees all associated memory
void hash_table_destroy(HashTable* table);

// Inserts a key-value pair into the hash table (updates the value if key exists)
void hash_table_insert(HashTable* table, const char* key, int value);

// Gets the value for a given key. Returns 1 if found, 0 otherwise.
int hash_table_get(HashTable* table, const char* key, int* out_value);

// Removes a key-value pair from the hash table. Returns 1 if removed, 0 otherwise.
int hash_table_remove(HashTable* table, const char* key);

#endif // HASH_TABLE_H
