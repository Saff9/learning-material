# 02 - Data Structures & Algorithms

> **Phase:** 1 (Foundations) · **Time:** ~8–12 weeks · **Difficulty:** ⭐⭐⭐

## What it is
- **Data Structures** = ways to organize and store data so it can be used efficiently (arrays, lists, trees, hash maps, graphs).
- **Algorithms** = step-by-step procedures to solve problems (sort, search, traverse, optimize).

They are two sides of the same coin: the right structure makes the right algorithm possible.

## Why it matters
- **#1 interview topic** at almost every tech company.
- The difference between a program that runs in **1 second vs 1 hour** is usually the choice of structure/algorithm.
- Trains **computational thinking** that applies everywhere.

## Big-O notation (learn this first!)
Measures how runtime/memory **grows** with input size `n`:
- `O(1)` constant — hash lookup
- `O(log n)` logarithmic — binary search
- `O(n)` linear — single loop
- `O(n log n)` — good sorting (merge/quick)
- `O(n²)` quadratic — nested loops (avoid on big data)
- `O(2ⁿ)`, `O(n!)` — exponential, usually too slow

> Memorize the common ones; you'll justify choices in interviews with Big-O.

## Data structures — detailed
| Structure | Access | Search | Insert | Use when |
|---|---|---|---|---|
| **Array** | O(1) | O(n) | O(n) | Fixed-size, fast index |
| **Linked List** | O(n) | O(n) | O(1) | Frequent add/remove |
| **Stack (LIFO)** | — | — | O(1) | Undo, recursion, parsing |
| **Queue (FIFO)** | — | — | O(1) | BFS, scheduling |
| **Hash Map** | — | O(1)* | O(1)* | Fast key→value lookup |
| **Binary Search Tree** | O(log n) | O(log n) | O(log n) | Sorted dynamic data |
| **Heap** | — | — | O(log n) | Priority queues, heapsort |
| **Graph** | — | — | — | Networks, relationships |

## Algorithms — detailed
- **Sorting:** bubble (teaching only), insertion, merge, quick, heap.
- **Searching:** linear, binary (needs sorted).
- **Recursion:** function calling itself; base case + recursive case.
- **Divide & Conquer:** split problem, solve, combine (merge sort).
- **Dynamic Programming:** cache subproblem answers (Fibonacci, knapsack).
- **Graph algorithms:** BFS, DFS, Dijkstra (shortest path), topological sort.
- **Greedy:** pick locally optimal (works for some problems).

## Free resources
- **TeachYourselfCS — Algorithms**: https://teachyourselfcs.com/
- **CS50** — gentle DSA intro.
- **MIT 6.006 — Intro to Algorithms (OCW)**: https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/
- **freeCodeCamp — DSA full course**: https://www.youtube.com/watch?v=8hly31xKli0
- **GeeksforGeeks — DSA**: https://www.geeksforgeeks.org/data-structures/
- **Visualgo** — animate structures/algorithms: https://visualgo.net/
- **Practice:** LeetCode (https://leetcode.com/), NeetCode (https://neetcode.io/), Exercism.

## Practice plan
1. **Implement from scratch:** array, linked list, stack, queue, hash map, binary search tree.
2. **Implement sorts:** bubble, insertion, merge, quick — and time them.
3. **Solve by difficulty:** 20 easy → 20 medium LeetCode.
4. **Build:** a pathfinding visualizer (BFS/Dijkstra on a grid).

## Self-check (can you…)
- [ ] Explain Big-O for common operations
- [ ] Implement a linked list and a hash map
- [ ] Write merge sort and quick sort
- [ ] Solve tree/graph problems with recursion
- [ ] Use DP to avoid recomputation

## Progress
- [ ] Understand Big-O deeply
- [ ] Implemented core structures by hand
- [ ] Comfortable with trees and graphs
- [ ] Solved 50+ LeetCode/NeetCode problems

## Next
→ [[03 - Databases (DBMS)]]
