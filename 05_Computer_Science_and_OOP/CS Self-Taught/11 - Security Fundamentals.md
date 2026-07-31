# 11 - Security Fundamentals

> **Phase:** 4 (Security & Career) · **Time:** ~3–4 weeks · **Difficulty:** ⭐⭐

## What it is
**Security** is protecting systems and data from attackers — through cryptography, secure design, and awareness of common vulnerabilities.

## Why it matters
- Security bugs are costly, public, and common.
- Every developer should ship code that isn't trivially exploitable.
- Growing field with strong demand (AppSec, pentesting, cryptography).

## Core concepts — detailed

### Cryptography basics
- **Hashing:** one-way (passwords stored as `bcrypt`/`argon2`, never plaintext).
- **Symmetric encryption:** same key to lock/unlock (AES).
- **Asymmetric:** public key encrypts, private key decrypts (RSA, ECC).
- **Salts** prevent rainbow-table attacks on passwords.

### Authentication vs Authorization
- **AuthN:** *who are you?* (login, passwords, OAuth, MFA).
- **AuthZ:** *what can you do?* (roles, permissions).

### OWASP Top 10 (know these)
1. **Injection** (SQL injection) — unescaped input in queries.
2. **Broken Authentication** — weak login/session handling.
3. **Sensitive Data Exposure** — no encryption in transit.
4. **XML External Entities (XXE)**.
5. **Broken Access Control** — users reach others' data.
6. **Security Misconfiguration.**
7. **Cross-Site Scripting (XSS)** — injected scripts in pages.
8. **Insecure Deserialization.**
9. **Using Components with Known Vulns.**
10. **Insufficient Logging & Monitoring.**

### HTTPS / TLS
- Encrypts traffic in transit via certificates.
- Always use HTTPS; redirect HTTP→HTTPS.

### Secrets & secure design
- Never hardcode API keys / passwords.
- Use env vars or a secrets manager.
- Validate and sanitize **all** user input.

## Free resources
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **TeachYourselfCS — Security**: https://teachyourselfcs.com/
- **GeeksforGeeks — Cyber Security**: https://www.geeksforgeeks.org/cyber-security/
- **PortSwigger Web Security Academy (free labs)**: https://portswigger.net/web-security
- **Crypto 101 (free book)**: https://crypto101.io/

## Practice (hands-on)
1. **Find + fix** an SQL injection in a demo app (use prepared statements).
2. Store passwords with **bcrypt**, never plaintext.
3. Complete **3 PortSwigger labs** (XSS, SQLi).
4. Run a **security linter** on one of your projects.

## Self-check (can you…)
- [ ] Explain hashing vs encryption
- [ ] Name + describe OWASP Top 10
- [ ] Use HTTPS and prepared statements
- [ ] Store passwords securely

## Progress
- [ ] Understand hashing & encryption
- [ ] Know OWASP Top 10
- [ ] Done secure-coding practice
- [ ] Completed PortSwigger labs

## Next
→ [[12 - Career & Job Prep]]
