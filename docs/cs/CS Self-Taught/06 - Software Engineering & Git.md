# 06 - Software Engineering & Git

> **Phase:** 2 (Core Engineering) · **Time:** ongoing · **Difficulty:** ⭐⭐

## What it is
**Software engineering** is the *discipline* of building software that works, scales, and can be maintained by teams — beyond just writing code. It covers version control, testing, code quality, and collaboration.

## Why it matters
- Knowing a language ≠ being employable. Teams need Git, tests, and clean code.
- Prevents the "works on my machine" nightmare.
- The skill that turns solo scripts into shippable products.

## Git & version control — detailed
**Git** tracks every change to your code.
```bash
git init            # start a repo
git add .          # stage changes
git commit -m "msg"# save a snapshot
git branch feat     # new branch
git checkout feat   # switch
git merge feat      # combine
git push           # upload to GitHub
git pull           # download
```
- **Commit** = a saved snapshot. Write clear messages ("fix login bug", not "stuff").
- **Branch** = an isolated line of work (never break `main`).
- **Pull request (PR)** = propose changes; others review before merge.
- **Merge vs Rebase** — merge keeps history; rebase rewrites it linearly.

## GitHub / GitLab
- Hosting + collaboration: issues, PRs, code review, Actions (CI).
- **Open source:** contribute to real projects (start with docs/typos).

## Testing
- **Unit test:** verifies one function.
- **Integration test:** verifies pieces working together.
- **TDD (Test-Driven Development):** write the test before the code.
- Tools: `pytest` (Python), `jest` (JS), `JUnit` (Java).

## Clean code principles
- **DRY** — Don't Repeat Yourself.
- **KISS** — Keep It Simple, Stupid.
- **Naming** — `calculateTax()` beats `doThing2()`.
- **Small functions** with one responsibility.
- **Comments** explain *why*, not *what*.

## CI/CD (intro)
- **CI** (Continuous Integration): automatically run tests on every push.
- **CD** (Continuous Deployment): automatically ship when tests pass.

## Free resources
- **Git official book (free)**: https://git-scm.com/book/en/v2
- **freeCodeCamp — Git & GitHub**: https://www.youtube.com/watch?v=RGOj5yH7evk
- **GeeksforGeeks — Software Engineering**: https://www.geeksforgeeks.org/software-engineering/
- **Your vault:** [[Ubuntu-WSL-Obsidian-Vault]] for a Linux/WSL dev setup.

## Practice (do from day one)
1. Put **every** project on GitHub.
2. Use **branches** for features; open a PR to merge.
3. Write **tests** for at least one project.
4. **Contribute** to an open-source repo (fix a typo to start).
5. Set up a simple **GitHub Action** that runs your tests.

## Self-check (can you…)
- [ ] Commit, branch, merge confidently
- [ ] Open and review a pull request
- [ ] Write a unit test
- [ ] Explain DRY / KISS with examples

## Progress
- [ ] Confident with Git basics + branching
- [ ] Made a real pull request
- [ ] Write tests regularly
- [ ] Used a linter / CI

## Next
→ [[07 - Computer Architecture]]
