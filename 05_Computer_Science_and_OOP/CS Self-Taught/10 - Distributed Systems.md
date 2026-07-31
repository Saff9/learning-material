# 10 - Distributed Systems

> **Phase:** 3 (Systems & Theory) · **Time:** ~6–8 weeks · **Difficulty:** ⭐⭐⭐⭐

## What it is
A **distributed system** is many computers working together as one — the foundation of modern tech (databases, cloud, search, social networks).

> If you study only **one** advanced topic, make it this. It's the "holy grail" for tech companies and a top interview subject.

## Why it matters
- Almost every production system is distributed.
- Failures are normal, not exceptional — you must design for them.
- Highest-ROI advanced CS topic for a career.

## Core concepts — detailed

### CAP theorem
You can't have all three during a network partition:
- **C**onsistency — every read gets the latest write
- **A**vailability — every request gets a response
- **P**artition tolerance — survives network failure
> In practice you pick **CP** or **AP**; partitions are unavoidable.

### Replication & sharding
- **Replication:** copy data to multiple nodes (fault tolerance, read scale).
- **Sharding:** split data across nodes (write scale).

### Consensus
- How nodes agree on a value despite failures.
- **Raft**, **Paxos** — elect a leader, replicate a log.

### Fault tolerance
- Design so one node dying doesn't break the system.
- **Idempotency:** retrying a request is safe.
- **Quorums:** majority wins.

### Messaging
- **Message queues** (Kafka, RabbitMQ) decouple producers/consumers.
- **Event logs** as the source of truth.

## Deep Dive: System Design & Distributed Systems
- **CAP Theorem vs. PACELC:** Extends CAP to define behavior during normal operation (latency vs. consistency).
- **Consistency Models:** Strong, Eventual, Causal, Read-Your-Writes, Monotonic Reads.
- **Database Scaling Strategies:** 
  - *Sharding (Partitioning)*: Splitting data across multiple machines based on a shard key.
  - *Replication*: Master-Slave (write to master, read from slaves) vs. Master-Master.
- **Distributed Consensus Algorithms:**
  - *Paxos & Raft*: Ensuring a cluster of nodes agrees on a shared state, even if some fail.
- **Microservices Architecture:** API Gateways, Service Discovery, Event-Driven Architecture (Kafka, RabbitMQ), Circuit Breakers.

## Key Metrics in System Design
- **Latency:** Time taken for a single request.
- **Throughput:** Number of requests processed per second.
- **Availability:** Uptime percentage (e.g., "Five Nines" = 99.999%).

## Free resources
- **Designing Data-Intensive Applications** (Kleppmann) — the modern bible.
- **TeachYourselfCS — Distributed Systems**: https://teachyourselfcs.com/
- **MIT 6.824 — Distributed Systems (OCW, with labs)**: https://pdos.csail.mit.edu/6.824/
- **Raft visual explanation**: https://raft.github.io/
- **CMU DB / Systems lectures (YouTube)**.

## Practice projects
1. **Key-value store** with replication across 3 nodes.
2. **Leader election** toy implementation (Raft-lite).
3. Read the **Kafka** or **Raft** paper and summarize it.
4. Design (on paper) a URL shortener or chat app for 1M users.

## Self-check (can you…)
- [ ] Explain CAP with a real example
- [ ] Describe replication vs sharding
- [ ] Explain consensus / Raft at a high level
- [ ] Design a fault-tolerant service

## Progress
- [ ] Understand CAP theorem
- [ ] Explain replication + consensus
- [ ] Read a systems paper (Kafka/Raft)
- [ ] Designed a distributed app

## Next
→ [[11 - Security Fundamentals]]
