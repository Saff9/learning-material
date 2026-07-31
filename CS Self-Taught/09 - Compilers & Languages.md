# 09 - Compilers & Languages

> **Phase:** 3 (Systems & Theory) · **Time:** ~5–7 weeks · **Difficulty:** ⭐⭐⭐

## What it is
A **compiler** translates source code (Python, C++, Java) into something a machine can run — either machine code or an intermediate form. **Language design** studies *how* we express computation.

## Why it matters
- Demystifies every language you use (why errors look the way they do).
- Builds deep confidence as an engineer.
- Opens paths into tooling, DSLs, and interpreters.

## The pipeline — detailed
```
Source code
   ↓ 1. Lexing (scanning)    → tokens
   ↓ 2. Parsing              → AST (syntax tree)
   ↓ 3. Semantic analysis     → type checking
   ↓ 4. Optimization          → faster IR
   ↓ 5. Code generation       → machine/byte code
```
- **Lexer:** turns characters into tokens (`if`, `x`, `=`, `5`).
- **Parser:** builds an **AST** (abstract syntax tree).
- **Semantic analysis:** types, scopes, undefined vars.
- **Code gen:** emits target code (or runs on a VM).

## Interpretation vs Compilation
- **Compiled (C, Go, Rust):** source → machine code ahead of time.
- **Interpreted (Python, JS):** run line-by-line via an interpreter/VM.
- **Hybrid (Java):** source → bytecode → JIT-compiled at runtime.

## Language design basics
- **Static vs dynamic typing.**
- **Strong vs weak typing.**
- **Scoping:** lexical (static) vs dynamic.
- **Paradigms:** imperative, OOP, functional, logic.

## Free resources
- **Crafting Interpreters (free book)**: https://craftinginterpreters.com/contents.html
- **TeachYourselfCS — Languages & Compilers**: https://teachyourselfcs.com/
- **Compilers: Principles, Techniques & Tools** ("Dragon Book").
- **Alex Aiken — Compilers (edX)**: https://www.edx.org/course/compilers
- **MIT 6.035 / 6.828** OCW materials.

## Practice projects
1. **Calculator interpreter** — lex + parse + eval `(1 + 2) * 3`.
2. **Tiny Lisp** — parentheses, `def`, `if`, functions.
3. **Tokenizer** for a subset of a real language (e.g., JSON).
4. **Bytecode VM** — define your own simple instruction set.

## Self-check (can you…)
- [ ] Explain lexing + parsing
- [ ] Draw an AST for an expression
- [ ] Build a small interpreter
- [ ] Compare compiled vs interpreted languages

## Progress
- [ ] Understand the compile pipeline
- [ ] Built a small interpreter
- [ ] Read part of Crafting Interpreters

## Next
→ [[10 - Distributed Systems]]
