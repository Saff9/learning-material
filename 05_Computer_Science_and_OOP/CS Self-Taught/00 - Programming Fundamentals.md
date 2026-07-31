# 00 - Programming Fundamentals

> **Phase:** 1 (Foundations) · **Time:** ~4–6 weeks · **Difficulty:** ⭐

## What it is
Programming is the act of writing precise instructions a computer can execute. "Fundamentals" means the universal building blocks that exist in **every** language: how data is stored, how the program makes decisions, and how work is broken into reusable pieces.

You are not "learning Python" — you are learning to **think computationally**. The language is just the syntax; the thinking transfers everywhere.

## Why it matters
- Every later topic (algorithms, web dev, systems, AI) assumes you can already write and debug a program.
- Employers screen on fundamentals first. Weak fundamentals = a ceiling on everything you build.
- Debugging skill comes from fundamentals, not frameworks.

## Choose ONE first language (and stick with it)
| Language | Best for | Notes |
|---|---|---|
| **Python** | Beginners, data, AI, scripting | Easiest to read; huge ecosystem |
| **JavaScript** | Web development | Runs in every browser |
| **C++** | Understanding the machine | Teaches memory/pointers; harder |
| **Java** | Enterprise, Android | Verbose but structured |

> 🚫 Don't switch languages mid-learning. Master one, then others are easy.

## Core concepts — detailed

### 1. Variables & data types
- A **variable** is a named box holding a value.
- **Types:** integers, floats, booleans, strings, (later) lists/dicts.
- Type systems: *static* (Java, C++) vs *dynamic* (Python, JS).

### 2. Operators
- Arithmetic (`+ - * / % **`), comparison (`== != < >`), logical (`and or not`).

### 3. Control flow
- **Conditionals:** `if / elif / else` — branching logic.
- **Loops:** `for` (iterate a collection), `while` (repeat while true).
- **Loop control:** `break`, `continue`.

### 4. Functions
- Reusable named blocks: `def add(a, b): return a + b`.
- **Parameters** (inputs) and **return** (output).
- **Scope:** local vs global variables.
- **Recursion** (a function calling itself) — introduced here lightly, deepened in DSA.

### 5. Data collections (intro)
- **Arrays/lists:** ordered, indexed.
- **Strings** as sequences of characters.
- **Dictionaries/maps** (intro only — full treatment in DSA).

### 6. Errors & debugging
- **Syntax errors** (typos), **runtime errors** (crash on bad input), **logic errors** (runs but wrong answer).
- Read the **stack trace** top-to-bottom.
- Use `print()` / a debugger to inspect state.

## A realistic week-by-week plan
- **Week 1:** variables, types, arithmetic, printing.
- **Week 2:** conditionals and loops; small logic puzzles.
- **Week 3:** functions, parameters, scope; break problems into functions.
- **Week 4:** lists/strings, basic file reading.
- **Week 5–6:** build 2–3 small projects (see below).

## Free resources
- **CS50 (Harvard)** — the single best free CS intro: https://cs50.harvard.edu/
- **MIT 6.0001** — Intro to CS with Python (OCW): https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/
- **freeCodeCamp** — full free curriculum: https://www.freecodecamp.org/
- **GeeksforGeeks** — syntax reference by language: https://www.geeksforgeeks.org/
- **W3Schools** — quick lookups: https://www.w3schools.com/

## Practice projects (build these)
1. **Calculator** — take two numbers and an operator, print the result.
2. **Number guessing game** — computer picks a number, user guesses, give "higher/lower" hints.
3. **To-do list (terminal)** — add, list, remove tasks stored in a list.
4. **Word counter** — read a file and count words/lines/characters.

## Self-check (can you…)
- [ ] Explain what a variable and a type are
- [ ] Write a `for` and a `while` loop and know when each fits
- [ ] Break a problem into 3+ functions
- [ ] Read an error message and fix it
- [ ] Build a small project from scratch

## Progress
- [ ] Finished an intro course (CS50 / MIT 6.0001)
- [ ] Comfortable with loops, functions, scope
- [ ] Built 2+ projects
- [ ] Can debug without help

## Next
→ [[01 - Object-Oriented Programming]]
