/*
Windows:
gcc -fopenmp demo.cpp -o demo.exe -lstdc++
g++ -fopenmp demo.cpp -o demo.exe

demo.exe

Ubuntu: 
gcc -fopenmp demo.cpp -o demo.exe -lstdc++ 
or
gcc -o demo.exe -fopenmp demo.c
or
g++ -fopenmp demo.cpp -o demo.exe

./demo.exe
*/
#include <iostream>
#include <stack>
#include <vector>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
using namespace std;

struct TreeNode {
    int val;         // Value of the node
    TreeNode* left;  // Pointer to the left child
    TreeNode* right; // Pointer to the right child

    TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}
};

bool dfs(TreeNode* root, int target_val, vector<int>& visited_nodes) {
    stack<TreeNode*> s;
    s.push(root);
    bool found = false;

    vector<int> local_visited_nodes; // to store the visited nodes in the local stack

    #pragma omp parallel
    {
        stack<TreeNode*> local_stack; // to store the nodes in the local stack
        #pragma omp single
        {
            local_stack.push(s.top());
            s.pop();
        }
        while (!local_stack.empty()) {
            TreeNode* node;
            #pragma omp critical
            {
                node = local_stack.top();
                local_stack.pop();
            }

            local_visited_nodes.push_back(node->val); // add the visited node to local_visited_nodes vector

            if (node->val == target_val) {
                #pragma omp critical
                {
                    found = true; // Node found!
                }
            }

            if (node->right) {
                #pragma omp critical
                {
                    local_stack.push(node->right);
                }
            }

            if (node->left) {
                #pragma omp critical
                {
                    local_stack.push(node->left);
                }
            }
        }
    }

    #pragma omp critical
    {
        visited_nodes.insert(visited_nodes.end(), local_visited_nodes.begin(), local_visited_nodes.end());
    }

    return found;
}

int main() {
    // Example binary tree
    TreeNode* root = new TreeNode(1);
    root->left = new TreeNode(2);
    root->right = new TreeNode(3);
    root->left->left = new TreeNode(4);
    root->left->right = new TreeNode(5);
    root->right->left = new TreeNode(6);
    root->right->right = new TreeNode(7);

    int target_val = 5;
    vector<int> visited_nodes;

    bool found = dfs(root, target_val, visited_nodes);

    if (found) {
        cout << "Node with value " << target_val << " found in the tree!" << endl;
    } else {
        cout << "Node with value " << target_val << " not found in the tree." << endl;
    }

    cout << "Visited nodes: ";
    for (int i = 0; i < visited_nodes.size(); i++) {
        cout << visited_nodes[i] << " ";
    }
    cout << endl;

    return 0;
}
