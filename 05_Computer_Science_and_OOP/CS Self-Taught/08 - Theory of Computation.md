# 08 - Theory of Computation

> **Phase:** 3 (Systems & Theory) · **Time:** ~4–5 weeks · **Difficulty:** ⭐⭐⭐

## What it is
The mathematical study of **what computers can and cannot do** — from simple pattern matchers to the limits of computation itself.

## Why it matters
- Builds rigorous, abstract thinking that pays off in algorithms and compilers.
- Explains *why* some problems are unsolvable (the halting problem).
- Interview-adjacent for research/PhD roles; foundational for CS theory.

## Core concepts — detailed

### Automata & languages
- **Finite Automata (FA):** recognize **regular languages** (what regex does).
- **Pushdown Automata:** recognize **context-free** languages (most programming syntax).
- **Turing Machine (TM):** the most powerful model — recognizes **recursively enumerable** languages.

### Chomsky hierarchy
```
Regular ⊂ Context-Free ⊂ Context-Sensitive ⊂ Recursively Enumerable
```

### Turing machines
- An abstract machine with infinite tape + read/write head.
- The formal definition of "computable."
- **Church-Turing thesis:** anything computable can be done by a TM.

### Decidability
- **Decidable:** a TM always halts with yes/no.
- **The Halting Problem:** *undecidable* — no program can tell if arbitrary programs halt. Proof by contradiction.

### Complexity
- **P:** problems solvable in polynomial time (tractable).
- **NP:** verifiable in polynomial time.
- **P vs NP:** the famous open question — is verifying easier than solving?
- **NP-complete:** hardest NP problems; solving one solves all.

## Free resources
- **TeachYourselfCS — Theory**: https://teachyourselfcs.com/
- **GeeksforGeeks — Theory of Computation**: https://www.geeksforgeeks.org/theory-of-computation/
- **MIT 6.045 — Automata & Computability (OCW)**.
- **Michael Sipser — *Introduction to the Theory of Computation*** (standard textbook).

## Practice / exercises
1. Build a **regex → NFA** matcher.
2. Prove a language is **not regular** (pumping lemma).
3. Explain the **halting problem** in plain words, with an example.
4. Classify problems as P / NP / NP-complete.

## Self-check (can you…)
- [ ] Explain finite automata vs Turing machines
- [ ] State the Church-Turing thesis
- [ ] Describe the halting problem
- [ ] Explain P vs NP

## Progress
- [ ] Understand automata + regular languages
- [ ] Explained Turing machines
- [ ] Know P vs NP + decidability

## Next
→ [[09 - Compilers & Languages]]
