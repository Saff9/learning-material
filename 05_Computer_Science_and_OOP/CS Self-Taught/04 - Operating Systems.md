# 04 - Operating Systems

> **Phase:** 2 (Core Engineering) · **Time:** ~5–7 weeks · **Difficulty:** ⭐⭐⭐

## What it is
An **Operating System (OS)** is the layer of software that manages hardware (CPU, memory, disk, devices) and provides services for programs. Examples: Linux, Windows, macOS, Android (Linux kernel).

Every program you write runs *on top of* an OS — understanding it explains crashes, slowness, and concurrency bugs.

## Why it matters
- Makes you a **better debugger** (why is my program slow / out of memory?).
- Essential for **systems**, backend, and embedded work.
- Common interview topic (processes, threads, concurrency, memory).

## Core concepts — detailed

### Processes & Threads
- **Process:** an isolated running program (its own memory).
- **Thread:** a lightweight execution unit *within* a process (shares memory).
- A process can have many threads → need **synchronization**.

### CPU scheduling
How the OS decides which process/thread runs:
- **FIFO, Round Robin, Priority, Multi-level**.
- Context switching has a cost.

### Memory management
- **Virtual memory:** each process gets its own address space; the OS maps it to physical RAM.
- **Paging:** memory split into fixed-size pages.
- **Segmentation,** swapping to disk when RAM is full.

### Concurrency
- **Race condition:** outcome depends on timing.
- **Mutex / Lock:** ensures only one thread enters a critical section.
- **Deadlock:** two threads each wait for the other's lock (fix: ordering, timeouts).

### File systems
How bytes are stored on disk (inodes, directories, permissions).

### System calls
The interface programs use to ask the OS for resources (`open`, `read`, `fork`, `exec`).

## Deep Dive: Operating System Internals
- **Inter-Process Communication (IPC):** Pipes, Shared Memory, Message Queues, Sockets.
- **Thread Synchronization:** Semaphores (counting mechanism) vs. Mutexes (binary locking). Spinlocks vs. Sleeping locks.
- **Deadlock Handling:** 
  - *Prevention*: negate one of the Coffman conditions.
  - *Avoidance*: Banker's Algorithm.
  - *Detection and Recovery*: preempt resources or terminate processes.
- **Memory Management Advanced:**
  - *Page Replacement Algorithms*: FIFO, LRU, LFU, Clock/Second-Chance.
  - *Translation Lookaside Buffer (TLB)*: Hardware cache to speed up virtual-to-physical address translation.
  - *Thrashing*: When a system spends more time paging than executing.

## Real-world Applications
- Containerization (Docker) relies heavily on OS features like `cgroups` (resource limiting) and `namespaces` (isolation) in the Linux kernel.

## Free resources
- **TeachYourselfCS — Operating Systems**: https://teachyourselfcs.com/
- **OSTEP (Operating Systems: Three Easy Pieces)** — *free book*: http://pages.cs.wisc.edu/~remzi/OSTEP/
- **GeeksforGeeks — OS**: https://www.geeksforgeeks.org/operating-systems/
- **xv6** — a tiny, readable Unix kernel to study: https://pdos.csail.mit.edu/6.828/2016/xv6.html
- **Linux** — your [[Ubuntu-WSL-Obsidian-Vault]] is a great hands-on OS lab.

## Practice projects
1. **Multithreaded counter** — cause a race condition, then fix it with a lock.
2. **Deadlock demo** — create and resolve a deadlock.
3. **Read xv6** — trace how it boots and schedules processes.
4. **System-monitor** — use OS APIs to show CPU/memory usage.

## Self-check (can you…)
- [ ] Explain process vs thread
- [ ] Describe virtual memory
- [ ] Prevent a race condition with a lock
- [ ] Explain what a deadlock is and how to avoid it

## Progress
- [ ] Understand processes, threads, scheduling
- [ ] Explained virtual memory + paging
- [ ] Written safe concurrent code
- [ ] Read part of OSTEP / xv6

## Next
→ [[05 - Computer Networking]]
