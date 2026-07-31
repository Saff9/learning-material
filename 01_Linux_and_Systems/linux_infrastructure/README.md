# 🗺️ Linux Infrastructure & DevOps — From Zero to Competence

> A self-taught developer’s roadmap for learning Linux, cloud basics, and DevOps tools (CI/CD, Docker, GitOps).

## How to use this vault

1. Start at **01 - Linux Basics** and move down sequentially.
2. Every note has: *What it is* · *Why it matters* · *Hands‑on commands* · *Free resources* · *Practice* · *Progress*.
3. Tick `Progress` as you go; update the [[Linux Infrastructure Progress]] tracker weekly.
4. Use the **Feynman method**: if you can’t explain it simply, you don’t understand it yet.

## 🧭 The Path (12 weeks recommended)

- **Phase 1 – Core Linux:** shell, files, users, sudo, commands (Weeks 1‑3)
- **Phase 2 – Admin:** package management, services, storage, logs (Weeks 4‑6)
- **Phase 3 – DevOps:** containers, CI/CD, git, cloud basics (Weeks 7‑10)
- **Phase 4 – Monitoring & Automation:** scripting, monitoring, incident response (Weeks 11‑12)

## 📚 Recommended resources

- **Linux The Hard Way:** https://www.linuxhandbook.com/ (free ebook)
- **GeeksforGeeks — Linux Tutorials:** https://www.geeksforgeeks.org/linux/
- **Official Docs:** man pages, `tldr`, `overthewire` (capture‑the‑flag)
- **Docker docs:** https://docs.docker.com
- **GitHub:** best practice repos (e.g., GitHub’s default CONTRIBUTING.md)

## 🗂️ Folder structure (for your notes, not to copy)

- `01 - Linux Basics/` — shell, file system, navigation
- `02 - Users & Permissions/` — sudo, ACLs
- `03 - Package Management/` — apt, yum, rpm, compose
- `04 - System Services/` — systemctl, systemd
- `05 - Storage & Backups/` — LVM, files, tar
- `06 - Security & Auditing/` — firewalld, SELinux, login audits
- `07 - Networking/` — basics, bonds, bridges, DNS
- `08 - Containers/` — Docker concepts, compose, swarm
- `09 - CI/CD & Automation/` — GitHub Actions, Terraform basics
- `10 - Cloud Foundations/` — AWS/Azure/GCP, storage objects
- `11 - Monitoring & Observability/` — logs, alerts, Prometheus/Grafana
- `12 - Projects & DevOps Integration/` — capstone projects

## 📅 Suggested schedule

| Week | Topics | Focus |
|------|--------|-------|
| 1‑2  | Shell basics, file ops, basics | Practice daily on a local VM
a
| 3    | Users, groups, sudo, permissions | Setup home lab
a
| 4‑5  | Package managers, script installation
a
| 6‑7  | Services, systemd, logs
a
| 8‑9  | Storage, networking basics
a
| 10   | Container basics, Docker CLI
a
| 11   | Git workflows, CI basics
a
| 12   | Small project building (capstone)
a
## 💡 Tips

- **Write commands in Markdown** and practice in a local VM or WSL2.
- **Use `tldr`:** `tldr mkdir` for quick commands.
- **Automate daily**: one script per day.
- **Err on safety**: `sudo` essential; master it.
- **Version control everything**: even systemd configs.

---

See also your existing vault notes on PostgreSQL and Flask.
