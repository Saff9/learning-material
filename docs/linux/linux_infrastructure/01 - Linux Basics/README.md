# 01 - Linux Basics: System Architecture & Command-Line Mastery

> **Phase:** 1 (Core Linux) · **Time Investment:** ~2–3 weeks · **Difficulty:** ⭐ (Beginner to Intermediate) · **Target Role:** Systems Engineer / DevOps / SRE

---

## 📋 Table of Contents
1. [Architecture Overview & Core Mechanics](#1-architecture-overview--core-mechanics)
2. [Linux File System Hierarchy Standard (FHS 3.0)](#2-linux-file-system-hierarchy-standard-fhs-30)
3. [Command Line Foundations & Advanced Navigation](#3-command-line-foundations--advanced-navigation)
4. [Linux Permissions & Access Control Model (POSIX)](#4-linux-permissions--access-control-model-posix)
5. [Environment Variables, Shell Expansion & Process Execution](#5-environment-variables-shell-expansion--process-execution)
6. [Streams, Redirection & Pipelines (I/O Subsystem)](#6-streams-redirection--pipelines-io-subsystem)
7. [Production Toolkit: Core Utilities & Data Processing](#7-production-toolkit-core-utilities--data-processing)
8. [System Administration Troubleshooting & Diagnostics Matrix](#8-system-administration-troubleshooting--diagnostics-matrix)
9. [Enterprise Hands-On Lab Exercises](#9-enterprise-hands-on-lab-exercises)
10. [Self-Check Verification & Skills Matrix](#10-self-check-verification--skills-matrix)

---

## 1. Architecture Overview & Core Mechanics

Understanding the Linux user-space environment requires distinguishing between the visual display interface, terminal emulators, pseudo-terminal devices, and the command interpreter (shell).

```
+-----------------------------------------------------------------------+
| User Interaction Layer                                               |
|  +-----------------------------------------------------------------+  |
|  | Terminal Emulator (e.g., Alacritty, GNOME Terminal, Windows Terminal)|
|  +-----------------------------------------------------------------+  |
|                                |                                      |
|                                v (IPC / PTY Pair)                     |
|  +-----------------------------------------------------------------+  |
|  | Pseudo-Terminal Master / Slave (/dev/pts/N)                     |
|  +-----------------------------------------------------------------+  |
|                                |                                      |
|                                v (stdin / stdout / stderr)            |
|  +-----------------------------------------------------------------+  |
|  | Command Interpreter / Shell (e.g., /bin/bash, /bin/zsh)          |
|  +-----------------------------------------------------------------+  |
+-----------------------------------------------------------------------+
                                 |
                                 v (System Calls: execve, fork, open)
+-----------------------------------------------------------------------+
| Linux Kernel Space (VFS, Process Scheduler, Memory Management)        |
+-----------------------------------------------------------------------+
```

### 1.1 Key Terminology
*   **Console:** The physical hardware interface (keyboard and monitor) attached directly to the machine.
*   **TTY (Teletypewriter):** A virtual console device provided directly by the Linux kernel (accessed via `Ctrl + Alt + F1` through `F6`, represented as `/dev/tty1` to `/dev/tty6`).
*   **Terminal Emulator:** A graphical program running inside a desktop environment (or SSH session) that mimics a hardware terminal (e.g., `gnome-terminal`, `kitty`, `tmux`).
*   **PTY (Pseudo-Terminal):** A software pair consisting of a master and slave device (`/dev/pts/X`) that allows graphical apps or remote SSH daemons (`sshd`) to communicate with a shell.
*   **Shell:** The command-line interpreter (e.g., Bash, Zsh, Fish) that reads command strings, parses tokens, evaluates expansions, executes programs via system calls (`fork()` / `execve()`), and manages job control.

### 1.2 Shell Execution Pipeline & Expansion Order
When you submit a command string to Bash, it processes the text in a deterministic sequence before invoking the target binary:

1.  **Tokenization & Parsing:** Splits raw input into words, operators, and commands based on metacharacters (` `, `\t`, `;`, `&`, `|`, `<`, `>`).
2.  **Brace Expansion:** Expands expression lists (e.g., `file{1,2}.txt` $\rightarrow$ `file1.txt file2.txt`).
3.  **Tilde Expansion:** Replaces `~` with the user's home directory path (`/home/username`).
4.  **Parameter & Variable Expansion:** Replaces `$VAR` or `${VAR}` with stored values.
5.  **Command Substitution:** Executes `$(command)` or `` `command` `` subshells and replaces the expression with stdout.
6.  **Arithmetic Expansion:** Evaluates `$(( 2 + 2 ))` expressions.
7.  **Word Splitting:** Scans expansion outputs and splits them into distinct arguments based on `$IFS` (Internal Field Separator, default: space, tab, newline).
8.  **Pathname Expansion (Globbing):** Replaces wildcard patterns (`*`, `?`, `[a-z]`) with matching local file paths.
9.  **Quote Removal:** Removes unquoted single (`'`) and double (`"`) quotes, alongside backslashes (`\`).
10. **Command Execution:** Looks up aliases, built-ins, and executable binaries along `$PATH`, executing via `execve()`.

---

## 2. Linux File System Hierarchy Standard (FHS 3.0)

Linux structures its storage layout logically around a single root directory (`/`), regardless of underlying physical disk partitions or network storage mounts.

```text
/ (Root Directory)
├── bin  -> usr/bin        # Essential single-user system binaries (ls, cp, bash)
├── boot                   # Static bootloader configuration, kernel (vmlinuz), initramfs
├── dev                    # Special device nodes representing physical/virtual hardware
├── etc                    # System-wide configuration files and startup scripts
├── home                   # User personal home directories (/home/alice, /home/bob)
├── lib  -> usr/lib        # Shared libraries essential for binaries in /bin and /sbin
├── lib64 -> usr/lib64     # 64-bit architecture shared object files (.so)
├── media                  # Mount point for removable media (USB drives, CD-ROMs)
├── mnt                    # Temporary mount point for filesystems mounted by admins
├── opt                    # Add-on application software packages (third-party vendor apps)
├── proc                   # Virtual pseudo-filesystem exposing kernel state and process info
├── root                   # Home directory for the administrative root user
├── run                    # Volatile runtime data describing system state since boot (tmpfs)
├── sbin -> usr/sbin       # Essential system administration binaries (fdisk, ip, iptables)
├── srv                    # Site-specific data served by the system (e.g., web/ftp data)
├── sys                    # Virtual pseudo-filesystem exposing kernel hardware subsystems
├── tmp                    # Temporary storage cleared on reboot or by automated cron cleanup
├── usr                    # Secondary hierarchy containing read-only user data and utilities
│   ├── bin                # Standard non-essential user binaries
│   ├── include            # C/C++ header files
│   ├── lib                # Architecture-independent library files
│   ├── local              # Local software installed by host admin (bypassing package manager)
│   └── share              # Architecture-independent shared data (documentation, man pages)
└── var                    # Variable data files (logs, state databases, mail spools, locks)
    ├── log                # System logs (syslog, journald, nginx, auth.log)
    ├── lib                # Dynamic state information used by system daemons (docker, mysql)
    └── spool              # Queued tasks awaiting processing (cron jobs, mail queues)
```

### 2.1 Virtual Pseudo-Filesystems Deep Dive
*   **`/proc` (procfs):** Exists only in system memory. Each numerical folder represents an active PID (Process ID).
    *   `/proc/cpuinfo`: Hardware CPU properties and flag capabilities.
    *   `/proc/meminfo`: RAM usage metrics, buffers, and cached memory.
    *   `/proc/sys/net/ipv4/ip_forward`: Dynamic kernel parameter switch for routing packets.
    *   `/proc/[PID]/cmdline`: Complete command string used to launch process `[PID]`.
*   **`/sys` (sysfs):** Exists in memory. Exposes kernel hardware device models, drivers, bus layouts, and tunables.
*   **`/dev` (devtmpfs):** Holds device nodes managed dynamically by `udevd`.
    *   `/dev/null`: The "black hole" device; absorbs and discards all data written to it.
    *   `/dev/zero`: Produces an infinite stream of null bytes (`0x00`).
    *   `/dev/urandom`: Cryptographically secure pseudo-random number generator interface.

---

## 3. Command Line Foundations & Advanced Navigation

### 3.1 Directory Navigation & Directory Stack Management
```bash
# Print current absolute path
pwd

# Navigate to home directory
cd ~

# Navigate to previous directory in shell history
cd -

# Push current directory onto the directory stack and change to target
pushd /var/log/nginx

# View current directory stack
dirs -v

# Pop top directory from stack and cd back to it
popd
```

### 3.2 Deep File & Directory Manipulation Commands

#### `ls` - Directory Listing
```bash
# Detailed listing: long format (-l), human readable (-h), show hidden (-a), sorted by modified time (-t), reverse (-r)
ls -lhatr /var/log

# Print directory inodes alongside file names
ls -i /etc

# Recursively list subdirectories with color coding
ls -R --color=auto /srv
```

#### `cp` - Copying Files and Trees
```bash
# Copy single file preserving mode, ownership, and timestamps (-p)
cp -p /etc/fstab /etc/fstab.bak

# Archive copy: recursive, preserve links, permissions, times, owner (-a)
cp -a /var/www/html /backup/html_$(date +%Y%m%d)

# Sparse copy: efficient copy of large zero-filled files (e.g., VM disk images)
cp --sparse=always /vms/disk.img /vms/disk_copy.img
```

#### `mv` - Moving and Renaming
```bash
# Rename file locally
mv old_name.conf new_name.conf

# Move multiple files into target directory with interactive prompt before overwrite (-i)
mv -i *.log /var/log/archive/
```

#### `rm` - File and Directory Deletion
```bash
# Interactively remove files
rm -i config.tmp

# Forceful recursive deletion (Exercise extreme caution!)
rm -rf /tmp/scratch_dir/

# Securely erase file content by overwriting before unlinking
shred -u -n 3 -z sensitive_data.key
```

#### `mkdir` & `touch` - File and Directory Creation
```bash
# Create nested parent directories automatically (-p) with explicit mode (-m)
mkdir -p -m 0755 /opt/app/{bin,config,logs,data}

# Update access/modification timestamp, or create zero-byte file if non-existent
touch /var/log/app_maintenance.flag
```

### 3.3 Link Mechanics: Hard Links vs. Symbolic Links

```
Hard Link Structure:
File Name "file1" ------> Inode 104523 -------> Disk Data Blocks [ "Hello World" ]
File Name "file2" ------/ (Ref Count: 2)

Symbolic Link Structure:
File Name "symlink" ---> Inode 209811 -------> Disk Data Block [ Path: "/tmp/file1" ]
                                                        |
File Name "file1"  ---> Inode 104523 -------------------/
```

| Property | Hard Link (`ln target link`) | Symbolic Link (`ln -s target link`) |
| :--- | :--- | :--- |
| **Inode Number** | Shares exact same inode as target | Gets a new, unique inode |
| **Cross-Filesystem** | **No**. Cannot span across different mount points | **Yes**. Can point across mount points/filesystems |
| **Target Directory**| **No**. Cannot link to directories (prevents loops) | **Yes**. Can point to directories |
| **Target Deletion** | File data persists until ref count reaches 0 | Link becomes broken (points to missing path) |
| **Size** | Exactly equal to target file size | Size equal to character length of target path |

```bash
# Create a hard link
ln /etc/hosts /tmp/hosts_hardlink

# Create a symbolic (soft) link
ln -s /etc/hosts /tmp/hosts_softlink

# Inspect inodes and link counts (column 2)
ls -li /tmp/hosts_* /etc/hosts
```

---

## 4. Linux Permissions & Access Control Model (POSIX)

Standard Linux permissions govern three entity scopes:
1.  **User (`u`):** The individual account owning the file.
2.  **Group (`g`):** The group assigned to the file.
3.  **Others (`o`):** Every other system user account.

```text
  File Type
  |   User (Owner)   Group Permissions   Others Permissions
  |   │   │   │        │   │   │           │   │   │
  v   v   v   v        v   v   v           v   v   v
  -   r   w   x        r   -   x           r   -   -
      │   │   │        │   │   │           │   │   │
      4 + 2 + 1        4 + 0 + 1           4 + 0 + 0
        = 7              = 5                 = 4
```

### 4.1 Permission Bits Breakdown

| Bit Symbol | Numeric Value | Meaning on File | Meaning on Directory |
| :---: | :---: | :--- | :--- |
| **`r`** | **`4`** | Read file content | List directory contents (`ls`) |
| **`w`** | **`2`** | Modify/overwrite file content | Create, rename, or delete files inside directory |
| **`x`** | **`1`** | Execute file as binary/script | Enter directory (`cd`) and access metadata |

### 4.2 Special Permission Bits (SUID, SGID, Sticky Bit)

```bash
# Octal Representation: [Special Bit][User][Group][Others]
# SUID = 4000, SGID = 2000, Sticky Bit = 1000
```

1.  **SUID (Set User ID - `4000` / `chmod u+s`):**
    *   **Behavior:** When executed, the binary runs with the privileges of the file's *owner*, not the executing user.
    *   **Example:** `/usr/bin/passwd` allows regular users to modify `/etc/shadow` owned by root.
    *   **Security Hazard:** Vulnerable SUID binaries allow immediate privilege escalation.
2.  **SGID (Set Group ID - `2000` / `chmod g+s`):**
    *   **Behavior on Files:** Binary executes with privileges of file's *group*.
    *   **Behavior on Directories:** Any newly created file inside the directory automatically inherits the directory's group ownership instead of the creator's primary group.
    *   **Use Case:** Shared team directories for collaborative editing.
3.  **Sticky Bit (`1000` / `chmod +t`):**
    *   **Behavior on Directories:** Only the file owner, directory owner, or root can delete or rename files inside the directory.
    *   **Use Case:** Public shared directories like `/tmp` or `/var/tmp` (`drwxrwxrwt`).

```bash
# Set SGID and Sticky Bit on a shared engineering directory
chmod 3770 /srv/shared/engineering
# Symbolic equivalent:
chmod u=rwx,g=rwxs,o=t /srv/shared/engineering

# Audit system for all SUID executable binaries owned by root
find / -maxdepth 3 -perm -4000 -type f -uid 0 -ls 2>/dev/null
```

### 4.3 `umask` Math & Default Permission Calculation

The system calculates default creation permissions by performing a bitwise AND with the bitwise NOT of the `umask` value:
$$\text{Effective Mode} = \text{Base Mode} \ \& \ (\sim \text{umask})$$

*   **Base Mode for Files:** `0666` (`rw-rw-rw-`) — Files are never created executable by default.
*   **Base Mode for Directories:** `0777` (`rwxrwxrwx`).

#### Calculation Example for `umask 0027` (Production Hardened Environment):
*   **Default File Permission:**
    $$0666 \ (\text{rw-rw-rw-}) - 0027 \ (\text{---r-xr-w}) \longrightarrow 0640 \ (\text{rw-r-----})$$
*   **Default Directory Permission:**
    $$0777 \ (\text{rwxrwxrwx}) - 0027 \ (\text{---r-xr-w}) \longrightarrow 0750 \ (\text{rwxr-x---})$$

```bash
# Check current umask in symbolic and octal formats
umask
umask -S

# Permanently enforce restrictive umask in shell profile
echo "umask 0027" >> ~/.bashrc
```

---

## 5. Environment Variables, Shell Expansion & Process Execution

### 5.1 Local vs. Exported Environment Variables

```bash
# Local shell variable (visible ONLY in current shell process, not inherited by subshells)
APP_ENV="staging"

# Export variable into process environment (inherited by child processes)
export APP_ENV="production"

# Display all exported environment variables
env

# View specific variable value
echo "${APP_ENV}"
```

### 5.2 Vital Linux System Variables

| Variable | Description |
| :--- | :--- |
| **`$PATH`** | Colon-separated list of directories searched when running un-pathed commands. |
| **`$HOME`** | Absolute path to current user's home directory. |
| **`$USER`** | Name of logged-in user. |
| **`$SHELL`** | Path to user's default login shell (e.g., `/bin/bash`). |
| **`$LANG` / `$LC_ALL`** | System locale, character encoding, and language configuration. |
| **`$PS1`** | Primary prompt string structure definition. |
| **`$LD_LIBRARY_PATH`** | Directories to search for dynamic C/C++ shared object libraries (`.so`). |

### 5.3 Shell Startup & Profile Execution Order

```
Interactive Login Shell (SSH, su - user, Console Login)
├── 1. Reads /etc/profile
│      ├── Reads /etc/bash.bashrc (or /etc/bashrc)
│      └── Reads files in /etc/profile.d/*.sh
└── 2. Reads first existing user file:
       ├── ~/.bash_profile
       ├── ~/.bash_login
       └── ~/.profile

Interactive Non-Login Shell (Opening subshell, terminal window, tmux pane)
├── 1. Reads /etc/bash.bashrc
└── 2. Reads ~/.bashrc

Non-Interactive Shell (Running shell script file.sh)
└── Reads file pointed to by $BASH_ENV (if configured)
```

### 5.4 Production Shebang & Bash Execution Strict Mode

Always structure executable production scripts with a portable shebang and safety flags:

```bash
#!/usr/bin/env bash
# ==============================================================================
# Script Name:    backup_pipeline.sh
# Description:    Automated DB & filesystem sync script with error checks
# ==============================================================================

# Strict Execution Mode (Fail-Fast Architecture)
set -euo pipefail

# -e  : Exit immediately if any command returns a non-zero exit status.
# -u  : Treat unset variables and parameters as an error when expanding.
# -o pipefail : The return status of a pipeline is the status of the last command
#               to exit with a non-zero status (prevents silent failures in pipes).

export TRACE_ID=$(date +%s)
echo "Executing pipeline with Trace ID: ${TRACE_ID}"
```

---

## 6. Streams, Redirection & Pipelines (I/O Subsystem)

In Linux, everything is handled via file descriptors (FDs). Every process opens three standard I/O streams by default:

```
                  +-----------------------+
stdin  (FD 0) --> |                       | --> stdout (FD 1)
                  |     Linux Process     |
                  |                       | --> stderr (FD 2)
                  +-----------------------+
```

| Name | File Descriptor | Default Keyboard / Screen |
| :--- | :---: | :--- |
| **Standard Input (`stdin`)** | `0` | Keyboard / Terminal Stream |
| **Standard Output (`stdout`)** | `1` | Screen / Terminal Display |
| **Standard Error (`stderr`)** | `2` | Screen / Terminal Display |

### 6.1 Redirection Operators Quick Reference

```bash
# Redirect stdout to file (overwrite)
echo "Server Online" > /tmp/status.txt

# Redirect stdout to file (append)
echo "$(date): Healthcheck OK" >> /tmp/status.log

# Redirect stderr only to error log file
ls /root 2> /tmp/errors.log

# Redirect stdout and stderr to separate files
systemctl status nginx > /tmp/stdout.log 2> /tmp/stderr.log

# Combine stdout and stderr into single file (POSIX recommended)
/opt/app/run.sh > /tmp/combined.log 2>&1
# Bash shortcut:
/opt/app/run.sh &> /tmp/combined.log

# Discard all error output entirely
find /var/log -name "*.log" 2>/dev/null

# Here-Document (multiline file generation)
cat << 'EOF' > /etc/nginx/conf.d/app.conf
server {
    listen 80;
    server_name localhost;
    root /var/www/html;
}
EOF

# Here-String (pass string variable directly into stdin)
grep "ERROR" <<< "${LOG_BUFFER}"
```

### 6.2 Pipelines, Process Substitution & Tee

```bash
# Pipeline: Connect stdout of command 1 directly to stdin of command 2
journalctl -u nginx --since "1 hour ago" | grep "HTTP/1.1\" 500" | wc -l

# Process Substitution: Feed output of commands as temporary file descriptors
diff -u <(sort /tmp/list_A.txt) <(sort /tmp/list_B.txt)

# Tee: Split output stream — write to file AND view on screen simultaneously
echo "Starting deployment step 1" | tee -a /var/log/deploy.log
```

---

## 7. Production Toolkit: Core Utilities & Data Processing

### 7.1 Text Searching: `grep` & `ripgrep` (`rg`)
```bash
# Case-insensitive (-i), recursive (-r), line numbers (-n), context 2 lines before/after (-C 2)
grep -irnC 2 "FATAL" /var/log/syslog

# Count matching lines (-c) excluding pattern (-v)
grep -v "^#" /etc/hosts | grep -c "127.0.0.1"

# Extended regular expressions (-E) matching IP addresses
grep -E "([0-9]{1,3}\.){3}[0-9]{1,3}" /var/log/auth.log

# Modern fast search with ripgrep (rg) searching python files for function definitions
rg -t py "def process_data" /srv/app/
```

### 7.2 Stream Editing: `sed`
```bash
# Replace first occurrence of 'http' with 'https' per line and print
sed 's/http/https/' /tmp/urls.txt

# Global search and replace ('g') inline in-place modification (-i) with backup extension
sed -i.bak 's/port = 8080/port = 9000/g' /etc/app/config.ini

# Delete blank lines and lines starting with '#'
sed -i '/^$/d; /^\s*#/d' /etc/nginx/nginx.conf

# Print specific line range (lines 15 to 30)
sed -n '15,30p' /var/log/syslog
```

### 7.3 Structured Field Processing: `awk`
```bash
# Print line number (NR) and specific fields ($1 IP, $7 Request path, $9 Status code) from web access log
awk '{print NR, $1, $7, $9}' /var/log/nginx/access.log

# Custom field separator (-F): Parse /etc/passwd for users with UID >= 1000
awk -F: '$3 >= 1000 {print $1, $3, $6}' /etc/passwd

# Conditional summation: Calculate total bytes transferred (field $10) for HTTP 200 responses
awk '$9 == 200 {sum += $10} END {printf "Total Data Transferred: %.2f MB\n", sum/(1024*1024)}' /var/log/nginx/access.log
```

### 7.4 Archiving & Data Transfer (`tar`, `rsync`, `ssh`, `curl`)

```bash
# TAR Archive Creation (c: create, z: gzip, v: verbose, f: file, p: preserve permissions)
tar -czvpf /backups/etc_backup_$(date +%F).tar.gz /etc

# TAR Extraction (x: extract, z: gunzip, v: verbose, f: file, -C: destination directory)
tar -xzvf /backups/etc_backup.tar.gz -C /tmp/restore/

# Create tar archive using xz compression (higher ratio)
tar -cJvf /backups/logs.tar.xz /var/log/nginx

# Production RSYNC Sync: archive (-a), verbose (-v), compress (-z), progress (-P), delete stale (-delete) over SSH
rsync -avzP --delete -e "ssh -i /root/.ssh/deploy_key" /var/www/html/ deploy@remote-host:/var/www/html/

# Fast HTTP API Request with curl: Silent (-s), fail on HTTP error (-f), show headers (-i), timeout 5s
curl -sSfi --max-time 5 https://api.internal.net/healthcheck
```

---

## 8. System Administration Troubleshooting & Diagnostics Matrix

When diagnosing host issues, systematically apply diagnostic commands based on observed symptoms:

| Category / Symptom | Root Cause Candidates | Diagnostic Commands | Resolution Strategy |
| :--- | :--- | :--- | :--- |
| **Disk Space Exhaustion (`No space left on device`)** | Large log files, abandoned core dumps, orphaned unlinked open files holding space. | `df -h`<br>`du -sh /* 2>/dev/null \| sort -hr \| head -10`<br>`lsof +L1` | Rotate/truncate logs (`> file.log`), clean package caches (`apt clean` / `dnf clean all`), kill processes holding deleted handles. |
| **Inode Exhaustion (`No space left on device` but `df -h` shows disk space available)** | Millions of tiny zero-byte files (e.g., mail spools, session files). | `df -i`<br>`find /var/spool -type f \| wc -l` | Locate directory with excessive files using `find` and purge via `xargs rm`. |
| **Command Not Found (`bash: foo: command not found`)** | Executable missing from system, or binary directory not present in `$PATH`. | `echo $PATH`<br>`which foo`<br>`find / -name foo -type f 2>/dev/null` | Update `$PATH` variable in `~/.bashrc` or specify explicit absolute path `/opt/bin/foo`. |
| **Permission Denied (`EACCES`)** | User lacks `r`/`w`/`x` bits, directory lacks execute bit, or active SELinux/AppArmor policy blocks access. | `ls -la /path/to/target`<br>`id`<br>`getenforce`<br>`dmesg \| grep -i audit` | Adjust ownership (`chown`), correct permission bits (`chmod`), or tune SELinux boolean contexts (`chcon` / `semanage`). |
| **Shared Library Missing (`error while loading shared libraries`)** | Dynamic linker cannot locate required `.so` library files in runtime search path. | `ldd /usr/bin/program_name`<br>`ldconfig -p \| grep libname` | Add library path to `/etc/ld.so.conf.d/custom.conf` and run `sudo ldconfig`. |
| **High I/O Wait Bottleneck (`%wa` in top)** | Disk subsystem saturated by excessive write IOPS or failing hardware. | `top`<br>`iostat -xz 1 5`<br>`iotop -oP` | Identify runaway disk write process using `iotop`, tune process `nice`/`ionice` priorities, or migrate storage to faster NVMe/SAN. |
| **Broken Soft Link (`No such file or directory`)** | Target destination file was renamed, relocated, or deleted. | `ls -l /path/to/symlink`<br>`test -e /path/to/symlink \|\| echo "Link Broken"` | Update link to target correct path using `ln -sfn /new/target /path/to/symlink`. |

---

## 9. Enterprise Hands-On Lab Exercises

### Lab 1: Infrastructure Log Sanitization & Forensic Extraction Pipeline
**Objective:** Parse a multi-gigabyte Nginx access log, extract client IP addresses causing HTTP 5xx errors, sort by frequency, and store the output in a compressed forensic tarball.

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Setup isolated working directory
WORK_DIR="/tmp/lab1_forensics"
mkdir -p "${WORK_DIR}"
cd "${WORK_DIR}"

# 2. Simulate raw Nginx log data
cat << 'EOF' > access.log
192.168.1.50 - - [31/Jul/2026:10:00:01 +0000] "GET /api/v1/users HTTP/1.1" 200 1420
10.0.4.12 - - [31/Jul/2026:10:00:02 +0000] "POST /api/v1/checkout HTTP/1.1" 500 512
172.16.0.8 - - [31/Jul/2026:10:00:03 +0000] "GET /images/logo.png HTTP/1.1" 200 8920
10.0.4.12 - - [31/Jul/2026:10:00:04 +0000] "GET /api/v1/cart HTTP/1.1" 502 204
192.168.1.50 - - [31/Jul/2026:10:00:05 +0000] "POST /api/v1/checkout HTTP/1.1" 500 512
10.0.4.12 - - [31/Jul/2026:10:00:06 +0000] "DELETE /api/v1/orders HTTP/1.1" 503 128
EOF

# 3. Process logs: Filter 5xx errors -> Extract IP ($1) -> Sort -> Count unique -> Sort descending
echo "=== Top Offensive IP Addresses (5xx Errors) ==="
awk '$9 ~ /^5/ {print $1}' access.log | sort | uniq -c | sort -nr > failed_ips.txt
cat failed_ips.txt

# 4. Generate timestamped, compressed report
REPORT_NAME="incident_report_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czvf "${REPORT_NAME}" access.log failed_ips.txt

echo "Lab 1 Complete. Output generated at: ${WORK_DIR}/${REPORT_NAME}"
```

---

### Lab 2: Multi-Tenant Secure Directory Hierarchy (SGID, Sticky Bit & umask)
**Objective:** Construct a collaborative team folder `/srv/projects/finance` where team members can create and share files seamlessly without allowing non-owners to delete files or override group permissions.

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Create directory structure
DIRECTORY="/srv/projects/finance"
sudo mkdir -p "${DIRECTORY}"

# 2. Create simulated system group and users (if non-existent)
sudo groupadd -f finance_team

# 3. Assign ownership (root owner, finance_team group)
sudo chown root:finance_team "${DIRECTORY}"

# 4. Configure permissions:
# - User (root): rwx (7)
# - Group (finance_team): rwx + SGID (2770) -> New files inherit finance_team group
# - Others: no access (0) + Sticky bit (+t / 1) -> Users can only delete their own files
sudo chmod 3770 "${DIRECTORY}"

# 5. Verify configured permissions
ls -ld "${DIRECTORY}"
# Expected Output: drwxrws--T 2 root finance_team ... /srv/projects/finance
```

---

### Lab 3: Production-Grade Automated Backup & Synchronization Script
**Objective:** Write a robust shell script adhering to strict error checking, atomic execution, logging, and automated cleanup of backups older than 7 days.

```bash
#!/usr/bin/env bash
# ==============================================================================
# Enterprise Directory Synchronization & Backup Engine
# ==============================================================================
set -euo pipefail
IFS=$'\n\t'

# Environment Configuration
readonly SOURCE_DIR="/etc"
readonly BACKUP_DIR="/var/backups/system_configs"
readonly LOG_FILE="/var/log/sys_backup.log"
readonly TIMESTAMP=$(date +%Y%m%d_%H%M%S)
readonly TARGET_ARCHIVE="${BACKUP_DIR}/config_backup_${TIMESTAMP}.tar.gz"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [${1}] ${2}" | tee -a "${LOG_FILE}"
}

# Main Execution Flow
log "INFO" "Starting backup process..."

# Ensure target backup directory exists
mkdir -p "${BACKUP_DIR}"

# Create compressed tarball
if tar -czf "${TARGET_ARCHIVE}" "${SOURCE_DIR}" 2>>"${LOG_FILE}"; then
    log "INFO" "Successfully created archive: ${TARGET_ARCHIVE}"
else
    log "ERROR" "Failed to create archive!"
    exit 1
fi

# Set secure permissions on output archive (rw-r-----)
chmod 0640 "${TARGET_ARCHIVE}"

# Retention Cleanup: Purge backup archives older than 7 days
log "INFO" "Purging backups older than 7 days..."
find "${BACKUP_DIR}" -type f -name "config_backup_*.tar.gz" -mtime +7 -exec rm -f {} \; -print | while read -r deleted_file; do
    log "INFO" "Deleted old backup: ${deleted_file}"
done

log "INFO" "Backup pipeline execution completed successfully."
```

---

### Lab 4: Broken Environment & PATH Recovery Scenario
**Objective:** Simulate an administration failure where `$PATH` is corrupted or cleared, preventing standard command invocation, and recover system state safely using shell built-ins and absolute binary paths.

```bash
# 1. Break PATH in current subshell session
export PATH=""

# Attempting standard commands now fails:
ls
# Result: bash: ls: No such file or directory

# 2. Diagnose current binary locations using built-in commands
echo "Current PATH is empty: '$PATH'"

# 3. Execute recovery using absolute utility paths
/bin/ls -l /usr/bin/ls
/bin/echo "Restoring default Linux standard PATH environment..."

# 4. Restore standard PATH variable
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# 5. Verify recovery
which ls
ls -la
```

---

## 10. Self-Check Verification & Skills Matrix

Assess your operational command-line proficiency against these core competencies:

- [ ] **Architecture Mechanics:** Can explain the exact difference between a TTY (`/dev/tty1`), PTY (`/dev/pts/0`), Terminal Emulator, and Shell Interpreter.
- [ ] **FHS Compliance:** Can identify the distinct roles of `/etc`, `/var`, `/usr`, `/proc`, `/sys`, and `/opt` without referencing documentation.
- [ ] **Navigation & Inspection:** Mastered stack navigation using `pushd`/`popd`, and inspecting detailed file metadata via `stat` and `ls -li`.
- [ ] **Inodes & Links:** Can explain why hard links cannot span filesystems or target directories, whereas soft links can.
- [ ] **Permissions & Special Bits:** Can calculate octal modes for SUID (`4000`), SGID (`2000`), and Sticky Bit (`1000`), and calculate default file creation permissions using `umask`.
- [ ] **Environment & Profile:** Understands the startup sequence of interactive login vs non-login shells and writes scripts using strict mode (`set -euo pipefail`).
- [ ] **I/O Redirection & Streams:** Capable of manipulating FDs (`0`, `1`, `2`), using process substitution `<()`, and utilizing `tee` in pipelines.
- [ ] **Text Processing Heavyweights:** Fluent in using `grep`/`ripgrep`, `sed` inline search-and-replace, and multi-field conditional formatting in `awk`.
- [ ] **Archiving & Remote Sync:** Able to create/extract `tar.gz` and `tar.xz` archives, sync directories via `rsync` over SSH, and send API requests with `curl`.
- [ ] **Troubleshooting:** Capable of diagnosing disk space vs inode exhaustion, locating unlinked open files with `lsof`, and recovering from corrupted environment paths.

---

## 🔗 Link to Next Module
Proceed to the next module to master Linux user accounts, group management, shadow password databases, and Advanced Access Control Lists (FACLs):
→ **[02 - Users & Permissions](../02 - Users & Permissions/README.md)**
