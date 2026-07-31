# 04 - System Services: Modern Linux Init & Daemon Management

> **Phase:** 1 (Core Linux) · **Time:** ~3 weeks · **Difficulty:** ⭐⭐⭐  
> **Core Focus:** `systemd`, `systemctl`, `journalctl`, Unit File Engineering, Cgroups v2 Resource Management, Security Sandboxing, Socket Activation, Systemd Timers, Container Services, and Enterprise Troubleshooting.

---

## 1. Executive Overview & System Architecture

### What are System Services?
In modern Linux enterprise infrastructure, **system services** (often called *daemons*) are long-running background processes. They provide essential system functionality, serve network protocols (HTTP, SSH, DNS, Database management), manage hardware devices, and ensure infrastructure reliability across system reboots.

Since ~2015, virtually all major enterprise Linux distributions (RHEL/CentOS/Rocky, Ubuntu/Debian, SUSE, Fedora, Arch) standardize on **systemd** as the init system (PID 1) and service manager, replacing legacy SysVinit scripts and Upstart.

```
+-----------------------------------------------------------------------------------+
|                                 USER SPACE                                        |
|  +-------------------+   +--------------------+   +----------------------------+  |
|  | systemctl Utility |   | journalctl Utility |   |   Custom Applications      |  |
|  +---------+---------+   +---------+----------+   +-------------+--------------+  |
|            |                       |                            |                 |
|            +-----------------------+----------------------------+                 |
|                                    | (D-Bus IPC / API)                            |
|                                    v                                              |
|  +-----------------------------------------------------------------------------+  |
|  |                       systemd (PID 1 / Init System)                         |  |
|  |  +------------------+  +-------------------+  +--------------------------+  |  |
|  |  | Unit Controller  |  | Dependency Solver |  | Socket & Timer Activation |  |  |
|  |  +------------------+  +-------------------+  +--------------------------+  |  |
|  |  +------------------+  +-------------------+  +--------------------------+  |  |
|  |  | Cgroup Manager   |  | Security Sandbox  |  | Journald Logging Engine  |  |  |
|  |  +------------------+  +-------------------+  +--------------------------+  |  |
|  +---------------------------------+-------------------------------------------+  |
+------------------------------------|----------------------------------------------+
|                                    v                                              |
|                                KERNEL SPACE                                       |
|  +------------------+     +-------------------+     +--------------------------+  |
|  | Cgroups v2 Trees |     | Namespaces (PID/  |     | Seccomp / Capabilities / |  |
|  | (CPU/Mem/IO)     |     | Mount/Net/IPC)    |     | eBPF Filters             |  |
|  +------------------+     +-------------------+     +--------------------------+  |
+-----------------------------------------------------------------------------------+
```

### Why Systemd Infrastructure Matters
* **Parallelized Initialization:** Concurrent service startup drastically reduces boot time compared to sequential shell scripts.
* **Declarative Dependency Resolution:** Automatic ordering and conditional execution (`Wants=`, `Requires=`, `After=`).
* **Process Lifecycle Control:** Reliable process tracking via Control Groups (Cgroups v2)—killing a service terminates all child sub-processes, preventing orphan/zombie leaks.
* **Built-in Security Sandboxing:** Granular kernel security constraints applied directly inside unit configuration (e.g., `ProtectSystem=strict`, `PrivateTmp=yes`, `CapabilityBoundingSet=`).
* **Unified Logging Engine (`journalctl`):** Binary, structured, metadata-indexed logging synchronized across all system services and kernel ring buffers.

---

## 2. SysVinit vs. Systemd Comparative Matrix

| Architectural Feature | Legacy SysVinit / Initscripts | Modern Systemd System |
| :--- | :--- | :--- |
| **Primary Executable** | `/sbin/init` (Shell-script driven) | `/usr/lib/systemd/systemd` (C-compiled binary, PID 1) |
| **Startup Model** | Sequential execution of shell scripts (`/etc/init.d/`) | Highly parallelized dependency graph execution |
| **Process Tracking** | PID files in `/var/run/` (Fragile, susceptible to PID reuse) | Cgroups v2 tracking (Unhackable sub-tree process mapping) |
| **Configuration Format** | Imperative Bash scripts (`start()`, `stop()`, `status()`) | Declarative INI unit configuration files (`.service`, `.timer`) |
| **Logging Mechanism** | Text-based syslog (`/var/log/messages`, `/var/log/syslog`) | Binary indexed journal (`/var/log/journal/`) with rich metadata |
| **Dependency Control** | Manual script execution order numbering (`S20nginx`, `K10nginx`) | Automatic graph resolution (`After=`, `Requires=`, `Wants=`) |
| **On-Demand Activation** | Requires external daemons (`xinetd`, `inetd`) | Native Socket (`.socket`), D-Bus, Path (`.path`), and Timer (`.timer`) activation |
| **Resource Limits** | `/etc/security/limits.conf` (Per-user ulimits) | Direct per-unit Cgroups limits (`MemoryMax=`, `CPUQuota=`) |

---

## 3. Systemd Unit Types & File Locations

Systemd categorizes managed resources into **Units**. Each unit type handles a distinct infrastructure domain.

### Primary Unit Types

| Extension | Unit Type | Purpose & Description |
| :--- | :--- | :--- |
| `.service` | **Service** | Manages background daemons, applications, and scripts. |
| `.socket` | **Socket** | Manages IPC or network sockets for on-demand service activation. |
| `.timer` | **Timer** | Manages scheduled execution (replaces cron jobs with high precision). |
| `.target` | **Target** | Logical grouping of units representing runlevels/boot states (e.g., `multi-user.target`). |
| `.mount` | **Mount** | Manages filesystem mount points (replaces or integrates with `/etc/fstab`). |
| `.automount` | **Automount** | Provides on-demand automounting of local or network filesystems. |
| `.path` | **Path** | Triggers services upon file/directory modification or creation (uses `inotify`). |
| `.slice` | **Slice** | Hierarchical resource management node for cgroups resource allocation. |
| `.scope` | **Scope** | Manages externally created process groups (e.g., container runtimes, user sessions). |

### Unit Search Path Precedence
Systemd evaluates unit files using a strict override hierarchy. Files in higher-precedence directories override lower-precedence directories:

```
Higher Precedence (Administrator / Runtime Overrides)
  ├── 1. /etc/systemd/system/                 <-- Local admin custom units & overrides (PRIMARY WORKSPACE)
  ├── 2. /run/systemd/system/                 <-- Runtime generated units (ephemeral, lost on reboot)
  └── 3. /usr/lib/systemd/system/             <-- Vendor / Package installed defaults (DO NOT EDIT DIRECTLY)
Lower Precedence (Default Package Files)
```

> 💡 **Best Practice:** Never modify unit files inside `/usr/lib/systemd/system/`. Place custom units or override drop-in snippets inside `/etc/systemd/system/` or use `systemctl edit <service>`.

---

## 4. Engineering Systemd Service Units (`.service`)

A `.service` file is divided into three primary sections: `[Unit]`, `[Service]`, and `[Install]`.

### Production-Grade `.service` Unit Example

File Location: `/etc/systemd/system/production-api.service`

```ini
[Unit]
# Human-readable label displayed in systemctl status and logs
Description=Enterprise Production Payment Gateway API
Documentation=https://docs.internal.net/api/payment-service

# Execution Ordering & Dependencies
After=network-online.target PostgreSQL.service redis.service
Wants=network-online.target redis.service
Requires=postgresql.service
Conflicts=maintenance-mode.target

[Service]
# Service Execution Type (simple, forking, oneshot, notify, exec, dbus)
Type=notify
NotifyAccess=main

# Execution Credentials
User=apiworker
Group=apiworker
WorkingDirectory=/opt/production-api

# Environment Configuration
Environment=NODE_ENV=production PORT=8080
EnvironmentFile=-/etc/default/production-api

# Binary Execution Controls
ExecStartPre=/opt/production-api/bin/pre-flight-check.sh
ExecStart=/opt/production-api/bin/api-server --config /etc/production-api/config.json
ExecReload=/bin/kill -HUP $MAINPID
ExecStop=/opt/production-api/bin/graceful-shutdown.sh

# Restart Policies & Thermal Controls
Restart=on-failure
RestartSec=5s
StartLimitIntervalSec=300s
StartLimitBurst=5

# Resource Management (Cgroups v2)
MemoryMax=2G
MemoryHigh=1.8G
CPUQuota=200%
TasksMax=5000

# Security Hardening & Sandboxing Directives
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
PrivateDevices=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
NoNewPrivileges=true
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
ReadWritePaths=/var/log/production-api /var/tmp/production-api

[Install]
# Defines which target activates this unit during system enable
WantedBy=multi-user.target
```

---

## 5. Service Types Deep Dive

The `Type=` directive dictates how systemd determines whether a service has successfully launched:

```
  simple:   [systemd forks exec] ---> Service marked ACTIVE immediately (No readiness check)
  
  exec:     [systemd forks exec] ---> Service marked ACTIVE once binary successfully execve()s
  
  forking:  [parent process forks worker] ---> [parent exits 0] ---> Service marked ACTIVE
  
  oneshot:  [process runs to completion] ---> [exits 0] ---> Service marked INACTIVE (or ACTIVE if RemainAfterExit=yes)
  
  notify:   [systemd forks exec] ---> Waiting for SD_NOTIFY readiness socket signal ---> Service marked ACTIVE
```

* **`simple` (Default if ExecStart= is set):** systemd assumes the process is started immediately after `execve()` is called. Suitable for non-forking binaries.
* **`exec`:** Similar to `simple`, but systemd delays marking the unit active until the binary execution succeeds.
* **`forking`:** The executed binary spawns a background worker process and the main parent process terminates (classic UNIX daemon). Requires `PIDFile=` pointing to the daemon's PID file.
* **`oneshot`:** Used for short-lived tasks (e.g., initialization scripts). The unit stays in activating state until the process exits 0. Combine with `RemainAfterExit=yes` to keep unit in `active (exited)` state.
* **`notify`:** Modern, secure standard. The application explicitly notifies systemd of its readiness by sending a message over a UNIX socket using `sd_notify("READY=1")`.

---

## 6. Dependency Logic: `After` vs. `Requires` vs. `Wants`

Understanding systemd dependency resolution is critical to preventing race conditions during system boot.

```
       OPERATIONAL DEPENDENCIES                  EXECUTION ORDERING
    (Does Service A NEED Service B?)        (WHEN should Service A run relative to B?)
  
    +------------------------------+        +------------------------------+
    |  Requires=B.service          |        |  After=B.service             |
    |  (Hard Failure Link)         |        |  (Strict Serial Delay)       |
    +------------------------------+        +------------------------------+
  
    +------------------------------+        +------------------------------+
    |  Wants=B.service             |        |  Before=B.service            |
    |  (Soft Link - Best Effort)   |        |  (Reverse Serial Delay)      |
    +------------------------------+        +------------------------------+
```

### Dependency Matrix & Behavior

| Directive | Functional Purpose | Failure Behavior |
| :--- | :--- | :--- |
| **`Requires=`** | Enforces a hard binary dependency. | If target unit fails or stops, this unit is immediately stopped or aborted. |
| **`Wants=`** | Enforces a soft advisory dependency (Recommended). | If target unit fails to start, this unit will still proceed to execute normally. |
| **`BindsTo=`** | Ultra-strict hard dependency. | If target unit goes down (or device unplugged), this unit is abruptly terminated. |
| **`Requisite=`** | Immediate pre-flight check dependency. | If target unit is not *already active*, this unit fails instantly without starting target. |
| **`Conflicts=`** | Mutually exclusive units. | Starting this unit automatically stops any conflicting units running currently. |
| **`After=`** | Controls execution startup sequence (Ordering ONLY). | Does NOT start target unit; only dictates sequence if both units are scheduled to start. |
| **`Before=`** | Controls execution startup sequence (Ordering ONLY). | Forces target unit to wait until this unit finishes starting. |

> ⚠️ **CRITICAL ARCHITECTURAL WARNING:** `After=` and `Wants=`/`Requires=` are completely decoupled!  
> * Setting `Wants=foo.service` WITHOUT `After=foo.service` means systemd starts both services **in parallel concurrently**, leading to potential network or database connection drops! Always specify **BOTH** dependency and ordering directives.

---

## 7. Security Sandboxing & Hardening Engine

Systemd provides enterprise-grade Linux kernel isolation capabilities built directly into PID 1.

```ini
[Service]
# Filesystem Isolation
ProtectSystem=strict        # Mounts /usr, /boot, /etc as read-only for this process
ProtectHome=true            # Hides /home, /root, /run/user from service vision
PrivateTmp=true             # Mounts isolated, per-service /tmp and /var/tmp directories
ReadOnlyPaths=/opt/app/conf # Explicit read-only path mounts
ReadWritePaths=/var/log/app # Explicit read-write target path mounts

# Process & Credential Restrictions
NoNewPrivileges=true        # Prevents child processes from gaining privileges via setuid binaries
PrivateDevices=true         # Denies access to physical devices (/dev/sd*, /dev/mem); presents /dev/null only
ProtectKernelTunables=true  # Makes /proc/sys, /sys, /proc/sysrq-trigger read-only
ProtectKernelModules=true   # Denies explicit module loading via modprobe
ProtectControlGroups=true   # Makes /sys/fs/cgroup read-only for service

# Network & Privilege Filtering
CapabilityBoundingSet=CAP_NET_BIND_SERVICE # Restricts Linux Capabilities (only allow binding <1024 ports)
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6 # Blocks UNIX raw sockets, packet sockets
SystemCallFilter=@system-service ~@privileged ~@resources # Seccomp syscall filtering blacklist
```

### Auditing Security Posture
Inspect the security score of any active or installed service using `systemd-analyze security`:

```bash
# Analyze security posture of nginx
systemd-analyze security nginx.service
```

*Output Breakdown:*
```
NAME                          DESCRIPTION                                         EXPOSURE
✔ PrivateTmp=                 Service has a private /tmp directory                0.0
✔ ProtectSystem=              Service has strict read-only system mounts          0.0
❌ CapabilityBoundingSet=     Service has no capability bounding set restricted   0.4
...
→ Overall exposure level for nginx.service: 2.1 OK (Lower score = higher security)
```

---

## 8. Cgroups v2 Resource Controls

Systemd leverages Linux Cgroups v2 to regulate CPU, Memory, Disk I/O, and Process Limits without requiring external tooling.

```ini
[Service]
# Memory Limits
MemoryMin=256M               # Absolute protected memory footprint (kernel won't reclaim below this)
MemoryHigh=1.5G              # Soft limit: triggers aggressive throttling and reclaim when breached
MemoryMax=2G                 # Hard limit: process triggers Out-Of-Memory (OOM) killer if exceeded
MemorySwapMax=512M           # Maximum swap space allowable

# CPU Limits
CPUWeight=100                # Relative CPU share weight (1-10000, default is 100)
CPUQuota=150%                # Hard limit: allows maximum 1.5 CPU cores utilization across threads

# Task & Process Controls
TasksMax=1024                # Prevents fork-bomb vulnerability by capping max threads/processes

# Disk I/O Controls
IOWeight=100                 # I/O scheduling weight
IOReadBandwidthMax=/dev/sda 100M  # Limit read throughput on device to 100 MB/s
IOWriteBandwidthMax=/dev/sda 50M  # Limit write throughput on device to 50 MB/s
```

### Resource Monitoring & Inspection Commands
```bash
# View active control group tree layout
systemd-cgls

# Live interactive top-style cgroup resource view
systemd-cgtop

# Inspect current cgroup configuration for a specific service
systemctl show nginx.service --property=MemoryMax,CPUQuota,TasksCurrent
```

---

## 9. Systemd Timers (`.timer`): Modern Cron Replacement

Systemd Timers replace legacy `cron` jobs with microsecond precision, integrated journal logging, dependency enforcement, and event-driven triggers.

Creating a timer requires **two files**:
1. `service-name.service` (Execution payload)
2. `service-name.timer` (Scheduling trigger)

### Step 1: Payload Unit (`/etc/systemd/system/db-backup.service`)
```ini
[Unit]
Description=Automated Database Backup Job
After=postgresql.service

[Service]
Type=oneshot
User=postgres
ExecStart=/usr/local/bin/backup-database.sh
```

### Step 2: Timer Trigger Unit (`/etc/systemd/system/db-backup.timer`)
```ini
[Unit]
Description=Daily Database Backup Schedule Trigger

[Timer]
# Option A: Monotonic Timer (Relative to events)
# OnBootSec=15min            # Trigger 15 minutes after system boot
# OnUnitActiveSec=1d         # Trigger 1 day after last unit activation

# Option B: Real-Time Calendar Timer (Cron-like syntax)
OnCalendar=Mon..Fri *-*-* 02:00:00   # Run Monday through Friday at 2:00 AM UTC

# Drift & Performance Optimizations
RandomizedDelaySec=30min             # Prevents resource spikes by spreading execution across a 30m window
Persistent=true                      # Catches up missed executions if machine was powered down during run time

[Install]
WantedBy=timers.target
```

### Managing Timers
```bash
# Reload daemon and enable timer
sudo systemctl daemon-reload
sudo systemctl enable --now db-backup.timer

# List all active system timers with next scheduled run time
systemctl list-timers --all
```

---

## 10. Socket Activation (`.socket`)

Socket activation allows systemd to create and listen on network/IPC sockets (ports, UNIX sockets) *before* the application starts. When traffic arrives on the socket, systemd instantly launches the service and passes the file descriptor to the process.

### Benefits:
* **Zero Downtime Reloads:** Traffic queues in the kernel socket buffer while service restarts.
* **On-Demand Resource Saving:** Services remain unlaunched in RAM until an actual incoming packet arrives.

```
  1. Client sends HTTP request to Port 80
                 │
                 ▼
  2. Systemd Kernel Socket intercepts request (Socket Unit active)
                 │
                 ▼
  3. Systemd instantly launches target Service Unit & passes Socket File Descriptor (FD)
                 │
                 ▼
  4. Service Unit processes payload & returns response transparently
```

### Socket Unit (`/etc/systemd/system/web-app.socket`)
```ini
[Unit]
Description=On-Demand Web Socket Listener

[Socket]
ListenStream=8080
ListenStream=127.0.0.1:8081
Accept=false

[Install]
WantedBy=sockets.target
```

### Service Unit (`/etc/systemd/system/web-app.service`)
```ini
[Unit]
Description=Web Application Server Process
Requires=web-app.socket
After=web-app.socket

[Service]
Type=simple
ExecStart=/opt/webapp/bin/server
NonBlocking=true
```

---

## 11. Centralized Logging Architecture (`journalctl`)

Systemd's logging engine (`systemd-journald`) captures standard output (`stdout`), standard error (`stderr`), kernel ring messages, and syslog events into an indexed binary journal format.

```
  Applications (stdout/stderr) ───┐
  Kernel Ring Buffer (kmsg)    ───┼──► systemd-journald ──► /var/log/journal/ ──► journalctl
  Audit Logs (auditd)          ───┤    (Binary Storage)   (Filtering API)      (CLI Output)
  Syslog API (sd_journal)      ───┘
```

### Journald Configuration (`/etc/systemd/journald.conf`)
```ini
[Journal]
Storage=persistent
Compress=yes
SystemMaxUse=2G
SystemKeepFree=1G
SystemMaxFileSize=250M
MaxRetentionSec=1month
ForwardToSyslog=no
```

### Master `journalctl` Command Cheatsheet

| Goal / Query Task | Production Command |
| :--- | :--- |
| **Follow Live Logs (Tail)** | `journalctl -f` |
| **Filter by Unit / Service** | `journalctl -u nginx.service` |
| **Filter by Specific PID** | `journalctl _PID=4521` |
| **Filter by Log Priority / Severity** | `journalctl -p err..emerg` *(Levels: emerg, alert, crit, err, warning, notice, info, debug)* |
| **Filter Current Boot Only** | `journalctl -b` |
| **Filter Previous Boot** | `journalctl -b -1` |
| **Time-Range Filtering** | `journalctl --since "2026-07-31 00:00:00" --until "2026-07-31 12:00:00"` |
| **Relative Time Filtering** | `journalctl --since "1 hour ago"` |
| **Format Output as JSON** | `journalctl -u nginx.service -o json-pretty` |
| **Kernel Log Output Only** | `journalctl -k` |
| **Check Disk Space Usage** | `journalctl --disk-usage` |
| **Vacuum Log Files by Size** | `sudo journalctl --vacuum-size=500M` |
| **Vacuum Log Files by Age** | `sudo journalctl --vacuum-time=14d` |

---

## 12. User Services & Lingering (`systemctl --user`)

Non-privileged users can manage their own personal services without root privileges using systemd user mode.

### Directory Structure & Execution
* User Units Location: `~/.config/systemd/user/`
* Execution Control: `systemctl --user <command>`

```bash
# Create user systemd directory
mkdir -p ~/.config/systemd/user

# Create user service
cat <<'EOF' > ~/.config/systemd/user/user-notifier.service
[Unit]
Description=Personal User Sync Daemon

[Service]
ExecStart=/usr/bin/python3 %h/bin/sync-script.py
Restart=on-failure

[Install]
WantedBy=default.target
EOF

# Reload user daemon and start unit
systemctl --user daemon-reload
systemctl --user enable --now user-notifier.service
```

### Enabling User Lingering (Headless Execution)
By default, user services are spawned only when the user logs in and are terminated when the user logs out. To allow user services to run headlessly on boot without an active session:

```bash
# Enable lingering for specific user (Run as root)
sudo loginctl enable-linger owais

# Verify lingering status
loginctl show-user owais | grep Linger
```

---

## 13. Container Orchestration with Systemd

Modern infrastructure integrates containers (Docker / Podman) with systemd for process supervision, boot ordering, and auto-restart policies.

### Wrapper Systemd Unit for Docker (`/etc/systemd/system/docker-redis.service`)

```ini
[Unit]
Description=Enterprise Redis Container Service
After=docker.service
Requires=docker.service

[Service]
TimeoutStartSec=0
Restart=always
ExecStartPre=-/usr/bin/docker stop redis-prod
ExecStartPre=-/usr/bin/docker rm redis-prod
ExecStartPre=/usr/bin/docker pull redis:7-alpine
ExecStart=/usr/bin/docker run --name redis-prod \
  --p 6379:6379 \
  -v /var/data/redis:/data \
  redis:7-alpine redis-server --appendonly yes
ExecStop=/usr/bin/docker stop redis-prod

[Install]
WantedBy=multi-user.target
```

---

## 14. Essential System Management CLI Commands

```bash
# ==============================================================================
# SYSTEMCTL COMMAND CHEATSHEET
# ==============================================================================

# Unit State Lifecycle Controls
sudo systemctl start <unit>          # Start service immediately
sudo systemctl stop <unit>           # Stop running service
sudo systemctl restart <unit>        # Restart service (stop + start)
sudo systemctl reload <unit>         # Reload service configuration without stopping
sudo systemctl reload-or-restart <unit> # Reload if supported, otherwise restart

# Boot Enablement Controls
sudo systemctl enable <unit>         # Enable service on boot (creates symlink)
sudo systemctl disable <unit>        # Disable service on boot (removes symlink)
sudo systemctl enable --now <unit>   # Enable AND start service in single step
sudo systemctl mask <unit>           # Symlink unit to /dev/null (Prevents any execution)
sudo systemctl unmask <unit>         # Remove mask restriction

# Unit Status & Inspection
systemctl status <unit>              # Detailed operational status, PID, logs
systemctl is-active <unit>           # Return 0 if active, non-zero if inactive (Scripting)
systemctl is-enabled <unit>          # Return 0 if enabled on boot
systemctl is-failed <unit>           # Return 0 if unit failed state

# System Analysis & Boot Performance
systemctl daemon-reload              # Re-scan filesystem for unit changes (MANDATORY AFTER EDIT)
systemd-analyze                      # Show total startup time split between Kernel & Userspace
systemd-analyze blame                # List units sorted by boot time consumption
systemd-analyze critical-chain       # Display tree of time-critical unit dependencies

# Target & Runlevel Control
systemctl get-default                # Show default boot target (e.g., multi-user.target)
sudo systemctl set-default graphical.target # Change default boot state
sudo systemctl isolate rescue.target # Switch immediately to single-user rescue mode
```

---

## 15. Real-World Infrastructure Scenarios

### Scenario A: Production Microservice Deployment with Auto-Restart & Hardening
**Context:** A mission-critical microservice crashes under high traffic loads. The engineering team requires zero manual intervention, memory cap protection, and isolated security.

**Solution Architecture:**
1. Configure `Restart=on-failure` with `RestartSec=3s` and a burst window (`StartLimitBurst=5` within `StartLimitIntervalSec=60s`) to prevent runaway crash loops.
2. Enforce strict cgroup RAM bounds (`MemoryMax=1G`).
3. Apply `ProtectSystem=strict` and `NoNewPrivileges=true`.

### Scenario B: Zero-Downtime Application Reload Pattern
**Context:** Updating configuration files for web servers (Nginx/HAProxy) without dropping active customer TCP connections.

**Solution Architecture:**
1. Use `ExecReload=/bin/kill -HUP $MAINPID` inside the unit.
2. Run `sudo systemctl reload nginx`.
3. The master PID parses the new configuration file, spawns new worker threads, and gracefully terminates old workers after existing connections finish draining.

---

## 16. Step-by-Step Hands-On Labs

### Lab 1: Building, Hardening, and Deploying a Custom Python Daemon

#### Objective
Create a custom Python service script, write a production systemd unit file with security sandboxing, enable and manage its lifecycle.

#### Step 1: Create Payload Script
```bash
sudo mkdir -p /opt/pydaemon
sudo bash -c 'cat <<"EOF" > /opt/pydaemon/app.py
import time
import sys
import os

print(f"Starting Python Daemon PID: {os.getpid()}", flush=True)

while True:
    print("Daemon heartbeat active...", flush=True)
    time.sleep(5)
EOF'

# Create dedicated service user
sudo useradd -r -s /bin/false pyworker
sudo chown -R pyworker:pyworker /opt/pydaemon
```

#### Step 2: Create Hardened Service Unit
```bash
sudo bash -c 'cat <<"EOF" > /etc/systemd/system/pydaemon.service
[Unit]
Description=Hardened Python Background Daemon
After=network.target

[Service]
Type=simple
User=pyworker
Group=pyworker
WorkingDirectory=/opt/pydaemon
ExecStart=/usr/bin/python3 /opt/pydaemon/app.py
Restart=on-failure
RestartSec=3s

# Security Hardening
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
NoNewPrivileges=true
MemoryMax=256M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
EOF'
```

#### Step 3: Test and Verify
```bash
# Reload daemon
sudo systemctl daemon-reload

# Enable and start unit
sudo systemctl enable --now pydaemon.service

# Check operational status
systemctl status pydaemon.service

# Inspect live journal output
sudo journalctl -u pydaemon.service -f --no-pager
```

---

### Lab 2: Creating a Systemd Precision Timer Replacement for Cron

#### Objective
Deploy a custom database cleanup job that fires every day at midnight with a randomized delay.

#### Step 1: Create Payload Unit (`/etc/systemd/system/log-cleanup.service`)
```bash
sudo bash -c 'cat <<"EOF" > /etc/systemd/system/log-cleanup.service
[Unit]
Description=Ephemeral Log Cleanup Task

[Service]
Type=oneshot
ExecStart=/usr/bin/find /var/log/tmp-app/ -type f -mtime +7 -delete
EOF'
```

#### Step 2: Create Timer Unit (`/etc/systemd/system/log-cleanup.timer`)
```bash
sudo bash -c 'cat <<"EOF" > /etc/systemd/system/log-cleanup.timer
[Unit]
Description=Daily Execution Trigger for Ephemeral Log Cleanup

[Timer]
OnCalendar=*-*-* 00:00:00
RandomizedDelaySec=15m
Persistent=true

[Install]
WantedBy=timers.target
EOF'
```

#### Step 3: Load and Inspect
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now log-cleanup.timer

# Verify timer registry
systemctl list-timers log-cleanup.timer
```

---

### Lab 3: Boot Performance Profiling & Optimization

#### Objective
Analyze boot time bottlenecks and generate a graphical dependency plot.

```bash
# Print total startup time breakdown
systemd-analyze

# Display top 10 slowest boot services
systemd-analyze blame | head -n 10

# Print critical boot chain ordering
systemd-analyze critical-chain

# Export SVG boot graph (Requires SVG viewer)
systemd-analyze plot > /tmp/boot_analysis.svg
echo "Boot plot generated at /tmp/boot_analysis.svg"
```

---

## 17. Production System Administration Troubleshooting Matrix

| Issue / Symptom | Root Cause Analysis | Diagnostic Command | Remediation Action |
| :--- | :--- | :--- | :--- |
| **`Active: failed (Result: exit-code)`** | Binary failed to start due to missing environment, wrong path, or syntax error. | `journalctl -u <unit> -e -n 50` | Inspect log output. Verify `ExecStart=` path executable and check permissions. |
| **`Active: failed (Result: start-limit-hit)`** | Service crashed repeatedly in a short window, exceeding `StartLimitBurst`. | `systemctl status <unit>` | Fix underlying crash cause. Reset failure counter: `sudo systemctl reset-failed <unit>`. |
| **`Unit <name> is masked.`** | Symlink to `/dev/null` exists in `/etc/systemd/system/`. | `ls -la /etc/systemd/system/<unit>` | Unmask service: `sudo systemctl unmask <unit>`. |
| **`Permission Denied (status=203/EXEC)`** | Missing execute (`+x`) permissions on binary, or incorrect SELinux/AppArmor context. | `ls -l /path/to/binary` & `dmesg \| grep audit` | Add permissions (`chmod +x`) or update SELinux label (`restorecon -v`). |
| **`Process OOM Killed (status=137/OOM)`** | Cgroup memory limit (`MemoryMax=`) was breached by process allocations. | `dmesg \| grep -i oom` & `journalctl -k` | Increase `MemoryMax=` in unit or optimize application RAM utilization. |
| **`Changes to unit file ignored`** | Disk unit file modified but systemd daemon state was not updated in RAM. | `systemctl status <unit>` *(Warning displayed)* | Execute `sudo systemctl daemon-reload`. |
| **`Failed to start: Dependency failed`** | A required dependency specified in `Requires=` or `BindsTo=` failed to launch. | `systemctl list-dependencies <unit>` | Troubleshoot and resolve the failing upstream dependency unit first. |
| **`Service hangs during shutdown/restart`** | Process ignored `SIGTERM` and timed out waiting for `TimeoutStopSec=`. | `journalctl -u <unit> --since "5 min ago"` | Send `SIGKILL` or shorten `TimeoutStopSec=30s` in unit definition. |

---

## 18. Verification Checklist & Self-Assessment

- [ ] Can you explain the structural role of PID 1 and systemd in modern Linux systems?
- [ ] Do you know the difference between unit locations in `/etc/systemd/system/` vs `/usr/lib/systemd/system/`?
- [ ] Can you write a custom `.service` file with `[Unit]`, `[Service]`, and `[Install]` sections?
- [ ] Do you understand why `After=` and `Wants=`/`Requires=` must be paired together?
- [ ] Can you enforce Cgroups v2 resource limits (`MemoryMax=`, `CPUQuota=`) on a service?
- [ ] Do you know how to apply security sandboxing directives (`ProtectSystem=`, `PrivateTmp=`, `NoNewPrivileges=`)?
- [ ] Can you replace a legacy crontab job with a systemd `.timer` and `.service` pair?
- [ ] Are you comfortable querying binary logs with `journalctl` using time, unit, and priority filters?
- [ ] Can you enable headless user services using `loginctl enable-linger`?
- [ ] Do you know how to debug `start-limit-hit` and exit code errors using `systemctl reset-failed` and logs?

---

## 19. Summary & Next Steps

### Key Takeaways
1. **Systemd** unifies init, service management, logging (`journald`), resource control (`cgroups v2`), and event scheduling (`timers`).
2. Declarative `.service` files eliminate fragile shell scripts and provide predictable, ordered service startup.
3. Systemd sandboxing directives allow sysadmins to secure applications right at the system layer without external virtualization wrappers.

### Next Module
Proceed to **[[06 - Storage & Backups]]** to master Linux filesystem management, LVM, mounting, and automated backup strategies.
