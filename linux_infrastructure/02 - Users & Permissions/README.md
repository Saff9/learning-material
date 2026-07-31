# 02 - Users & Permissions

> **Phase:** 1 (Core Linux) · **Time:** ~2‑3 weeks · **Difficulty:** ⭐⭐

## What it is
The **user and permission system** in Linux is how the OS controls who can do what, from reading files to executing scripts and making system changes. It’s the foundation of security and teamwork.

We’ll cover:
- **User accounts** and groups
- **sudo** (administrative access)
- **Ownership**, **permissions**, and **ACL basics**
- **SUDOers**, **wheel groups**, and privilege escalation controls

## Why it matters
- **Security:** correct permissions keep data safe.
- **Collaboration:** multiple users share resources without stepping on each other.
- **Automation/admin:** you need `sudo` to install packages, edit configs, and manage services.
- **CI/CD pipelines:** running as correct users (e.g., `node` vs root) is essential for safety.

## Core concepts — detailed

### 1. Users, groups, and UID/GID
| Entity | What it is | Typical values |
|---|---|---|
| **User** | A login identity (who you are). Identified by UID (numeric) and name. | Regular users: 1000‑1999. **root** (UID 0) = superuser. |
| **Group** | Logical collection of users (security context). Identified by GID. | **root** (GID 0), **users** (GID 100), **docker** (dynamic). |
| **Primary group** | default group for the user (stored in `/etc/passwd`). |
| **Supplementary groups** | extra groups user belongs to (e.g., `docker`, `staff`). |

**Command to inspect a user:**
```bash
id username             # UID, GID, groups
sudo -u username whoami # the effective user you'll become
```

### 2. Standard Linux user hierarchy (quick cheat‑sheet)
```text
/home/username/        # user’s home directory (files, scripts)
/tmp/                  # temporary storage (cleared on reboot)
/var/log/              # logs (audit, auth, system)
/etc/passwd            # user database (name:UID:GID:home)
/etc/group             # group database
/etc/shadow            # encrypted passwords (root‑only)
/etc/sudoers          # sudo policies (root‑only)
```

### 3. Creating and managing users (with safety)
**Adding a regular user (interactive):**
```bash
sudo adduser alice
```
**Adding a user non‑interactively (for automation):**
```bash
sudo useradd -m -s /bin/bash alice   # -m creates home, -s shell
sudo passwd alice                # set password (requires tty or `chpasswd`)
```

**Adding to groups:**
```bash
sudo usermod -aG sudo alice    # alice can run sudo (watch privileges!)
sudo usermod -aG docker alice  # for Docker runtime
```

**Checking a user’s groups:**
```bash
sudo id alice
```

### 4. Passwords and locking accounts
**Locks users:**
```bash
sudo passwd -l bob        # lock (login disabled)
sudo passwd -u bob        # unlock
```

**Expired passwords (administrative):**
```bash
sudo chage -E 2026-01-01 bob   # expire on date
sudo chage -l bob            # lock
```

### 5. sudo (admin access) fundamentals
**sudoers rules** are in `/etc/sudoers` (edit only with `visudo`).

**Common patterns (see `/etc/sudoers.d/`):**
```conf
# Allow alice to run anything as root
alice ALL=(ALL:ALL) ALL
# Allow group `wheel` (default many distros) to sudo
%wheel ALL=(ALL) ALL
```

**Typical workflow:**
```bash
# Without sudo (won’t work)
someadmincommand

# With sudo (prompt for password)
sudo someadmincommand

# Run another command as a different user (rare, requires setup)
sudo -u www-data systemctl restart nginx
```

**Configure sudo:**
- `/etc/sudoers.d/example` → `username ALL=(ALL) NOPASSWD: ALL` (dangerous!).
- Use `!requiretty` to force terminal for security.

### 6. Permissions deep‑dive
**Numeric:** `r=4, w=2, x=1` (e.g., `755`).
- `chmod 755 script.sh` → owner: rwx, group/others: rx.
- `chmod 644 file.txt` → owner: rw-, group/others: r-.

**Symbolic:**
```bash
# grant read to group
chmod g+r important.txt
# remove all permissions for others (better: set to private)
chmod o= important.txt
# make a script executable
chmod +x deploy.sh
chmod 755 deploy.sh   # same effect
```

**Ownership:**
```bash
# who owns it?
ls -l important.txt

# change owner and group
chown bob:admin important.txt
chown :admin important.txt   # only group
chown bob                   # both (primary group from bob)
```

### 7. ACLs (Access Control Lists) — optional.
```bash
# Install if supported
sudo apt install acl
# Set an ACL (example)
sudo setfacl -m u:alice:rwx /shared/report.pdf
# List ACLs
ls -l /shared/report.pdf
```
> ACLs give you more granular control beyond traditional perms.

## Free resources — tailored for self‑learners

1. **Linux The Hard Way — Chapter “Passwords”**:
   - https://www.linuxhandbook.com/ (Lesson 12)
2. **`man 5 passwd`**, `man 5 group`, `man 5 sudoers` (online at https://man7.org/linux/man-pages/man5/passwd.5.html)
3. **OverTheWire Bandit** (Wargame #1‑) — perfect for learning file permissions and sudo:
   - https://overthewire.org/wargames/bandit/
4. **Red Hat – User & Group Management Docs**:
   - https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/
5. **Sudo documentation**:
   - https://www.sudo.ws/man/1.8.21/sudoers.html (for visudo)
6. **`sudo` quick cheat sheet** (download via `curl` or your browser):
   - https://github.com/iamthefij/sudo-cheat-sheet

## Practice labs (save each command in a script, test in safe directories)

### Lab 1: User and group exploration
```bash
# List existing users (filter)
sudo cat /etc/passwd | grep -E '^(bob|alice|root)' || echo "users not found"

# Show a user’s primary + supplementary groups
sudo id alice

# Examine a file’s UID/GID ownership
ls -l /etc/shadow
```

### Lab 2: Create and configure a user
```bash
# Create a non‑interactive user (no login shell required for services)
sudo useradd -r -s /bin/false monitoring
# -> -r (system user), -s (shell)
# Set a password (non‑interactive)
echo "monitoring:SecurePass123" | sudo chpasswd
# Check user
id monitoring
# Add to group `docker` (for later container work)
sudo usermod -aG docker monitoring
```

### Lab 3: Sudo permissions (safe test)
```bash
# Grant sudo rights (TESTING is a safe namespace)
sudo adduser testing sudo

# Verify with sudo -l (list permissions)
sudo -l -U testing

# Run a read‑only sudo command (e.g., listing users)
sudo -u nobody id
```

### Lab 4: File permissions:
```bash
# Create a file owned by alice (as root)
sudo touch /tmp/secret.txt
sudo chown alice:admin /tmp/secret.txt

# Set permissions: alice can r/w, group/others r
h sudo chmod 644 /tmp/secret.txt

# Alice tries to read it (switch user temporarily)
sudo -u alice cat /tmp/secret.txt
```

### Lab 5: ACLs (if supported)
```bash
# Create a directory for ACL test
mkdir /tmp/shared
sudo chmod 777 /tmp/shared  # permissive for testing

# Set ACL for user alice (rw)
sudo setfacl -m u:alice:rwx /tmp/shared

# List ACLs
ls -l /tmp/shared
```

## Self‑check (can you…)
- [ ] Explain UID/GID, primary vs supplementary groups
- [ ] Create a regular user and set a password
- [ ] Add a user to a group (`sudo`) safely
- [ ] Describe what `sudo` does, how to invoke it, and why it’s needed
- [ ] Modify file ownership and permissions with `chown` and `chmod`
- [ ] Use ACLs when extra granularity is required

## Progress
- [ ] Completed Labs 1‑5 (use safe test directories, verify output)
- [ ] Explain the purpose of `/etc/passwd`, `/etc/group`, `/etc/shadow`
- [ ] Run a command as a different user with `sudo` successfully
- [ ] Created at least one user and modified its groups
- [ ] Set up a local user account for future practice

## Link to next module
→ [[03 - Package Management]]
