# 04 - System Services

> **Phase:** 1 (Core Linux) · **Time:** ~3 weeks · **Difficulty:** ⭐⭐⭐

## What it is
**System services** are long‑running processes that run in the background, provide functionality (web servers, databases, logging), and survive reboots. In modern Linux, almost all services are managed by **systemd** (the init system introduced in 2015, replacing SysV init scripts).

We’ll cover:
- What a systemd service is
- Core `systemctl` commands
- Enabling, starting, stopping, disabling, and masking services
- User vs. system services
- “WantedBy” and “Requires” unit dependencies
- Container orchestration basics (Docker, Docker Compose)
- Logs and troubleshooting (`journalctl`)

## Why it matters
- **Automation:** start/stop services with one command.
- **Reliability:** systemd guarantees ordering, restarts, and dependency resolution.
- **Modern tooling:** containers, CI/CD, cloud apps all rely on service management.
- **Debugging:** centralized logs, status checks, and service units make troubleshooting easier.

## Core concepts — detailed

### 1. Systemd units
Systemd uses **unit files** (`.service`, `.socket`, `.timer`, `.target`, `.mount`, `.network`).

**Basic unit file syntax** (example `/etc/systemd/system/foo.service`):
```ini
[Unit]
Description=My sample service
After=network.target
Wants=network.target

[Service]
Type=simple
ExecStart=/usr/bin/sleep infinity
Restart=on-failure
User=nobody
Group=nogroup

[Install]
WantedBy=multi-user.target
```

**Key sections:**
- **`[Unit]`**: metadata, dependencies, and constraints.
- **`[Service]`**: how to start the process.
- **`[Install]`**: what happens when the service is enabled (`WantedBy`, `Also`).

**Common service types:**
- `simple` (one command, exits = failure)
- `forking` (parent process execs worker; parent exits)
- `oneshot` (executes once, use RemainAfterExit to stay active)
- `dbus` (for D‑Bus services)
- `notify` (service sends readiness notification)
- `exec` (generic, default)

### 2. Fundamental systemctl commands
| Command | Purpose | Typical use |
|---|---|---|
| `systemctl status <service>` | Show active state, main PID, recent logs | Check if nginx runs |
| `systemctl start <service>` | Start or restart a service | `systemctl start mysql` |
| `systemctl stop <service>` | Stop a running service | `systemctl stop nginx` |
| `systemctl restart <service>` | Stop then start | Reload config changes |
| `systemctl enable <service>` | Configure to start on boot (`/etc/systemd/system/*.wants/`) |
| `systemctl disable <service>` | Remove boot start (`.wants/`) but keep file |
| `systemctl mask <service>` | Prevent starting (symlink to `/dev/null`) |
| `systemctl is-active <service>` | Exit 0 if active, non‑0 otherwise (script friendly) |

**Common targets:**
- `multi-user.target` (multi‑user login, normal servers)
- `graphical.target` (X/Wayland login)
- `network.target` (network ready)
- `remote-fs.target` (remote file systems mounted)
- `time-sync.target` (ntp synchronized)

### 3. User vs. system services
- **System (root) services:** in `/etc/systemd/system/` or `systemd/system/`.
- **User services:** `~/.config/systemd/user/` (per‑user). `systemctl --user` commands.

**Systemd user mode** (thanks to `DBus Session Bus`): if you run `systemctl --user` for GNOME/KDE, you can start/stop personal services without root.

### 4. Dependencies: `After`, `Requires`, `Wants`
- **`After=network.target`** – start service after network target.
- **`Requires=network.target`** – stronger; if network fails, unit won’t start.
- **`Wants=network.target`** – start if target exists but don’t fail if it’s missing.

**Example:** a web server needs the network ready before it binds to ports.

### 5. Docker and systemd integration
**Containers as services** (Docker Compose 2+ uses systemd under the hood):

**Docker Compose example (`docker-compose.yml`):**
```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    restart: unless-stopped
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
```

**Running:** `docker compose up -d` → systemd creates a "container" unit per service.

**Docker‑unprivileged on host:** `docker run -d --name foo busybox sleep infinity`

### 6. Logs: `journalctl` basics
- **System logs** (`/var/log/syslog`, `/var/log/journal`) are unified in `journalctl`.
- **Filtering:** `journalctl -u nginx` (service), `journalctl -u nginx -b` (current boot), `journalctl --since "2025-07-20 12:00"`.

### 7. Security and best practices
- **User restriction:** services should run as non‑root users (e.g., `nobody`, dedicated service accounts).
- **Capability bounding:** remove unnecessary capabilities (`CapabilityBoundingSet=`).
- **Read limiting:** read-only filesystem for binaries.
- **Resource limits:** `LimitNOFILE=1024`, etc.
- **Logging:** use structured logs, configure `SystemMaxUse`.

## Free resources

1. **Systemd Official Documentation:** https://www.freedesktop.org/software/systemd/man/
2. **Tldr pages:** `systemctl tldr` (for quick command overview)
3. **DigitalOcean: How to Use Systemd:** https://www.digitalocean.com/community/tutorials/an-introduction-to-systemd
4. **Docker Compose docs:** https://docs.docker.com/compose/overview/
5. **OverTheWire: Bandit (Wargame) — practical file ownership and sudo**:
   - https://overthewire.org/wargames/bandit/
6. **Microsoft Docs: WSL2 systemd details** (if using WSL):
   - https://learn.microsoft.com/en-us/windows/wsl/systemd

## Practice labs (run as root or with sudo; use safe test directories)

### Lab 1: Create a systemd service
```bash
# As root
sudo bash -c 'cat > /etc/systemd/system/myscript.service <<EOF
[Unit]
Description=Sample daemon showing systemctl usage
After=network.target
Wants=network.target

[Service]
Type=simple
ExecStart=/usr/bin/sleep infinity
Restart=on-failure
User=nobody
Group=nogroup

[Install]
WantedBy=multi-user.target
EOF'
```

### Lab 2: Enable and start the service
```bash
sudo systemctl daemon-reload          # reload unit files
sudo systemctl enable myscript.service
sudo systemctl start myscript.service
sudo systemctl status myscript.service
```

### Lab 3: Verify status and logs
```bash
sudo systemctl is-active myscript.service && echo "active"
sudo journalctl -u myscript.service -b --no-pager
```

### Lab 4: Stop, disable, and mask
```bash
sudo systemctl stop myscript.service
sudo systemctl disable myscript.service
sudo systemctl mask myscript.service
```

### Lab 5: Docker as a service (Container orchestration)
```bash
# Create a docker-compose file
sudo bash -c 'cat > /home/user/docker-compose.yml <<EOF
services:
  app:
    image: nginx:alpine
    ports:
      - "8080:80"
    restart: unless-stopped
EOF'

# Run it
sudo docker compose -f /home/user/docker-compose.yml up -d
# Inspect systemd units for containers
sudo systemctl list-units --type=service | grep docker
```

### Lab 6: User systemd (optional)
```bash
# Enable user systemd (GNOME/KDE)
systemctl --user daemon-reload

# Create a user service
mkdir -p ~/.config/systemd/user/
cat > ~/.config/systemd/user/myservice.service <<EOF
[Unit]
Description=User service (background script)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/sleep 10

[Install]
WantedBy=default.target
EOF

systemctl --user enable --now myservice.service
```

## Self‑check (can you…)
- [ ] Explain what a systemd unit file is and its sections (`[Unit]`, `[Service]`, `[Install]`)
- [ ] Create a systemd service from scratch and enable/start it
- [ ] Use `systemctl status`, `start`, `stop`, `enable`, `disable`, `mask`
- [ ] Explain the difference between `After`, `Requires`, and `Wants`
- [ ] Explain user vs. system services and `systemctl --user`
- [ ] Show how Docker Compose integrates with systemd
- [ ] Filter and read logs with `journalctl`

## Progress
- [ ] Created a systemd service file (correct syntax)
- [ ] Enabled and started a service (status check)
- [ ] Used core systemctl commands (start, stop, enable, disable, mask)
- [ ] Explored Docker as a service (compose) and logs
- [ ] Explored user systemd (if applicable)

## Next
→ [[06 - Storage & Backups]]
