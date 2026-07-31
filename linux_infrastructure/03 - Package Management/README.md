# 03 - Package Management

> **Phase:** 1 (Core Linux) · **Time:** ~3 weeks · **Difficulty:** ⭐⭐

## What it is
**Package management** is how Linux systems install, update, remove, and configure software. It centralizes dependencies, permissions, and metadata, making life easier for users and administrators.

Two major package ecosystem families:
- **Debian‑based** (apt, dpkg, apt‑cache): Ubuntu, Debian, Pop!_OS, elementary OS, etc.
- **Red Hat‑based** (dnf, rpm, yum, dnf-plugins): Fedora, CentOS, RHEL, Rocky Linux, AlmaLinux.

Most beginner learning resources start with `apt` because it’s the most common on popular desktop distros.

## Why it matters
- **Reliable installs:** one command pulls the correct version and dependencies.
- **System integrity:** checks for broken packages, conflicts, and security advisories.
- **Updates:** keep software and the kernel current with minimal friction.
- **Cleanup:** remove unused dependencies after uninstalling applications.
- **Reproducibility:** package lists (`*.list` files) allow identical environments across machines.

## Core concepts — detailed

### 1. Core commands (Debian/Ubuntu style)
| Command | Action | Example use case |
|---|---|---|
| `apt update` | Refresh package lists (index of available packages) | Runs before any install; cheap if recent |
| `apt upgrade` | Upgrade all installed packages to latest versions | Usually runs automatically via cron |
| `apt install <pkg>` | Install a package and all its dependencies | `apt install curl` |
| `apt remove <pkg>` | Remove a package (keeps config files) | `apt remove git` |
| `apt purge <pkg>` | Remove package **and** config files | `apt purge vim` |
| `apt search <keyword>` | Search available packages | `apt search python3` |
| `apt show <pkg>` | Show package metadata (version, size, description) | `apt show tmux` |

> Tip: Use `sudo apt …` for commands that modify system‑wide packages.

### 2. Red Hat / CentOS equivalents
```bash
dnf update
dnf install <pkg>
dnf remove <pkg>
dnf clean all  # similar to apt’s cleanup
```

### 3. Package files (`.deb`, `.rpm`)
- **`.deb`** = Debian package: control files, data files, dependencies.
- **`.rpm`** = Red Hat package: similar but different tooling.
- End‑users rarely need to inspect internals; just use the package manager.

### 4. Repository configuration
**Debian's default repos:**
```text
# /etc/apt/sources.list (example)
deb http://deb.debian.org.uk/debian bullseye main deb http://deb.debian.org.uk/debian bullseye-updates main deb http://deb.debian.org.uk/debian bullseye-security main
deb http://deb.debian.org.uk/debian sid main
```

**Adding third‑party repos** (e.g., Docker):
```bash
sudo apt install curl
sudo curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
sudo apt-add-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker.io
```

### 5. Dependency resolution
- Dependencies are declared in package meta (`control` file).
- `apt` automatically pulls required packages, recursive as needed.
- Conflict resolution: apt will suggest alternatives if a package cannot be installed.

### 6. Backports and pinning
**Pinning** (`/etc/apt/preferences.d/`): e.g., force a specific version:
```conf
Package: *
Pin: release a=bookworm
Pin-Priority: 500
Package: some‑package
Pin: version 2.1.*
Pin-Priority: 1001
```

**Backports** (`bullseye-backports`): newer software for older releases.

### 7. Non‑Deb packages (Snap, Flatpak, Docker)
Snap and Flatpak provide sandboxed application bundles independent of system packages.

> For learning, focus on `apt` first; other formats are optional but popular.

## Free resources — curated for self‑learners

1. **Debian & Ubuntu Admin Guide** (online, free):
   - https://www.debian.org/doc/manuals/debian-handbook/ (Chapter on package management)
2. **Man pages:** `man 8 apt`, `man 8 dpkg`
3. **DigitalOcean – How To Install Software on Debian/Ubuntu**:
   - https://www.digitalocean.com/community/tutorials/how-to-install-software-on-ubuntu-and-debian-linux
4. **Red Hat Package Management Docs** (for RPM systems):
   - https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/
5. **TSDR – Ubuntu Package Management Cheat Sheet** (download from internet):
   - https://www.computerhope.com/unix/apt.htm
6. **Snap/Flatpak docs** for later exploration.

## Practice labs (run as root or with sudo; use safe test boxes)

### Lab 1: Update and upgrade (safe)
```bash
# Update package lists ( lightweight )
sudo apt update

# Upgrade all installed packages (interactive, safe)
sudo apt upgrade -y
```

### Lab 2: Search, show, install a package
```bash
# Search for ‘git’ (autocomplete with Tab)
sudo apt search git | grep -i git
# Install git (incl. dependencies)
sudo apt install git -y
# Check version
git --version
```

### Lab 3: Show metadata
```bash
# Show details for package ‘htop’
sudo apt show htop | head -10
```

### Lab 4: Remove and purge
```bash
# Uninstall ‘wget’ (leave configs)
sudo apt remove wget

# Remove ‘vim’ and delete configs
sudo apt purge vim
```

### Lab 5: Add a third‑party repo (Docker)
```bash
sudo apt install -y curl gnupg2
sudo curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
sudo apt-add-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker.io
```

## Self‑check (can you…)
- [ ] `apt update` refreshes the list; `apt upgrade` upgrades installed.
- [ ] Use `apt install <pkg>` and `apt remove`/`apt purge`.
- [ ] Search and show package details (`apt search`, `apt show`).
- [ ] Add a new software repository and install from it.
- [ ] Explain the difference between `.deb` packages and snap/flatpak.

## Progress
- [ ] Completed Labs 1‑5 (verify packages installed, configs removed appropriately)
- [ ] Explain how `apt` resolves dependencies.
- [ ] Set up a non‑default repository (e.g., Docker) successfully.
- [ ] Compare Debian-based vs Red Hat package tools.

## Link to next module
→ [[04 - System Services]]
