# 02 - Linux Users, Groups & Permissions (Production & Enterprise Administration Guide)

> **Phase:** 1 (Core Linux Systems Infrastructure) · **Target Audience:** System Administrators, DevOps Engineers, Security Operations · **Difficulty:** Intermediate to Advanced ⭐⭐

---

## Executive Summary & Module Overview
The Linux user, group, and privilege architecture forms the cornerstone of operating system security, process isolation, and multi-tenant resource control. In enterprise environments, proper identity management and fine-grained permission models prevent privilege escalation, data breaches, and service misconfigurations.

This guide provides an end-to-end, production-grade reference covering:
- **Linux Identity Architecture:** UID/GID mechanics, system vs human accounts, kernel process credentials (`ruid`, `euid`, `suid`), and account database schemas (`/etc/passwd`, `/etc/shadow`, `/etc/group`, `/etc/gshadow`).
- **User & Group Lifecycle Management:** Non-interactive service accounts, password aging policies, batch user provisioning, and secure account offboarding.
- **POSIX Permissions & Special Bits:** Octal/symbolic calculations, `umask` dynamics, SUID, SGID, and Sticky Bit mechanics.
- **Extended Access Control Lists (POSIX ACLs):** Overcoming traditional single-owner limitations with `setfacl`, `getfacl`, and default directory masks.
- **File System Attributes:** Kernel-level immutability (`chattr +i`) and append-only log protection (`chattr +a`).
- **Privilege Escalation Control & Sudoers:** Custom `/etc/sudoers.d/` policy design, alias definition, passwordless rules, security defaults, and `visudo` validation.
- **Troubleshooting & Diagnostic Matrix:** Step-by-step resolution paths for complex permission and identity failures.
- **Real-World Infrastructure Scenarios:** Multi-tenant web directories and hardened database backup service accounts.
- **Hands-On Guided Labs:** Practical exercises to test and reinforce production skills.

---

## 1. Deep Dive: Linux Identity Architecture & Data Stores

### 1.1 User & Group Classification
Linux categorizes identity objects by numeric Identifiers (UID for Users, GID for Groups):

| Category | UID Range (Debian/Ubuntu) | UID Range (RHEL/Rocky/Fedora) | Purpose / Characteristics |
|---|---|---|---|
| **Root (Superuser)** | `0` | `0` | Absolute privileges; bypasses standard file permission checks. |
| **System Users** | `1 – 999` | `1 – 999` (or `1 – 499`) | Daemon & service execution context (`nginx`, `postgres`, `systemd-resolve`). Shell set to `/sbin/nologin` or `/bin/false`. No interactive logins. |
| **Regular Users** | `1000 – 59999` | `1000 – 60000` | Human administrators, developers, and deployment accounts. Shell defaults to `/bin/bash` or `/bin/zsh`. |
| **Reserved / Ephemeral** | `60000+` / `65534` | `60000+` / `65534` | Container mapping, system overflow, and legacy unprivileged `nobody` account (UID `65534`). |

---

### 1.2 Kernel Process Credentials (RUID vs EUID vs SUID vs FSUID)
Every Linux process runs with four sets of user/group IDs that determine what resources it can access:

```text
  +-------------------------------------------------------------------+
  |                       Linux Process Context                       |
  |                                                                   |
  |   +-----------------------+     +-----------------------------+   |
  |   |  Real UID (RUID)      |     |  Effective UID (EUID)       |   |
  |   |  Identity of owner    |     |  Rights used for syscalls   |   |
  |   +-----------------------+     +-----------------------------+   |
  |   +-----------------------+     +-----------------------------+   |
  |   |  Saved UID (SUID)     |     |  FileSystem UID (FSUID)     |   |
  |   |  Pre-privilege drop   |     |  Rights used for file I/O   |   |
  |   +-----------------------+     +-----------------------------+   |
  +-------------------------------------------------------------------+
```

- **Real User ID (RUID):** Identifies the user who spawned the process.
- **Effective User ID (EUID):** Evaluated by the kernel for permission checks on system calls. SUID binaries elevate EUID to match the binary owner.
- **Saved Set-User-ID (SUID):** Copies the EUID prior to privilege reduction, allowing processes to toggle back to elevated states when needed.
- **FileSystem User ID (FSUID):** Used specifically for filesystem access verification (typically mirrors EUID unless altered by specialized system servers like NFS).

---

### 1.3 System Identity Databases (File Schema Breakdown)

#### A. `/etc/passwd` — User Account Database
Readable by all users (`644`). Contains primary account definitions.

```text
alice:x:1001:1001:Alice Smith,DevOps Room 302,,:/home/alice:/bin/bash
  |   |  |    |                     |               |          |
  |   |  |    |                     |               |          +--> 7. Default Login Shell
  |   |  |    |                     |               +-------------> 6. Home Directory Path
  |   |  |    |                     +-----------------------------> 5. GECOS / User Comment
  |   |  |    +---------------------------------------------------> 4. Primary Group ID (GID)
  |   |  +--------------------------------------------------------> 3. User ID (UID)
  |   +-----------------------------------------------------------> 2. Password Flag ('x' = stored in /etc/shadow)
  +---------------------------------------------------------------> 1. Account Username
```

#### B. `/etc/shadow` — Encrypted Passwords & Aging Policy
Restricted access (`640` or `600`, root/shadow group only). Stores hashed secrets and account limits.

```text
bob:$6$8zX...$vK8...:19730:7:90:14:30:20818:
 |        |           |    |  |  |  |    |   |
 |        |           |    |  |  |  |    |   +-> 9. Reserved Field
 |        |           |    |  |  |  |    +-----> 8. Absolute Account Expiration Date (days since Epoch)
 |        |           |    |  |  |  +----------> 7. Inactivity Grace Period (days after max before lock)
 |        |           |    |  |  +-------------> 6. Expiration Warning Period (days)
 |        |           |    |  +----------------> 5. Maximum Password Age (days)
 |        |           |    +-------------------> 4. Minimum Password Age (days before change allowed)
 |        |           +------------------------> 3. Date of Last Password Change (days since Jan 1, 1970)
 |        +------------------------------------> 2. Encrypted Password Hash ($6$ = SHA-512, $y$ = yescrypt)
 +---------------------------------------------> 1. Account Username
```

> **Hash Prefix Reference:**
> - `$1$` : MD5 (Legacy)
> - `$5$` : SHA-256
> - `$6$` : SHA-512 (Standard modern Linux)
> - `$y$` : Yescrypt (Modern Debian/Ubuntu standard)
> - `!` or `*` : Account locked / login disabled

#### C. `/etc/group` — Group Account Database
Readable by all users (`644`). Defines primary and secondary group memberships.

```text
docker:x:998:alice,bob,charlie
  |    |  |       |
  |    |  |       +--> 4. Supplementary Group Members (comma-separated usernames)
  |    |  +----------> 3. Group ID (GID)
  |    +-------------> 2. Group Password Placeholder ('x' = stored in /etc/gshadow)
  +------------------> 1. Group Name
```

---

## 2. User & Group Lifecycle Management

### 2.1 User Creation: Binary vs High-Level Tooling

| Feature | `useradd` (Low-Level Binary) | `adduser` (High-Level Perl Script) |
|---|---|---|
| **Portability** | Universal across all Linux distributions. | Debian / Ubuntu family specific. |
| **Mode** | Non-interactive (ideal for automation & shell scripts). | Interactive wizard prompt by default. |
| **Home Directory Creation** | Requires `-m` flag. | Automatic based on `/etc/adduser.conf`. |
| **Defaults Source** | `/etc/default/useradd` and `/etc/login.defs`. | `/etc/adduser.conf`. |

#### Production Non-Interactive User Provisioning Script
```bash
#!/usr/bin/env bash
# ==============================================================================
# Script: create_dev_user.sh
# Purpose: Provision a new developer account with standard enterprise policies
# ==============================================================================
set -euo pipefail

USERNAME="developer1"
PRIMARY_GROUP="developers"
USER_UID="2050"
USER_GID="2050"

# 1. Create primary group if non-existent
if ! getent group "${PRIMARY_GROUP}" >/dev/null; then
    sudo groupadd -g "${USER_GID}" "${PRIMARY_GROUP}"
    echo "[+] Group '${PRIMARY_GROUP}' created with GID ${USER_GID}."
fi

# 2. Provision non-interactive user account
if ! id "${USERNAME}" >/dev/null 2>&1; then
    sudo useradd \
        -u "${USER_UID}" \
        -g "${PRIMARY_GROUP}" \
        -G "docker,sudo" \
        -m \
        -k /etc/skel \
        -s /bin/bash \
        -c "Senior Backend Engineer" \
        "${USERNAME}"
    echo "[+] User '${USERNAME}' created successfully."
fi

# 3. Set temporary password and force change on initial login
echo "${USERNAME}:TempPass#2026!ChangeMe" | sudo chpasswd
sudo chage -d 0 "${USERNAME}"
echo "[+] Password configured and forced rotation flag set."
```

---

### 2.2 System Service Accounts (Security Lockdown Pattern)
Service accounts for applications (`nginx`, `redis`, `prometheus`) must never have interactive login capabilities or home directory shell access.

```bash
# Provision a isolated system service account
sudo useradd \
    --system \
    --no-create-home \
    --home-dir /var/lib/myapp \
    --shell /usr/sbin/nologin \
    --comment "App Engine Daemon Account" \
    myappdaemon

# Verify shell restriction
getent passwd myappdaemon
# Output: myappdaemon:x:995:995:App Engine Daemon Account:/var/lib/myapp:/usr/sbin/nologin
```

---

### 2.3 Account Expiration, Password Aging & Locking
Administrators must manage credential lifecycles using `chage`, `usermod`, and `passwd`.

```bash
# Display detailed aging statistics for user 'alice'
sudo chage -l alice

# Set Password Aging Rules:
# - Minimum days between password changes: 7
# - Maximum password validity: 90 days
# - Expiration warning window: 14 days
# - Account disable after expiry grace: 30 days
sudo chage -m 7 -M 90 -W 14 -I 30 alice

# Lock user account immediately (prepends '!' to /etc/shadow hash)
sudo usermod -L alice

# Verify locked state in /etc/shadow
sudo grep "^alice:" /etc/shadow

# Unlock user account
sudo usermod -U alice

# Set absolute account expiration date (YYYY-MM-DD)
sudo usermod -e 2026-12-31 alice
```

---

### 2.4 Secure Account Deprovisioning Protocol
When offboarding users, files must be audited and backed up before removal to preserve organizational data integrity.

```bash
#!/usr/bin/env bash
# Offboard user safely
TARGET_USER="developer1"
BACKUP_DIR="/var/backups/offboarded_users"

sudo mkdir -p "${BACKUP_DIR}"

# 1. Terminate all active processes owned by user
sudo pkill -u "${TARGET_USER}" || true

# 2. Archive home directory and mail spool
sudo tar -czvf "${BACKUP_DIR}/${TARGET_USER}_backup_$(date +%F).tar.gz" \
    "/home/${TARGET_USER}" \
    "/var/mail/${TARGET_USER}" 2>/dev/null || true

# 3. Delete account and home directory
sudo userdel -r "${TARGET_USER}"

# 4. Audit system for orphaned files previously owned by deleted UID
echo "[*] Scanning for orphaned files..."
sudo find / -nouser -o -nogroup -exec ls -ld {} + 2>/dev/null || true
```

---

## 3. Standard & Advanced POSIX Permissions

### 3.1 Standard Permission Matrix

Permissions operate on three target classes: **Owner (u)**, **Group (g)**, and **Others (o)**.

```text
   File Type (-=File, d=Dir, l=Link)
   |
   |   User/Owner (u)    Group (g)       Others (o)
   |   +-----------+   +-----------+   +-----------+
   -   r   w   x       r   -   x       r   -   -
       |   |   |       |   |   |       |   |   |
       4   2   1       4   0   1       4   0   0    ==> Octal Mode: 754
```

#### Permission Evaluation Rules:
1. **Read (`r` / 4):**
   - *File:* Read file content (`cat`, `grep`).
   - *Directory:* Read directory index (`ls`).
2. **Write (`w` / 2):**
   - *File:* Modify file content (`echo >>`, `vim`).
   - *Directory:* Create, delete, rename, or move files inside directory (requires `x` access).
3. **Execute (`x` / 1):**
   - *File:* Execute binary or shell script.
   - *Directory:* Traverse into directory (`cd`) and access inode metadata (`ls -l` contents).

---

### 3.2 Umask Dynamics (Calculation & Configuration)

`umask` filters out permission bits during file and directory creation.

- **Base Maximum Mode:** Files = `666` (`rw-rw-rw-`), Directories = `777` (`rwxrwxrwx`)
- **Calculation Formula:** `Effective Permissions = Base Mode AND NOT (Umask)`

#### Standard Umask Mapping Table:

| Umask Value | File Mode Created | Directory Mode Created | Common Usage Context |
|---|---|---|---|
| `0022` | `644` (`rw-r--r--`) | `755` (`rwxr-xr-x`) | Standard system default for users. |
| `0027` | `640` (`rw-r-----`) | `750` (`rwxr-x---`) | Hardened environment (Group read, others blocked). |
| `0077` | `600` (`rw-------`) | `700` (`rwx------`) | Strict security mode (Owner only). |

```bash
# Check current shell umask
umask

# Set temporary umask for current session
umask 0027

# Test file creation
touch test_file.txt && mkdir test_dir
ls -ld test_file.txt test_dir
# Output file: -rw-r----- (640)
# Output dir:  drwxr-x--- (750)
```

To configure persistent system-wide defaults, update `/etc/profile`, `/etc/bashrc`, or `/etc/login.defs` (setting `UMASK 027`).

---

### 3.3 Special Permissions: SUID, SGID, and Sticky Bit

Special permission bits occupy the lead digit in 4-digit octal notation (`4000`, `2000`, `1000`).

```text
  Octal Digit 1: Special Bits (SUID=4, SGID=2, Sticky=1)
  Octal Digit 2: Owner Permissions
  Octal Digit 3: Group Permissions
  Octal Digit 4: Other Permissions
```

#### Detailed Special Bits Table:

| Bit Name | Octal Value | Symbolic Flag | Effect on Executable Files | Effect on Directories | Practical Use Case |
|---|---|---|---|---|---|
| **SUID** (Set User ID) | `4000` | `u+s` (`rws------`) | Process executes with privileges of the file **owner**, regardless of who invokes it. | No standard effect on Linux binaries. | `/usr/bin/passwd` (allows users to update `/etc/shadow` owned by root). |
| **SGID** (Set Group ID) | `2000` | `g+s` (`rwxrws---`) | Process executes with privileges of the file **group**. | Newly created files/dirs inside inherit the directory's **group ownership**. | Shared collaborative team directories (`/srv/project_files`). |
| **Sticky Bit** | `1000` | `o+t` (`rwxrwxrwt`) | Legacy memory execution flag (obsolete). | Prevents non-owner users from deleting or renaming files they don't own. | Shared temporary dropboxes (`/tmp`, `/var/tmp`). |

#### Production Commands for Special Bits:
```bash
# 1. Apply SGID to a shared directory
sudo mkdir -p /srv/shared_dev
sudo chown root:developers /srv/shared_dev
sudo chmod 2770 /srv/shared_dev    # Octal 2770 (u=rwx, g=rws, o=---)

# 2. Apply Sticky Bit to a public directory
sudo chmod 1777 /tmp/custom_drop    # Octal 1777 (u=rwx, g=rwx, o=rwt)

# 3. Security Audit: Scan system for unauthorized SUID/SGID binaries
sudo find / -type f \( -perm -4000 -o -perm -2000 \) -exec ls -ld {} + 2>/dev/null
```

---

## 4. Extended Access Control Lists (POSIX ACLs)

Standard Linux permissions limit file ownership to a single user and single group. POSIX ACLs allow granting access to multiple distinct users and groups.

```text
  Standard Permission Model:         POSIX Extended ACL Model:
  +------------------------+        +--------------------------------+
  | Owner:  alice (rw-)    |        | Owner:  alice (rw-)            |
  | Group:  devs  (r--)    |  ===>  | Group:  devs  (r--)            |
  | Others: none  (---)    |        | User:   charlie (rw-)  [ACL]   |
  +------------------------+        | Group:  auditors (r--) [ACL]   |
                                    +--------------------------------+
```

### 4.1 ACL Management: `setfacl` & `getfacl`

```bash
# View active ACL entries for a file
getfacl /srv/app/config.json

# Grant specific user 'charlie' read-write access
sudo setfacl -m u:charlie:rw- /srv/app/config.json

# Grant specific group 'auditors' read-only access
sudo setfacl -m g:auditors:r-- /srv/app/config.json

# Set DEFAULT ACL on directory (automatically inherited by all future created child files)
sudo setfacl -d -m g:developers:rwx /srv/app/data/
sudo setfacl -d -m u:ci_bot:rwx /srv/app/data/

# Remove a specific user ACL rule
sudo setfacl -x u:charlie /srv/app/config.json

# Remove ALL extended ACL rules (revert to traditional POSIX)
sudo setfacl -b /srv/app/config.json
```

#### Interpreting `ls -l` ACL Indicator:
When an extended ACL is active on a file, `ls -l` appends a `+` symbol to the permission string:
`-rw-rw-r--+ 1 root root 2048 Jul 31 12:00 config.json`

---

### 4.2 Understanding the ACL Mask
The `mask:` line defines the **maximum permission limit** for all named users, named groups, and the group owner.

- If user `charlie` has ACL permission `rwx`, but the `mask` is set to `r--`, `charlie`'s **effective permission** is `r--`.
- Recalculate or fix mask:
  ```bash
  sudo setfacl -m m::rwx /srv/app/config.json
  ```

---

## 5. Linux File System Attributes (`chattr` & `lsattr`)

Linux Ext4/XFS filesystems support low-level attributes that override standard POSIX permissions, binding directly at the inode layer.

```bash
# 1. Apply Immutable attribute (+i)
# File cannot be modified, deleted, renamed, overwritten, or linked — even by ROOT!
sudo chattr +i /etc/resolv.conf

# Verify active attributes
lsattr /etc/resolv.conf
# Output: ----i---------e---- /etc/resolv.conf

# Test modification attempt as root (Will fail: Operation not permitted)
# echo "nameserver 1.1.1.1" >> /etc/resolv.conf

# Remove immutable attribute
sudo chattr -i /etc/resolv.conf

# 2. Apply Append-Only attribute (+a)
# File can only be opened in append mode (ideal for protecting log files from truncation)
sudo chattr +a /var/log/application_audit.log

# Verify append-only attribute
lsattr /var/log/application_audit.log
# Output: -----a--------e---- /var/log/application_audit.log
```

---

## 6. Privilege Escalation Control & Sudoers

The `sudo` utility grants delegated execution privileges under the root context while maintaining strict audit logging.

### 6.1 `sudoers` Syntax Architecture
Configuration files must **ALWAYS** be edited using `visudo` to prevent syntax errors that lock out system access.

```text
# Syntax Format:
# User/Group  Host_Spec = (RunAs_User : RunAs_Group) [Flags] Command_Path

alice         ALL = (ALL : ALL) ALL
%sysadmins    ALL = (root : root) NOPASSWD: /usr/bin/systemctl restart *
```

---

### 6.2 Modular Sudo Policies in `/etc/sudoers.d/`

Instead of editing `/etc/sudoers` directly, add drop-in files to `/etc/sudoers.d/`.

```conf
# File: /etc/sudoers.d/91-devops-policy
# ==============================================================================
# Aliases
# ==============================================================================
User_Alias DEVOPS_TEAM = alice, bob, charlie
Cmnd_Alias SERVICE_MGMT = /usr/bin/systemctl restart nginx, /usr/bin/systemctl status nginx, /usr/bin/systemctl reload nginx
Cmnd_Alias LOG_VIEW = /usr/bin/journalctl, /usr/bin/tail -f /var/log/*

# ==============================================================================
# User Rules
# ==============================================================================
# Allow DevOps team to run service commands and view logs without password prompt
DEVOPS_TEAM ALL=(root) NOPASSWD: SERVICE_MGMT, LOG_VIEW

# Allow database admin account to execute commands as 'postgres' user only
db_admin ALL=(postgres) NOPASSWD: /usr/bin/psql, /usr/bin/pg_dump
```

> **Security Rule:** Custom drop-in files in `/etc/sudoers.d/` MUST have permissions `0440` (`chmod 0440 /etc/sudoers.d/filename`) and contain no trailing tilde (`~`) or dot (`.`) characters in their names.

---

### 6.3 Security Hardening `sudoers` Defaults

Add these options to your sudoers file to enforce security best practices:

```conf
# Enforce explicit secure binary execution path (prevents PATH manipulation attacks)
Defaults secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Require terminal context (prevents background unauthorized scripts from calling sudo)
Defaults requiretty

# Centralize dedicated audit log file for all privileged calls
Defaults logfile="/var/log/sudo_audit.log"

# Set password cache timeout window to 15 minutes
Defaults timestamp_timeout=15

# Send email alert to sysadmins upon unauthorized sudo attempt
Defaults mailto="sysadmin-alerts@company.com"
Defaults mail_badpass
```

---

## 7. Troubleshooting & Diagnostic Matrix

| Symptom / Error | Root Cause | Diagnostic Command | Resolution Strategy |
|---|---|---|---|
| `bash: ./script.sh: Permission denied` | Script missing execute bit (`+x`). | `ls -l script.sh` | Grant execute mode: `chmod +x script.sh`. |
| `cd: /srv/data: Permission denied` | User lacks execute bit (`+x`) on directory traversal. | `ls -ld /srv/data` | Add directory execute bit: `chmod +x /srv/data`. |
| User added to group but command fails (e.g., `docker ps`) | Group membership token not refreshed in active shell session. | `id` (shows active tokens) vs `getent group docker` | Reload group session with `exec su - $USER` or `newgrp docker`, or log out and back in. |
| `rm: cannot remove 'config': Operation not permitted` (even for Root) | Immutable attribute (`+i`) active on file or parent directory. | `lsattr config` | Strip immutable attribute: `sudo chattr -i config`. |
| Cannot write file despite `rw-rw-rw-` permissions | Parent directory lacks write (`w`) permission for user. | `ls -ld $(dirname /path/to/file)` | Add write permission to parent directory: `chmod g+w /parent/dir`. |
| `sudo: parse error in /etc/sudoers.d/custom` | Syntax error in custom drop-in file. | `sudo visudo -c` | Run `visudo -f /etc/sudoers.d/custom` to repair syntax errors. |
| `sudo: no tty present and no askpass program specified` | Process invoking `sudo` lacks interactive terminal while `requiretty` is enforced. | Review `/var/log/sudo_audit.log` | Configure `NOPASSWD:` for targeted script command or adjust TTY policy. |
| File ACLs not persisting or failing | Filesystem mounted without ACL support (rare in modern kernels). | `mount \| grep " / "` | Re-mount filesystem with ACL flag or add `acl` to `/etc/fstab`. |

---

## 8. Real-World Production Infrastructure Scenarios

### Scenario A: Multi-Tenant Web Hosting Shared Workspace
**Requirement:** Create a secure directory `/var/www/shared_app` where members of group `webdevs` can create and edit code files. All newly created files must automatically inherit group `webdevs`, and developers must be restricted from deleting or renaming files owned by colleagues.

```bash
# 1. Create team group and append developers
sudo groupadd webdevs
sudo usermod -aG webdevs developer1
sudo usermod -aG webdevs developer2

# 2. Provision shared workspace directory
sudo mkdir -p /var/www/shared_app

# 3. Apply Group Ownership and Special Bits (SGID + Sticky Bit)
# Octal 3770 = SGID (2000) + Sticky Bit (1000) + Owner rwx (700) + Group rwx (070)
sudo chown -R www-data:webdevs /var/www/shared_app
sudo chmod 3770 /var/www/shared_app

# 4. Set POSIX Default ACLs to enforce permission inheritance
sudo setfacl -d -m g:webdevs:rwx /var/www/shared_app
sudo setfacl -d -m u::rwx /var/www/shared_app
sudo setfacl -d -m o::--- /var/www/shared_app

# 5. Verify Permissions
ls -ld /var/www/shared_app
# Expected Output: drwxrws-t+ 2 www-data webdevs 4096 Jul 31 12:00 /var/www/shared_app
```

---

### Scenario B: Hardening a Database Server Backup Service Account
**Requirement:** Configure an isolated automation account `db_backup` capable of generating PostgreSQL dumps and transferring archives to `/var/backups/db/`, without interactive shell access or elevated system privileges.

```bash
# 1. Create non-interactive service user
sudo useradd \
    --system \
    --shell /usr/sbin/nologin \
    --home-dir /var/backups/db \
    --create-home \
    --comment "Database Backup Daemon" \
    db_backup

# 2. Restrict backup directory permissions (Owner access only)
sudo chmod 0700 /var/backups/db
sudo chown db_backup:db_backup /var/backups/db

# 3. Create granular sudoers rule for backup binaries only
cat << 'EOF' | sudo tee /etc/sudoers.d/99-db-backup-policy
db_backup ALL=(root) NOPASSWD: /usr/bin/pg_dumpall, /usr/bin/rsync
EOF

# 4. Enforce strict permissions and validate syntax
sudo chmod 0440 /etc/sudoers.d/99-db-backup-policy
sudo visudo -c
```

---

## 9. Comprehensive Hands-On Lab Exercises

### Lab 1: Comprehensive User Lifecycle & Group Auditing
**Objective:** Provision a specialized finance technical user with password aging policies.

1. Create group `fintech` with GID `3050`.
2. Create user `carol` with UID `3050`, primary group `fintech`, secondary group `sudo`, shell `/bin/bash`.
3. Configure password aging: rotation mandatory every 45 days, warning 7 days prior.
4. Verify user records across `/etc/passwd`, `/etc/shadow`, and `/etc/group`.

```bash
# Solution Commands:
sudo groupadd -g 3050 fintech
sudo useradd -m -u 3050 -g fintech -G sudo -s /bin/bash -c "Carol Danvers - Finance Tech" carol
sudo chage -M 45 -W 7 carol

# Verification:
getent passwd carol
getent group fintech
sudo chage -l carol
```

---

### Lab 2: Special Bits & File Security Setup
**Objective:** Configure a secure team drop directory utilizing SGID and Sticky Bit.

1. Create directory `/tmp/secure_drop`.
2. Set ownership to `root:security`.
3. Allow `security` group members to read, write, and execute files inside.
4. Enforce group inheritance on new files (`SGID`).
5. Prevent users from deleting files created by other users (`Sticky Bit`).

```bash
# Solution Commands:
sudo groupadd security || true
sudo mkdir -p /tmp/secure_drop
sudo chown root:security /tmp/secure_drop
sudo chmod 3770 /tmp/secure_drop

# Verification:
ls -ld /tmp/secure_drop
# Expected: drwxrws-t 2 root security ...
```

---

### Lab 3: Granular POSIX ACL Implementation
**Objective:** Assign custom multi-user access rules to a financial document.

1. Create file `/srv/finance/report_2026.csv`.
2. Set standard ownership: owner `root`, group `finance` (`r--`), others (`---`).
3. Grant user `auditor_bob` read-write access via ACL (`rw-`).
4. Grant group `compliance` read-only access via ACL (`r--`).
5. Inspect and verify ACLs using `getfacl`.

```bash
# Solution Commands:
sudo mkdir -p /srv/finance
sudo touch /srv/finance/report_2026.csv
sudo groupadd finance || true
sudo groupadd compliance || true
sudo chown root:finance /srv/finance/report_2026.csv
sudo chmod 640 /srv/finance/report_2026.csv

# Apply ACLs
sudo setfacl -m u:auditor_bob:rw- /srv/finance/report_2026.csv 2>/dev/null || echo "[!] Ensure user auditor_bob exists"
sudo setfacl -m g:compliance:r-- /srv/finance/report_2026.csv

# Inspect ACL Output
getfacl /srv/finance/report_2026.csv
```

---

### Lab 4: Sudoers Granular Privilege Escalation
**Objective:** Author a validated drop-in sudoers policy for web developers.

1. Create drop-in policy file `/etc/sudoers.d/developer-rules`.
2. Define a user alias `DEV_TEAM` containing `alice` and `bob`.
3. Allow `DEV_TEAM` to execute `systemctl restart apache2` and `systemctl restart mysql` without entering a password.
4. Validate policy syntax using `visudo -c`.

```bash
# Solution Commands:
cat << 'EOF' | sudo tee /etc/sudoers.d/developer-rules
User_Alias DEV_TEAM = alice, bob
Cmnd_Alias WEB_RESTART = /usr/bin/systemctl restart apache2, /usr/bin/systemctl restart mysql
DEV_TEAM ALL=(root) NOPASSWD: WEB_RESTART
EOF

# Set secure file mode and validate
sudo chmod 0440 /etc/sudoers.d/developer-rules
sudo visudo -c
```

---

### Lab 5: System Hardening & Immutable Log File Protection
**Objective:** Safeguard log audit trails from tampering or accidental deletion.

1. Create log file `/var/log/security_audit.log`.
2. Set append-only attribute (`+a`) on the log file using `chattr`.
3. Verify that new logs can be appended (`echo ... >>`).
4. Verify that overwriting or removing the file is blocked even under root context.

```bash
# Solution Commands:
sudo touch /var/log/security_audit.log
sudo chattr +a /var/log/security_audit.log

# Test appending (Succeeds):
echo "$(date +%FT%T) [INFO] Audit process initialized" | sudo tee -a /var/log/security_audit.log

# Test removal attempt (Fails):
sudo rm /var/log/security_audit.log || echo "[+] Success: Removal blocked by append-only kernel attribute."
```

---

## 10. Self-Assessment & Verification Checklist
- [ ] Differentiate between Real UID (RUID), Effective UID (EUID), Saved UID (SUID), and FileSystem UID (FSUID).
- [ ] Explain line-by-line field definitions for `/etc/passwd`, `/etc/shadow`, `/etc/group`, and `/etc/sudoers`.
- [ ] Calculate effective file/directory permissions given a base mode and specific `umask` setting.
- [ ] Demonstrate octal and symbolic usage of SUID (`4000`), SGID (`2000`), and Sticky Bit (`1000`).
- [ ] Implement and verify POSIX ACLs and default directory inheritance using `setfacl` and `getfacl`.
- [ ] Configure low-level filesystem attributes using `chattr` (`+i` immutable, `+a` append-only).
- [ ] Write and validate drop-in `/etc/sudoers.d/` privilege policies using `visudo -c`.
- [ ] Systematically diagnose and resolve permission errors using Linux diagnostic utilities.

---

## 11. Reference Documentation & Learning Links
1. **Linux Man Pages:** `man 5 passwd`, `man 5 shadow`, `man 5 sudoers`, `man 1 chmod`, `man 1 chown`, `man 5 acl`
2. **Sudo Security Project:** [https://www.sudo.ws/docs/](https://www.sudo.ws/docs/)
3. **Red Hat Enterprise Linux Security & Identity Guide:** [https://access.redhat.com/documentation/](https://access.redhat.com/documentation/)
4. **POSIX Access Control Lists on Linux:** [https://man7.org/linux/man-pages/man5/acl.5.html](https://man7.org/linux/man-pages/man5/acl.5.html)
5. **OverTheWire Bandit Wargames:** [https://overthewire.org/wargames/bandit/](https://overthewire.org/wargames/bandit/)

---
→ **Next Module:** [[03 - Package Management]]
