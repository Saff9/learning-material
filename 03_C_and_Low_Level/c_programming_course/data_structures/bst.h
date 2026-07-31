#ifndef BST_H
#define BST_H

// Binary Search Tree Node
typedef struct BSTNode {
    int data;
    struct BSTNode* left;
    struct BSTNode* right;
} BSTNode;

// Binary Search Tree Structure
typedef struct BST {
    BSTNode* root;
} BST;

// Creates a new empty binary search tree
BST* bst_create();

// Destroys the tree and frees all associated memory
void bst_destroy(BST* tree);

// Inserts a new element into the BST
void bst_insert(BST* tree, int data);

// Searches for an element in the BST. Returns 1 if found, 0 otherwise.
int bst_search(BST* tree, int data);

// Prints the in-order traversal of the BST
void bst_inorder(BST* tree);

#endif // BST_H
