# Computer Science Fundamentals - Quick Reference Cheatsheet

## 1. Data Structures

| Structure | Access | Search | Insert | Delete | Space | Description |
|-----------|--------|--------|--------|--------|-------|-------------|
| **Array** | $O(1)$ | $O(N)$ | $O(N)$ | $O(N)$ | $O(N)$ | Contiguous memory allocation. Great for indexing, slow for inserts/deletes. |
| **Linked List** | $O(N)$ | $O(N)$ | $O(1)$ | $O(1)$ | $O(N)$ | Nodes pointing to next. Fast inserts/deletes if node is known. |
| **Stack** | $O(N)$ | $O(N)$ | $O(1)$ | $O(1)$ | $O(N)$ | LIFO (Last In First Out). Used in recursion, DFS, undo features. |
| **Queue** | $O(N)$ | $O(N)$ | $O(1)$ | $O(1)$ | $O(N)$ | FIFO (First In First Out). Used in BFS, scheduling. |
| **Hash Table** | N/A | $O(1)$*| $O(1)$*| $O(1)$*| $O(N)$ | Key-value mapping. *Average case $O(1)$, worst case $O(N)$ due to collisions. |
| **BST** | $O(\log N)$ | $O(\log N)$| $O(\log N)$| $O(\log N)$| $O(N)$ | Binary Search Tree. Left child < parent, right child > parent. |
| **Heap** | N/A | $O(N)$ | $O(\log N)$| $O(\log N)$| $O(N)$ | Complete binary tree. Used for Priority Queues (Min-Heap / Max-Heap). |

## 2. Algorithms & Big-O Notation

**Sorting:**
- **Merge Sort:** $O(N \log N)$ time, $O(N)$ space. Divide and conquer. Stable.
- **Quick Sort:** $O(N \log N)$ average time, $O(\log N)$ space. In-place. Unstable.
- **Heap Sort:** $O(N \log N)$ time, $O(1)$ space. In-place. Unstable.

**Graph Traversals:**
- **BFS:** $O(V + E)$ time, $O(V)$ space. Uses Queue. Good for shortest path on unweighted graphs.
- **DFS:** $O(V + E)$ time, $O(V)$ space. Uses Stack/Recursion. Good for exploring all paths, topological sort.

## 3. Operating Systems

- **Process vs. Thread:** A process is a program in execution (has own memory space). A thread is a unit of execution within a process (shares memory with other threads).
- **Concurrency vs. Parallelism:** Concurrency is dealing with many things at once (interleaving). Parallelism is doing many things at once (multi-core).
- **Deadlock Conditions (Coffman's):** Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait.
- **Virtual Memory:** Extends RAM by using disk space (paging/swapping). Pages are mapped to physical frames via page tables.

## 4. Computer Networking

**OSI Model (7 Layers):**
7. Application (HTTP, FTP, DNS)
6. Presentation (SSL/TLS, JPEG)
5. Session (Sockets)
4. Transport (TCP, UDP)
3. Network (IP, ICMP)
2. Data Link (Ethernet, MAC)
1. Physical (Cables, Radio)

**TCP vs UDP:**
- **TCP (Transmission Control Protocol):** Connection-oriented, reliable, ordered, error-checked. Slower (3-way handshake).
- **UDP (User Datagram Protocol):** Connectionless, unreliable, unordered, no error checking. Fast (streaming, gaming).

**HTTP/3:**
- Based on QUIC (runs over UDP) rather than TCP. Solves head-of-line blocking. Faster connection setup.

## 5. System Design Principles

- **CAP Theorem:** A distributed data store can only guarantee two out of three: Consistency, Availability, Partition Tolerance. (Network partitions are inevitable, so choose between C and A).
- **Vertical vs Horizontal Scaling:**
  - *Vertical (Scale Up):* Add more power (CPU, RAM) to existing machine.
  - *Horizontal (Scale Out):* Add more machines. Better for high traffic and fault tolerance.
- **Load Balancing:** Distributes incoming network traffic across multiple servers.
- **Caching:** Stores copies of frequently accessed data (e.g., Redis, Memcached) to reduce database load.
- **Database Indexing:** B-Tree structures to speed up read queries (at the cost of slower writes and extra storage).
