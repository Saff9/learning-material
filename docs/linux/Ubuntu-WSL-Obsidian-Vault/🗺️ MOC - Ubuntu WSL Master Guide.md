# 🐧 Ubuntu on WSL - Complete MOC

> **Your single reference for mastering Linux (Ubuntu) through WSL. A-Z, from zero to power user.**

---

## 📚 Table of Contents

| Section                                                       | Description                          | Status |
| ------------------------------------------------------------- | ------------------------------------ | ------ |
| [[01 - Getting Started/01.01 - What is Linux]]                | Philosophy, distributions, why Linux | ⬜      |
| [[01 - Getting Started/01.02 - WSL Setup Guide]]              | Installing, configuring WSL2         | ⬜      |
| [[01 - Getting Started/01.03 - First Login]]                  | Your first commands, navigation      | ⬜      |
| [[01 - Getting Started/01.04 - Terminal Basics]]              | Shell, prompt, keyboard shortcuts    | ⬜      |
| [[02 - Core Concepts/02.01 - Everything is a File]]           | The Unix philosophy                  | ⬜      |
| [[02 - Core Concepts/02.02 - The Linux Architecture]]         | Kernel, shell, userspace             | ⬜      |
| [[02 - Core Concepts/02.03 - Standard Streams]]               | stdin, stdout, stderr                | ⬜      |
| [[02 - Core Concepts/02.04 - Pipes and Redirection]]          | Connecting commands                  | ⬜      |
| [[03 - File System/03.01 - Directory Hierarchy]]              | FHS - Filesystem Hierarchy Standard  | ⬜      |
| [[03 - File System/03.02 - Navigation Commands]]              | cd, ls, pwd, tree                    | ⬜      |
| [[03 - File System/03.03 - Path Types]]                       | Absolute vs relative paths           | ⬜      |
| [[03 - File System/03.04 - Special Directories]]              | ., .., ~, -                          | ⬜      |
| [[03 - File System/03.05 - Mount Points]]                     | Understanding mounts in WSL          | ⬜      |
| [[04 - Essential Commands/04.01 - Command Structure]]         | Syntax, options, arguments           | ⬜      |
| [[04 - Essential Commands/04.02 - Getting Help]]              | man, --help, apropos, info           | ⬜      |
| [[04 - Essential Commands/04.03 - Command History]]           | history, !, Ctrl+R                   | ⬜      |
| [[04 - Essential Commands/04.04 - Tab Completion]]            | Bash completion                      | ⬜      |
| [[05 - File Operations/05.01 - Creating Files]]               | touch, mkdir, nano, vim              | ⬜      |
| [[05 - File Operations/05.02 - Viewing Files]]                | cat, less, more, head, tail          | ⬜      |
| [[05 - File Operations/05.03 - Copying Moving]]               | cp, mv, rsync                        | ⬜      |
| [[05 - File Operations/05.04 - Deleting]]                     | rm, rmdir, shred                     | ⬜      |
| [[05 - File Operations/05.05 - Finding Files]]                | find, locate, which, whereis         | ⬜      |
| [[05 - File Operations/05.06 - Comparing Files]]              | diff, cmp, comm                      | ⬜      |
| [[05 - File Operations/05.07 - Archiving]]                    | tar, gzip, zip, unzip                | ⬜      |
| [[06 - Text Processing/06.01 - grep]]                         | Pattern searching                    | ⬜      |
| [[06 - Text Processing/06.02 - sed]]                          | Stream editor                        | ⬜      |
| [[06 - Text Processing/06.03 - awk]]                          | Text processing language             | ⬜      |
| [[06 - Text Processing/06.04 - cut and paste]]                | Column operations                    | ⬜      |
| [[06 - Text Processing/06.05 - sort and uniq]]                | Sorting and deduplication            | ⬜      |
| [[06 - Text Processing/06.06 - wc and nl]]                    | Counting and numbering               | ⬜      |
| [[06 - Text Processing/06.07 - tr]]                           | Character translation                | ⬜      |
| [[06 - Text Processing/06.08 - xargs]]                        | Building command lines               | ⬜      |
| [[07 - User & Permissions/07.01 - Users and Groups]]          | /etc/passwd, /etc/group              | ⬜      |
| [[07 - User & Permissions/07.02 - File Permissions]]          | rwx, chmod, chown                    | ⬜      |
| [[07 - User & Permissions/07.03 - Special Permissions]]       | SUID, SGID, Sticky Bit               | ⬜      |
| [[07 - User & Permissions/07.04 - ACLs]]                      | Access Control Lists                 | ⬜      |
| [[07 - User & Permissions/07.05 - sudo]]                      | Superuser do                         | ⬜      |
| [[08 - Process Management/08.01 - What is a Process]]         | PID, PPID, init/systemd              | ⬜      |
| [[08 - Process Management/08.02 - Viewing Processes]]         | ps, top, htop, pgrep                 | ⬜      |
| [[08 - Process Management/08.03 - Controlling Processes]]     | kill, nice, nohup, jobs              | ⬜      |
| [[08 - Process Management/08.04 - Background and Foreground]] | &, fg, bg                            | ⬜      |
| [[08 - Process Management/08.05 - Scheduling]]                | cron, at, systemd timers             | ⬜      |
| [[09 - Networking/09.01 - Network Basics]]                    | IP, ports, protocols                 | ⬜      |
| [[09 - Networking/09.02 - Network Commands]]                  | ip, ss, ping, traceroute, curl       | ⬜      |
| [[09 - Networking/09.03 - SSH]]                               | Secure shell, keys, config           | ⬜      |
| [[09 - Networking/09.04 - Firewall]]                          | ufw, iptables basics                 | ⬜      |
| [[09 - Networking/09.05 - WSL Networking]]                    | WSL2 network architecture            | ⬜      |
| [[10 - Package Management/10.01 - apt and apt-get]]           | Installing, updating, removing       | ⬜      |
| [[10 - Package Management/10.02 - dpkg]]                      | Low-level package management         | ⬜      |
| [[10 - Package Management/10.03 - Snap]]                      | Ubuntu snap packages                 | ⬜      |
| [[10 - Package Management/10.04 - Repositories]]              | Sources, PPAs, mirrors               | ⬜      |
| [[11 - System Administration/11.01 - System Information]]     | uname, lsb_release, hostname         | ⬜      |
| [[11 - System Administration/11.02 - Disk Management]]        | df, du, fdisk, lsblk                 | ⬜      |
| [[11 - System Administration/11.03 - Memory Management]]      | free, vmstat, /proc/meminfo          | ⬜      |
| [[11 - System Administration/11.04 - System Services]]        | systemctl, service                   | ⬜      |
| [[11 - System Administration/11.05 - Logging]]                | journalctl, /var/log                 | ⬜      |
| [[11 - System Administration/11.06 - Environment Variables]]  | env, export, .bashrc                 | ⬜      |
| [[12 - Shell Scripting/12.01 - Bash Basics]]                  | Variables, conditionals, loops       | ⬜      |
| [[12 - Shell Scripting/12.02 - Functions]]                    | Defining and using functions         | ⬜      |
| [[12 - Shell Scripting/12.03 - Script Structure]]             | Shebang, exit codes, best practices  | ⬜      |
| [[12 - Shell Scripting/12.04 - Practical Scripts]]            | Real-world examples                  | ⬜      |
| [[13 - WSL Specific/13.01 - WSL Architecture]]                | WSL1 vs WSL2                         | ⬜      |
| [[13 - WSL Specific/13.02 - Windows Integration]]             | Accessing Windows files, interop     | ⬜      |
| [[13 - WSL Specific/13.03 - WSL Configuration]]               | wsl.conf, .wslconfig                 | ⬜      |
| [[13 - WSL Specific/13.04 - GUI Apps]]                        | Running graphical applications       | ⬜      |
| [[13 - WSL Specific/13.05 - WSL Tips and Tricks]]             | Power user techniques                | ⬜      |
| [[14 - Development Environment/14.01 - Git Setup]]            | Version control on WSL               | ⬜      |
| [[14 - Development Environment/14.02 - Node.js and Python]]   | Language environments                | ⬜      |
| [[14 - Development Environment/14.03 - Docker in WSL]]        | Containerization                     | ⬜      |
| [[14 - Development Environment/14.04 - VS Code Integration]]  | Remote WSL extension                 | ⬜      |
| [[14 - Development Environment/14.05 - Databases]]            | MySQL, PostgreSQL, Redis             | ⬜      |
| [[14 - Development Environment/14.06 - Zsh and Tmux]]         | Terminal multiplexer and power shell | ⬜      |
| [[15 - Troubleshooting/15.01 - Common Issues]]                | Fixes for frequent problems          | ⬜      |
| [[15 - Troubleshooting/15.02 - Debugging Commands]]           | strace, dmesg, lsof                  | ⬜      |
| [[15 - Troubleshooting/15.03 - WSL Specific Issues]]          | WSL troubleshooting                  | ⬜      |
| [[99 - Cheat Sheets/99.01 - Command Reference]]               | Quick command lookup                 | ⬜      |
| [[99 - Cheat Sheets/99.02 - Vim Cheatsheet]]                  | Vim quick reference                  | ⬜      |
| [[99 - Cheat Sheets/99.03 - Regex Reference]]                 | Regular expressions                  | ⬜      |
| [[99 - Cheat Sheets/99.04 - Keyboard Shortcuts]]              | Terminal shortcuts                   | ⬜      |
| [[99 - Cheat Sheets/99.05 - Zsh Tmux Cheatsheet]]             | Zsh & Tmux Master Cheatsheet         | ⬜      |

---

## 🗺️ Learning Path

```
Week 1: Getting Started → Core Concepts → File System
Week 2: Essential Commands → File Operations → Text Processing
Week 3: Users & Permissions → Process Management → Networking
Week 4: Package Management → System Administration → Shell Scripting
Week 5: WSL Specific → Development Environment → Troubleshooting
```

## 🔗 Quick Links

- [[99 - Cheat Sheets/99.01 - Command Reference|📋 Command Reference]]
- [[99 - Cheat Sheets/99.04 - Keyboard Shortcuts|⌨️ Keyboard Shortcuts]]
- [[99 - Cheat Sheets/99.02 - Vim Cheatsheet|📝 Vim Cheatsheet]]
- [[99 - Cheat Sheets/99.05 - Zsh Tmux Cheatsheet|🚀 Zsh & Tmux Cheatsheet]]

## 📝 Daily Practice Template

```markdown
## $(date +%Y-%m-%d) - Linux Practice Log

### Commands Learned Today:
- 

### Concepts Understood:
- 

### Issues Encountered:
- 

### Tomorrow's Goal:
- 
```

---

> **💡 Pro Tip:** Use `Ctrl+Click` on any `[[link]]` to navigate between notes. This vault is designed for discovery—follow the links!
