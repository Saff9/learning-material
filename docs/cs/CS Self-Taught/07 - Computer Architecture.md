# 07 - Computer Architecture

> **Phase:** 3 (Systems & Theory) · **Time:** ~5–7 weeks · **Difficulty:** ⭐⭐⭐

## What it is
**Computer Architecture** is how hardware actually executes software: the CPU, memory hierarchy, and how high-level code becomes machine instructions. It's the bridge between programs and silicon.

## Why it matters
- Explains *why* code is fast or slow (caches, pipelines).
- Required foundation for OS, compilers, embedded, and performance work.
- Makes "the computer" stop being magic.

## Core concepts — detailed

### The CPU
- **ALU** does arithmetic; **registers** are tiny ultra-fast storage.
- **Clock** ticks; instructions run per cycle.
- **Instruction cycle:** fetch → decode → execute.

### Memory hierarchy (fast→slow, small→big)
```
Registers → L1 cache → L2 cache → L3 → RAM → SSD → HDD
```
- Each step is ~10× slower than the last.
- **Principle of locality:** programs reuse recent data → caches work.

### Assembly (intro)
- Human-readable machine code: `MOV`, `ADD`, `JMP`.
- **Registers** hold operands; the CPU executes one instruction at a time.
- You don't need to master asm, but reading it demystifies bugs.

### Pipelines & parallelism
- **Pipelining:** start the next instruction before the current finishes.
- **Out-of-order execution**, branch prediction.
- **SIMD:** one instruction, many data (fast math).

### Number representation
- **Binary**, two's complement (negative numbers), fixed/floating point.
- Overflow, precision loss in floats.

## Free resources
- **TeachYourselfCS — Architecture**: https://teachyourselfcs.com/
- **Nand2Tetris** — build a computer from logic gates up: https://www.nand2tetris.org/
- **GeeksforGeeks — Computer Organization**: https://www.geeksforgeeks.org/computer-organization-and-architecture-tutorials/
- **MIT 6.004 — Computation Structures (OCW)**.
- **Ben Eater (YouTube)** — builds a CPU on a breadboard.

## Practice projects
1. **Nand2Tetris** projects 1–5 (gates → ALU → CPU → assembler).
2. Write a tiny **assembly** program (add two numbers).
3. **Benchmark:** time a loop that hits cache vs RAM.
4. Draw the **memory hierarchy** and explain it aloud.

## Self-check (can you…)
- [ ] Explain the CPU + instruction cycle
- [ ] Describe the memory hierarchy
- [ ] Read simple assembly
- [ ] Explain caches / locality

## Progress
- [ ] Understand CPU + memory hierarchy
- [ ] Read simple assembly
- [ ] Done Nand2Tetris projects 1–5

## Next
→ [[08 - Theory of Computation]]
