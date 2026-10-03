# 03 - Linux Package Management Architecture & Administration

> **Phase:** 1 (Core Linux) · **Time:** ~3 weeks · **Difficulty:** ⭐⭐

---

## Executive Overview & Deep Dive

**Package management** is the foundational subsystem through which Linux distributions deploy, configure, update, maintain, and audit software components. Rather than relying on monolithic installers, Linux utilizes structured software archives (packages) containing compiled binaries, libraries, configuration templates, documentation, dependency manifests, and pre/post-installation automation scriptlets.

At an enterprise infrastructure level, package management ensures:
1. **Deterministic Environment Provisioning:** Automated infrastructure deployment via Ansible, Puppet, or Cloud-Init relies on atomic package state management.
2. **Security & Vulnerability Remediation:** Rapid patch management against CVEs via cryptographically verified, signed distribution mirrors.
3. **Dependency Resolution Graphs:** Automatic traversal of complex Directed Acyclic Graphs (DAGs) representing software interdependencies and conflicts.
4. **System State Integrity:** Database-backed tracking of every single file owned by any package, preventing file collisions and enabling total uninstallations (`purge`).

---

## High-Level Architecture & Taxonomy

```
+-------------------------------------------------------------------------------+
|                        Universal Application Sandboxes                        |
|                  (Snap, Flatpak, AppImage, OCI Containers)                    |
+-------------------------------------------------------------------------------+
                                       |
+--------------------------------------v----------------------------------------+
|                    High-Level Package Managers & Solvers                      |
|            (APT / apt-get / apt-cache | DNF / YUM | ZYpp | Pacman)             |
|   - Fetches remote repo indexes & GPG signatures                             |
|   - Constructs & resolves dependency graphs (SAT solver / libsolv)           |
|   - Orchestrates multi-package transaction ordering                          |
+-------------------------------------------------------------------------------+
                                       |
+--------------------------------------v----------------------------------------+
|                     Low-Level Package Package Engines                         |
|                             (DPKG | RPM Engine)                               |
|   - Unpacks tarballs/archives (.deb / .rpm)                                   |
|   - Executes preinst/postinst/pre/post scriptlets                            |
|   - Writes raw file metadata to local databases (/var/lib/dpkg, /var/lib/rpm)|
+-------------------------------------------------------------------------------+
```

---

## Section 1: Low-Level Package Operations (`dpkg` & `rpm`)

Low-level package managers manipulate local package files (`.deb` and `.rpm`) directly without remote repository access or automatic dependency resolution.

### 1.1 Debian Lower Level Engine: `dpkg`

The `dpkg` command is the foundational engine for Debian, Ubuntu, Linux Mint, and Pop!_OS.

#### Core `dpkg` Administrative Commands

```bash
# 1. Install a local .deb package directly (does NOT download dependencies)
sudo dpkg -i package_name.deb

# 2. If dpkg fails due to missing dependencies, invoke APT to resolve and fix broken state
sudo apt-get install -f -y

# 3. List all installed packages matching a pattern with status flags
dpkg -l | grep -i "nginx"

# 4. Inspect detailed status and metadata of a specific installed package
dpkg -s nginx

# 5. List all files installed onto the filesystem by a package
dpkg -L nginx

# 6. Reverse lookup: Find which installed package owns a specific file on disk
dpkg -S /etc/nginx/nginx.conf

# 7. Unpack package contents without executing installation scriptlets or configuring
dpkg --unpack package_name.deb

# 8. Reconfigure an already installed package (triggers debconf prompts)
sudo dpkg-reconfigure tzdata

# 9. Purge a package completely (removes binaries AND system configuration files)
sudo dpkg -P package_name

# 10. Audit integrity of installed package files against stored MD5 checksums
dpkg -V nginx
```

#### Inspecting `.deb` Archive Internals

A `.deb` package is an `ar` archive containing three core files:
- `debian-binary`: Text file containing `.deb` format version (usually `2.0`).
- `control.tar.xz` (or `.gz`): Contains package control metadata, dependency definitions, MD5 sums, and debconf maintainer scripts (`preinst`, `postinst`, `prerm`, `postrm`).
- `data.tar.xz` (or `.gz`/`.zst`): The actual filesystem payload extractable to `/`.

```bash
# Create a temporary directory to inspect package payload
mkdir -p /tmp/inspect_pkg && cd /tmp/inspect_pkg

# Extract the control files (scripts, dependencies, metadata)
dpkg-deb -e /path/to/custom-app_1.0.0_amd64.deb ./control_files

# View package control file detailing metadata and architecture dependencies
cat ./control_files/control

# View pre-installation maintainer scriptlet
cat ./control_files/preinst

# Extract the raw filesystem file structure without installing
dpkg-deb -x /path/to/custom-app_1.0.0_amd64.deb ./filesystem_payload

# Tree view of installed payload location targets
tree ./filesystem_payload
```

---

### 1.2 Red Hat Lower Level Engine: `rpm`

The `rpm` (Red Hat Package Manager) tool operates on `.rpm` binaries across RHEL, CentOS Stream, Rocky Linux, AlmaLinux, and Fedora.

#### Core `rpm` Administrative Commands

```bash
# 1. Install a package with verbose progress indicators and hash mark progress bar
sudo rpm -ivh package_name.rpm

# 2. Upgrade a package (installs if not present, upgrades if older version exists)
sudo rpm -Uvh package_name.rpm

# 3. Fresh installation upgrade (only upgrades if an older version is ALREADY installed)
sudo rpm -Fvh package_name.rpm

# 4. Remove an installed RPM package without removing configs
sudo rpm -e package_name

# 5. Query all installed packages matching a pattern
rpm -qa | grep -i "httpd"

# 6. Detailed package information (version, vendor, build date, license, summary)
rpm -qi httpd

# 7. List files provided by an installed RPM package
rpm -ql httpd

# 8. Identify which RPM package owns a specific path
rpm -qf /etc/httpd/conf/httpd.conf

# 9. Inspect required dependencies of an uninstalled RPM file
rpm -qpR package_name.rpm

# 10. Inspect embedded installation scriptlets (prein, postin, preun, postun) of an RPM package file
rpm -qp --scripts package_name.rpm

# 11. Verify integrity of all installed system packages against RPM DB metadata
rpm -Va
```

#### RPM Verification Flag Reference

When executing `rpm -V`, output flags indicate discrepancies between current file attributes on disk and the original RPM database entry:

| Flag Symbol | Attribute Verified | Meaning |
| :--- | :--- | :--- |
| `S` | File Size | File size differs from original build |
| `M` | Mode / Permissions | File permissions or type changed |
| `5` | MD5 / SHA256 Checksum | File content has been modified |
| `D` | Device Major/Minor | Device node mismatch |
| `L` | readLink Path | Symlink path changed |
| `U` | User Ownership | File owner modified |
| `G` | Group Ownership | File group modified |
| `T` | Mtime (Modification Time)| File modification timestamp altered |
| `P` | Capabilities | Extended file capabilities changed |

---

## Section 2: Debian / Ubuntu Ecosystem (`apt`, `apt-get`, `apt-cache`)

APT (Advanced Package Tool) acts as the high-level orchestration interface over `dpkg`. It automatically fetches remote repository indices, resolves complex dependency chains, performs transactional batch installs, and verifies cryptographic signatures.

### 2.1 Interface Comparison: `apt` vs `apt-get` vs `apt-cache`

- `apt-get` & `apt-cache`: Legacy, stable, script-friendly low-level CLI utilities. Recommended for non-interactive Bash/CI scripts because CLI output flags remain strictly backwards compatible.
- `apt`: High-level, user-friendly wrapper introduced in APT 1.0. Features colorized output, interactive progress bars, inline search summaries, and consolidated management commands.

```bash
# Equivalent commands table script comparison
# Search:
apt search nginx         # High-level CLI output
apt-cache search nginx   # Scriptable, raw output

# Show metadata:
apt show nginx           # Consolidated summary
apt-cache show nginx     # Full raw control stanza

# Update & Install:
sudo apt update && sudo apt install -y nginx
sudo apt-get update && sudo apt-get install -y nginx
```

---

### 2.2 Modern Repository Management & GPG Security Model

> **CRITICAL SECURITY UPDATE:** The legacy command `apt-key add` and `/etc/apt/trusted.gpg` are **deprecated** due to cross-repository security vulnerabilities (a key added globally can sign packages for *any* repository).
> 
> Modern Linux security standards require dedicated, armored/dearmored keyring files placed in `/etc/apt/keyrings/` or `/usr/share/keyrings/`, explicitly linked to specific source definitions via `Signed-By`.

#### Modern GPG Keyring Ingestion Pipeline

```bash
# 1. Ensure security directory exists with restrictive permissions
sudo mkdir -p /etc/apt/keyrings
sudo chmod 0755 /etc/apt/keyrings

# 2. Download remote GPG ASCII-armored key, dearmor it to binary, and save to dedicated keyring file
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 3. Ensure public readability of the keyring file
sudo chmod 0644 /etc/apt/keyrings/docker.gpg
```

#### Repository Configuration Formats

##### A. Legacy Single-Line Format (`/etc/apt/sources.list.d/docker.list`)

```apt
# Format: deb [options] uri distribution components
deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu jammy stable
```

##### B. Modern DEB822 Format (`/etc/apt/sources.list.d/docker.sources`)

DEB822 is the standard multi-line configuration structure for modern Debian and Ubuntu distributions:

```ini
X-Repolib-Name: Docker Official Repository
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: jammy
Components: stable
Architectures: amd64 arm64
Signed-By: /etc/apt/keyrings/docker.gpg
```

---

### 2.3 Production Configuration & Automation (`apt.conf`)

APT configuration files reside in `/etc/apt/apt.conf` and `/etc/apt/apt.conf.d/`. Files are evaluated in numerical string order.

#### Example 1: Enterprise HTTP Proxy Configuration (`/etc/apt/apt.conf.d/01proxy`)

```apt
// Proxy configuration for corporate network traversal
Acquire::http::Proxy "http://proxy.enterprise.internal:8080/";
Acquire::https::Proxy "http://proxy.enterprise.internal:8080/";
Acquire::http::Proxy::download.docker.com "DIRECT"; // Bypass proxy for specific domain
```

#### Example 2: Disabling Unnecessary Package Recommendations (`/etc/apt/apt.conf.d/99norecommends`)

To minimize container image sizes and footprint on bare-metal nodes:

```apt
// Disable automatic installation of recommended and suggested packages
APT::Install-Recommends "false";
APT::Install-Suggests "false";
```

#### Example 3: Unattended Automatic Security Upgrades (`/etc/apt/apt.conf.d/50unattended-upgrades`)

```apt
// Configure automatic patch management for security repositories only
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-security";
};

// Package blacklists: Never auto-upgrade database or kernel core packages automatically
Unattended-Upgrade::Package-Blacklist {
    "postgresql";
    "mysql-server";
    "linux-image-generic";
};

// Automatic cleanup and notification setup
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Mail "sysadmin@enterprise.internal";
```

---

### 2.4 APT Pinning & Priority Management (`/etc/apt/preferences.d/`)

APT Pinning allows system administrators to explicitly control which repository or package version is selected, overriding default priority logic.

#### Pin Priority Value Scale

| Priority Range | Behavior / Policy |
| :--- | :--- |
| `P < 0` | The version is never installed. |
| `0 <= P < 100` | Installed only if no version of the package is currently installed. |
| `100 <= P < 500` | Installed only if there is no version available in another repo or installed. |
| `P = 500` | Default priority for installed and available releases. |
| `500 < P < 990` | Preferred over default target release unless installed version is newer. |
| `990 <= P < 1000` | Preferred even if not matching default release (e.g. backports). |
| `P >= 1000` | Forced downgrade priority. Installed even if it downgrades software. |

#### Real-World Pinning Scenario 1: Pinning Nginx to Official Stable Repo

Create file `/etc/apt/preferences.d/nginx-pin`:

```ini
# Force Nginx to be installed strictly from the official nginx.org repository
Package: nginx*
Pin: origin nginx.org
Pin-Priority: 990

# Prevent default distribution repository from overriding official nginx binaries
Package: nginx*
Pin: release o=Ubuntu
Pin-Priority: 50
```

#### Real-World Pinning Scenario 2: Holding a Specific Package Version

```bash
# Mark a package as held to prevent automatic updates during 'apt upgrade'
sudo apt-mark hold kubelet kubeadm kubectl

# Verify current held packages
apt-mark showhold

# Unhold to resume normal upgrade paths
sudo apt-mark unhold kubelet kubeadm kubectl
```

---

## Section 3: Red Hat / RHEL Ecosystem (`dnf`, `yum`, `rpm-ostree`)

DNF (Dandified YUM) is the next-generation package manager for RHEL 8/9, Fedora, Rocky Linux, and AlmaLinux. Powered by `libsolv` (a SAT-based dependency solver engine), DNF provides optimized memory usage and transactional operation tracking.

### 3.1 DNF Configuration Architecture (`/etc/dnf/dnf.conf`)

Main DNF daemon settings are configured in `/etc/dnf/dnf.conf`:

```ini
[main]
# Directory paths and logging
gpgcheck=1
installonly_limit=3
clean_requirements_on_remove=True
best=True
skip_if_unavailable=False

# Performance tuning for fast parallel package downloads
max_parallel_downloads=10
fastestmirror=True

# Enterprise Proxy configuration
# proxy=http://proxy.enterprise.internal:8080
```

### 3.2 Repository Definition Syntax (`/etc/yum.repos.d/*.repo`)

Repository files control remote package locations.

#### Example: Custom Enterprise Repository Configuration (`/etc/yum.repos.d/enterprise-internal.repo`)

```ini
[enterprise-apps-stable]
name=Enterprise Core Internal Application Repository - $basearch
baseurl=http://repo.internal.enterprise.com/rhel/$releasever/apps/$basearch/
enabled=1
gpgcheck=1
gpgkey=http://repo.internal.enterprise.com/keys/RPM-GPG-KEY-enterprise
priority=10
module_hotfixes=true
metadata_expire=6h
```

---

### 3.3 DNF Modules, AppStreams, & Profiles

RHEL 8/9 introduces **Application Streams (AppStreams)**, enabling multiple concurrent versions of application stacks (e.g. Node.js 18 vs Node.js 20, PostgreSQL 14 vs PostgreSQL 15) to coexist in the distribution ecosystem.

```bash
# 1. List available module streams for a specific software component
dnf module list postgresql

# Expected Output snippet:
# Name        Stream      Profiles                  Summary
# postgresql  15          client, server [d]        PostgreSQL server and client module
# postgresql  16          client, server            PostgreSQL server and client module

# 2. Inspect detailed information about a specific stream
dnf module info postgresql:16

# 3. Enable a specific version stream (e.g., PostgreSQL 16)
sudo dnf module enable postgresql:16 -y

# 4. Install a specific stream profile (e.g., 'server' profile of Stream 16)
sudo dnf module install postgresql:16/server -y

# 5. Reset module stream selection back to default state
sudo dnf module reset postgresql -y
```

---

### 3.4 DNF Transaction History & Disaster Rollbacks

DNF maintains an SQLite transactional database of every installation, upgrade, and removal operation.

```bash
# 1. View recent transaction history with transaction IDs
dnf history

# Example Output:
# ID | Command line             | Date and time    | Action(s)      | Altered
# ---------------------------------------------------------------------------
#  5 | install httpd            | 2026-07-31 10:15 | Install        |   12  
#  4 | update                   | 2026-07-30 08:00 | I, U, E        |   45  

# 2. Inspect exact details of a specific transaction ID
dnf history info 5

# 3. Undo a specific destructive transaction (e.g., roll back transaction ID 5)
sudo dnf history undo 5 -y

# 4. Roll back system package state to a historical transaction point
sudo dnf history rollback 3 -y
```

---

### 3.5 Enterprise Repository Management & Air-Gapped Syncing

#### Mirroring Remote Repositories for Air-Gapped Environments

In secure enterprise environments cut off from the public internet, sysadmins sync public repositories to internal mirror servers using `dnf reposync` and index them with `createrepo_c`.

```bash
#!/usr/bin/env bash
# Air-Gapped Repository Synchronization Automation Script
set -euo pipefail

REPO_ID="epel"
LOCAL_MIRROR_DIR="/var/www/html/repos/epel9"

echo "[+] Synchronizing remote repo '${REPO_ID}' to '${LOCAL_MIRROR_DIR}'..."
mkdir -p "${LOCAL_MIRROR_DIR}"

# Download packages (download updated/new RPMs only)
dnf reposync \
    --repoid="${REPO_ID}" \
    --download-metadata \
    --newest-only \
    --destdir="${LOCAL_MIRROR_DIR}" \
    --delete

echo "[+] Updating repository metadata index via createrepo_c..."
createrepo_c --update "${LOCAL_MIRROR_DIR}"

echo "[+] Repository sync complete. Mirror path: ${LOCAL_MIRROR_DIR}"
```

---

## Section 4: Universal Sandboxed Application Formats

Universal application formats encapsulate applications alongside all runtime libraries, insulating apps from core system dependency conflicts at the cost of higher storage and memory usage.

```
+----------------------------------------------------------------------------------------+
| Feature                | Native (.deb / .rpm) | Snap (Canonical) | Flatpak (Freedesktop)|
+------------------------+----------------------+------------------+----------------------+
| Sandboxing             | No (Full system)     | AppArmor         | Bubblewrap + OSTree  |
| Distribution Focus     | Debian/Ubuntu, RHEL  | Ubuntu-centric   | Desktop/GUI Apps     |
| Packaging Model        | Shared dependencies  | Bundled / Loop   | Bundled + Shared Run |
| Mount Mechanism        | Filesystem root (/)  | Squashfs / snapd | FUSE / Flatpak DB    |
| Startup Latency        | Instant              | Minor overhead   | Minimal overhead     |
| Multi-version Support  | Difficult            | Supported        | Supported            |
+----------------------------------------------------------------------------------------+
```

### 4.1 Snap (Canonical / Ubuntu)

Snaps are mounted `squashfs` compressed file images executed within AppArmor security confinements.

```bash
# Search and install a snap with classic full-system access privileges
sudo snap install code --classic

# List installed snap packages and runtime mount points
snap list

# Inspect system mount points created by active snaps
df -h | grep /snap

# Revert an application update to the previous snap revision
sudo snap revert code

# Disable snap auto-updates via configuration window
sudo snap set system refresh.hold="$(date --date='2 days' +%Y-%m-%dT%H:%M:%S%:z)"
```

### 4.2 Flatpak (Freedesktop / Desktop GUI Ecosystem)

Flatpak isolates application runtimes using Linux namespaces, cgroups, and Bubblewrap sandboxing.

```bash
# Add Flathub remote repository
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# Search and install an application from Flathub
flatpak install flathub org.gimp.GIMP -y

# Run flatpak application from terminal
flatpak run org.gimp.GIMP

# Audit and override sandbox permissions (e.g. grant network access to an app)
flatpak override --show org.gimp.GIMP
sudo flatpak override --filesystem=/mnt/data org.gimp.GIMP
```

---

## Section 5: Real-World Infrastructure Scenarios

### Scenario A: Air-Gapped Offline Local APT Mirror with Nginx

#### Problem Statement
An enterprise datacenter enforces strict air-gap isolation. 200 Ubuntu servers cannot connect to `archive.ubuntu.com`.

#### Architecture Solution
Setup an internet-connected bastion host that mirrors deb packages using `apt-mirror` or `debmirror`, host files via Nginx, and point internal nodes to the internal URL.

```nginx
# /etc/nginx/conf.d/apt-mirror.conf on internal mirror host
server {
    listen 80;
    server_name apt-mirror.internal.enterprise.com;
    root /var/spool/apt-mirror/mirror/archive.ubuntu.com/ubuntu;

    location / {
        autoindex on;
        dav_methods off;
    }
}
```

#### Client Configuration (`/etc/apt/sources.list` on Air-Gapped Nodes):

```apt
deb http://apt-mirror.internal.enterprise.com/ubuntu jammy main restricted universe multiverse
deb http://apt-mirror.internal.enterprise.com/ubuntu jammy-updates main restricted universe multiverse
deb http://apt-mirror.internal.enterprise.com/ubuntu jammy-security main restricted universe multiverse
```

---

### Scenario B: Building a Custom Enterprise `.deb` Package from Source

#### Step 1: Create Packaging Directory Layout

```bash
mkdir -p enterprise-monitor-1.0.0/DEBIAN
mkdir -p enterprise-monitor-1.0.0/usr/local/bin
mkdir -p enterprise-monitor-1.0.0/etc/systemd/system
```

#### Step 2: Create Control Metadata (`enterprise-monitor-1.0.0/DEBIAN/control`)

```ini
Package: enterprise-monitor
Version: 1.0.0
Architecture: amd64
Maintainer: DevOps Infrastructure Team <sysadmin@enterprise.internal>
Depends: bash, curl, jq, procps
Section: utils
Priority: optional
Description: Custom enterprise daemon monitoring node health metrics.
 Collects CPU, memory, and disk usage and reports to central Prometheus pushgateway.
```

#### Step 3: Create Post-Installation Scriptlet (`enterprise-monitor-1.0.0/DEBIAN/postinst`)

```bash
#!/bin/sh
set -e

# Reload systemd manager configuration and enable service
if [ "$1" = "configure" ]; then
    chmod 0755 /usr/local/bin/enterprise-monitor.sh
    systemctl daemon-reload || true
    systemctl enable enterprise-monitor.service || true
    systemctl restart enterprise-monitor.service || true
fi

exit 0
```
*(Make script executable: `chmod 0755 enterprise-monitor-1.0.0/DEBIAN/postinst`)*

#### Step 4: Build `.deb` Package Archive

```bash
# Build the binary package
dpkg-deb --build --root-owner-group enterprise-monitor-1.0.0

# Output package produced: enterprise-monitor-1.0.0.deb
# Test installation:
sudo dpkg -i enterprise-monitor-1.0.0.deb
```

---

## Section 6: Hands-On Lab Exercises

### Lab 1: Modern Secure Repository Setup (Docker Engine)

#### Task
Add the Docker repository to an Ubuntu node using modern security best practices (GPG keyring + DEB822 format), install Docker, and verify installation without using deprecated `apt-key`.

```bash
#!/usr/bin/env bash
# Lab 1 Solution Script: Modern Repo Ingestion
set -euo pipefail

echo "[Step 1] Installing pre-requisites..."
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

echo "[Step 2] Setting up GPG key..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
sudo chmod 0644 /etc/apt/keyrings/docker.gpg

echo "[Step 3] Adding DEB822 repository entry..."
ARCH=$(dpkg --print-architecture)
CODENAME=$(lsb_release -cs)

cat <<EOF | sudo tee /etc/apt/sources.list.d/docker.sources
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: ${CODENAME}
Components: stable
Architectures: ${ARCH}
Signed-By: /etc/apt/keyrings/docker.gpg
EOF

echo "[Step 4] Updating indices and installing Docker..."
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

echo "[Verification] Docker version check:"
docker --version
```

---

### Lab 2: Multi-Repo Conflict Resolution via APT Pinning

#### Task
Configure APT Pinning to ensure that `nginx` packages are installed exclusively from `nginx.org` while all other system packages default to Ubuntu official repositories.

```bash
#!/usr/bin/env bash
# Lab 2 Solution Script: APT Pinning Setup
set -euo pipefail

# 1. Add Nginx Official Repository
curl -fsSL https://nginx.org/keys/nginx_signing.key | sudo gpg --dearmor -o /etc/apt/keyrings/nginx.gpg
sudo chmod 0644 /etc/apt/keyrings/nginx.gpg

cat <<EOF | sudo tee /etc/apt/sources.list.d/nginx.sources
Types: deb
URIs: http://nginx.org/packages/ubuntu/
Suites: $(lsb_release -cs)
Components: nginx
Signed-By: /etc/apt/keyrings/nginx.gpg
EOF

# 2. Configure Pinning Policy
cat <<EOF | sudo tee /etc/apt/preferences.d/99-nginx-official
Package: nginx*
Pin: origin nginx.org
Pin-Priority: 999
EOF

# 3. Verify Policy Application
sudo apt-get update
apt-cache policy nginx
```

---

### Lab 3: DNF Module Stream Management & Rollback

#### Task
On a Red Hat/Rocky Linux node, enable the Node.js 20 module stream, install Node.js, audit DNF history, and perform a transactional rollback to revert to Node.js 18.

```bash
#!/usr/bin/env bash
# Lab 3 Solution Script: DNF Stream Management
set -euo pipefail

echo "[Step 1] Listing available Node.js streams..."
dnf module list nodejs

echo "[Step 2] Enabling Node.js 20 stream..."
sudo dnf module enable nodejs:20 -y

echo "[Step 3] Installing Node.js 20..."
sudo dnf install -y nodejs
node -v

echo "[Step 4] Checking history..."
dnf history

echo "[Step 5] Reverting transaction via rollback..."
LAST_TX_ID=$(dnf history | awk 'NR==4 {print $1}')
sudo dnf history undo "${LAST_TX_ID}" -y

echo "[Verification] Checking Node.js state..."
node -v || echo "Node.js successfully uninstalled via DNF rollback!"
```

---

## Section 7: Enterprise Troubleshooting & Diagnostics Matrix

| Diagnostic Code / Error Symptom | Root Cause | Exact Recovery Command / Remediation Sequence |
| :--- | :--- | :--- |
| `E: Could not get lock /var/lib/dpkg/lock-frontend` | Another process (`apt`, `unattended-upgr`, `dpkg`) is holding the package lock database. | `sudo fuser -v /var/lib/dpkg/lock-frontend`<br>`sudo systemctl stop unattended-upgrades`<br>*If process is dead:* `sudo rm -f /var/lib/dpkg/lock*`<br>`sudo dpkg --configure -a` |
| `Sub-process /usr/bin/dpkg returned an error code (1)` | Post-installation scriptlet (`postinst`) failed due to bad configuration or syntax errors. | `sudo mv /var/lib/dpkg/info/package_name.postinst /var/lib/dpkg/info/package_name.postinst.bak`<br>`sudo dpkg --configure -a`<br>`sudo apt-get install -f` |
| `W: GPG error: ... Signature invalid / EXPKEYSIG` | Repository public GPG signing key has expired or changed. | Identify key ID from error output (e.g. `A4B4699639258CA0`):<br>`curl -fsSL https://repo.url/key.gpg \| sudo gpg --dearmor -o /etc/apt/keyrings/repo.gpg` |
| `RPM error: rpmdb open failed` / `db5 error (-30973)` | RPM SQLite/BDB database index files are corrupted due to unclean shutdown. | `sudo mkdir -p /var/lib/rpm/backup`<br>`sudo cp -a /var/lib/rpm/__db* /var/lib/rpm/backup/`<br>`sudo rm -f /var/lib/rpm/__db*`<br>`sudo rpm --rebuilddb`<br>`sudo dnf clean all` |
| `Hash Sum mismatch` | ISP caching proxy or corrupted apt cache index files. | `sudo rm -rf /var/lib/apt/lists/*`<br>`sudo rm -rf /var/lib/apt/lists/partial/*`<br>`sudo apt-get clean`<br>`sudo apt-get update` |
| `Error: Dependency resolution loop / broken hold` | Conflicting held packages or incompatible third-party PPA packages. | `apt-mark showhold`<br>`sudo apt-mark unhold <pkg>`<br>`sudo apt-get install -f`<br>`sudo aptitude install <pkg>` *(uses advanced SAT solver)* |

---

## Section 8: Knowledge Self-Check & Verification

- [ ] Can you explain the structural difference between `dpkg` (low-level engine) and `apt` (high-level solver)?
- [ ] Do you know why `apt-key add` is deprecated and how to use `Signed-By` with binary GPG keyrings in `/etc/apt/keyrings/`?
- [ ] Can you write a modern DEB822 formatted source entry (`.sources`)?
- [ ] Can you explain how Pin-Priority numbers affect APT package version selection?
- [ ] Do you know how to use `dnf module list` and `dnf module enable` to switch Application Streams?
- [ ] Can you execute a DNF historical transaction rollback using `dnf history undo`?
- [ ] Can you build a custom `.deb` archive containing a `control` file and `postinst` script using `dpkg-deb`?
- [ ] Can you resolve a `/var/lib/dpkg/lock-frontend` lock contention incident without corrupting system state?

---

## Progress & Verification Matrix

- [x] Mastered low-level package engines (`dpkg`, `rpm`).
- [x] Configured GPG keyrings and DEB822 repository definitions.
- [x] Configured enterprise APT pinning and priority rules.
- [x] Completed DNF AppStream stream management and transaction history rollbacks.
- [x] Completed custom Debian software packaging.
- [x] Solved package manager database lock and corruption scenarios.

---

## Next Module

→ [[04 - System Services]]
