#include <stdio.h>
#include <stdlib.h>

typedef struct BSTNode {
    int data;
    struct BSTNode* left;
    struct BSTNode* right;
} BSTNode;

BSTNode* create_bst_node(int data) {
    BSTNode* new_node = (BSTNode*)malloc(sizeof(BSTNode));
    if (!new_node) return NULL;
    new_node->data = data;
    new_node->left = NULL;
    new_node->right = NULL;
    return new_node;
}

BSTNode* insert_bst(BSTNode* root, int data) {
    if (root == NULL) return create_bst_node(data);
    if (data < root->data) root->left = insert_bst(root->left, data);
    else if (data > root->data) root->right = insert_bst(root->right, data);
    return root;
}

void free_bst(BSTNode* root) {
    if (root != NULL) {
        free_bst(root->left);
        free_bst(root->right);
        free(root);
    }
}
