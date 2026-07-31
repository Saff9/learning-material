# 01 - Object-Oriented Programming

> **Phase:** 1 (Foundations) · **Time:** ~3–4 weeks · **Difficulty:** ⭐⭐

## What it is
**Object-Oriented Programming (OOP)** is a style of organizing code around **objects** — bundles of *data* (fields/attributes) and *behavior* (methods/functions) that represent real-world things or concepts.

Instead of writing long lists of functions and variables, you model your program as interacting objects: a `User`, a `BankAccount`, a `Car`.

## Why it matters
- The dominant paradigm in industry (Java, C++, Python, C#, Swift).
- Lets you **scale** code: big systems stay manageable when split into clear objects.
- Frameworks (React, Spring, Django) assume you understand classes/objects.
- Enables **reuse** through inheritance and **safety** through encapsulation.

## The 4 pillars — detailed

### 1. Encapsulation
- Hiding internal state; exposing only what's needed via methods.
- Example: a `BankAccount` keeps `balance` private and only changes it through `deposit()` / `withdraw()`.
- **Benefit:** callers can't corrupt state accidentally.

### 2. Abstraction
- Showing the *essential* features, hiding complex internals.
- A `Car.start()` method — you don't need to know the engine internals.
- **Benefit:** simpler interfaces, easier to change internals later.

### 3. Inheritance
- A class (**child/subclass**) extends another (**parent/superclass**) and reuses its code ("is-a" relationship).
- `Dog extends Animal` → Dog gets `eat()` for free, adds `bark()`.
- **Caution:** deep inheritance hierarchies get messy; prefer composition sometimes.

### 4. Polymorphism
- One interface, many implementations.
- A `shape.draw()` call behaves differently for `Circle` vs `Square`.
- Achieved via method **overriding** (runtime) and **overloading** (compile-time).

## Key vocabulary
- **Class** = blueprint (e.g., `class Dog:`).
- **Object / Instance** = a concrete thing created from the class (`my_dog = Dog()`).
- **Constructor** = special method that runs when an object is created (`__init__` in Python).
- **`self` / `this`** = reference to the current object.
- **Static vs instance** methods.

## Common mistakes
- Making everything a getter/setter with no behavior (anemic objects).
- Inheritance when **composition** ("has-a") fits better.
- Giant "God" classes doing too much.

## Free resources
- **GeeksforGeeks — OOP concepts**: https://www.geeksforgeeks.org/object-oriented-programming-oops-concept-in-cpp/
- **freeCodeCamp — OOP in Python/Java** (YouTube).
- **CS50 / MIT OCW** — software construction sections.
- **Refactoring Guru — OOP patterns explained visually**: https://refactoring.guru/

## Practice projects
1. **Bank system** — `Account` with deposit/withdraw, `Customer` with many accounts.
2. **Library** — `Book`, `Member`, `Librarian`; borrow/return logic.
3. **Game entities** — `Character` base class, `Player` and `Enemy` subclasses.
4. **Shape calculator** — `Shape` base, `Circle`/`Rectangle` override `area()`.

## Self-check (can you…)
- [ ] Explain class vs object with an example
- [ ] Use all 4 pillars in code
- [ ] Choose inheritance vs composition
- [ ] Refactor a procedural script into classes

## Progress
- [ ] Understand class vs object
- [ ] Used encapsulation + abstraction
- [ ] Built an inheritance hierarchy
- [ ] Shipped an OOP project

## Next
→ [[02 - Data Structures & Algorithms]]
