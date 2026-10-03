# 08 - Containers

> **Phase:** 1 (Core Linux) · **Time:** ~4 weeks · **Difficulty:** ⭐⭐⭐⭐
> **Prerequisites:** `01 - Linux Basics`, `02 - Users & Permissions`, `04 - System Services`, `06 - Storage & Backups`, `07 - Networking`

---

## Executive Summary & Fundamentals

**Containers** are lightweight, isolated execution environments that share the host Linux kernel while maintaining isolated process trees, network stacks, mount tables, and user spaces. Unlike Virtual Machines (VMs)—which require hypervisors (e.g., KVM, ESXi) and full guest operating systems—containers leverage native Linux kernel features to package applications with their exact runtime dependencies.

```
+-------------------------------------------------------+
|                 VIRTUAL MACHINES                      |
| +---------------+ +---------------+ +---------------+ |
| | App / Code    | | App / Code    | | App / Code    | |
| | Bins / Libs   | | Bins / Libs   | | Bins / Libs   | |
| | Guest OS      | | Guest OS      | | Guest OS      | |
| +---------------+ +---------------+ +---------------+ |
| |              Hypervisor (KVM / ESXi)                | |
| +-----------------------------------------------------+ |
| |                    Host OS / Kernel                 | |
+-------------------------------------------------------+

+-------------------------------------------------------+
|                    CONTAINERS                         |
| +---------------+ +---------------+ +---------------+ |
| | App / Code    | | App / Code    | | App / Code    | |
| | Bins / Libs   | | Bins / Libs   | | Bins / Libs   | |
| +---------------+ +---------------+ +---------------+ |
| |      Container Runtime (containerd / podman)        | |
| +-----------------------------------------------------+ |
| |            Host Linux Kernel (cgroups/ns)           | |
+-------------------------------------------------------+
```

### Why Containers Matter for Infrastructure & Systems Administration
- **Immutable Infrastructure:** Containers promote stateless, disposable deployments. Upgrades occur by replacing container instances rather than patching running hosts.
- **Resource Density & Speed:** Containers start in milliseconds and incur negligible CPU/RAM overhead compared to full guest OS kernels.
- **Environment Parity:** Eliminates the "works on my machine" problem across development, staging, and multi-cloud production hosts.
- **Security Isolation:** Restricts application impact during compromises via fine-grained kernel capabilities, seccomp filters, and namespace barriers.

---

## Under the Hood: Linux Kernel Primitives

Containers are not virtual machines or single binary objects; they are standard Linux processes running inside restricted kernel boundaries constructed from three primary primitives:

```
                  +-----------------------------------+
                  |         Linux Container           |
                  +-----------------------------------+
                  |  Namespaces (Isolation Boundary)  |
                  |  cgroups (Resource Controls)      |
                  |  OverlayFS (Copy-on-Write Storage)|
                  +-----------------------------------+
```

### 1. Linux Namespaces (Isolation Boundaries)
Namespaces wrap global system resources into isolated instances. A process within a namespace only sees resources assigned to that namespace.

| Namespace | Kernel Flag | Isolated Resource | Sysadmin Diagnostic Command |
|---|---|---|---|
| **PID** | `CLONE_NEWPID` | Process IDs & tree structure | `lsns -t pid` |
| **NET** | `CLONE_NEWNET` | Network devices, IP stacks, iptables | `ip netns list` / `ip link` |
| **MNT** | `CLONE_NEWMNT` | Mount points & filesystem hierarchy | `cat /proc/self/mountinfo` |
| **IPC** | `CLONE_NEWIPC` | System V IPC, POSIX message queues | `lsns -t ipc` |
| **UTS** | `CLONE_NEWUTS` | Hostname and NIS domain name | `hostname` |
| **USER** | `CLONE_NEWUSER`| UID/GID mappings (Rootless containers) | `cat /proc/uid_map` |
| **CGROUP**| `CLONE_NEWCGROUP`| Cgroup root directory view | `lsns -t cgroup` |

### 2. Control Groups (cgroups v1 vs cgroups v2)
Control Groups govern resource allocation, metering, and limiting for container process trees.

- **cgroups v1 (Legacy):** Multiple distinct resource controllers (`cpu`, `memory`, `blkio`) mounted in separate hierarchies under `/sys/fs/cgroup/`.
- **cgroups v2 (Unified Hierarchy):** A single unified tree under `/sys/fs/cgroup/` offering superior resource tracking, pressure stall information (PSI), and safe rootless delegation.

#### Essential cgroups v2 Files (`/sys/fs/cgroup/system.slice/docker-<ID>.scope/`):
```bash
# Inspect CPU memory allocation & limits
cat /sys/fs/cgroup/memory.max        # Max memory limit in bytes (or "max")
cat /sys/fs/cgroup/memory.current    # Current memory usage
cat /sys/fs/cgroup/cpu.max           # Quota and period (e.g., "200000 100000" = 2 CPUs)
```

### 3. Copy-on-Write (CoW) Storage: OverlayFS
Container images consist of stacked, read-only filesystem layers. When a container writes data, OverlayFS captures edits in a top-level ephemeral read-write layer without mutating base image layers.

```
+-------------------------------------------------------+
|  Container Read-Write Layer (upperdir)                |  <-- Ephemeral container edits
+-------------------------------------------------------+
|  Merged Directory View (merged)                       |  <-- Unified path seen by App
+-------------------------------------------------------+
|  Image Layer 2 (lowerdir)                             |  <-- Read-only base layer
+-------------------------------------------------------+
|  Image Layer 1 (lowerdir)                             |  <-- Read-only OS image layer
+-------------------------------------------------------+
```

---

## Container Architecture & The OCI Ecosystem

Modern container technology relies on open standards governed by the **Open Container Initiative (OCI)**:
1. **OCI Image Specification:** Defines image layout, layer formats, and manifest structure.
2. **OCI Runtime Specification:** Defines how to unpack and execute an OCI container bundle on Linux.

### The Container Runtime Stack
```
+-------------------------------------------------------+
| High-Level Orchestrator (Kubernetes / Docker Swarm)   |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
| Management Daemon / API (Docker Engine / Podman)     |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
| High-Level Container Runtime (containerd / CRI-O)     |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
| OCI Shim (containerd-shim-runc-v2)                    |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
| Low-Level OCI Runtime Engine (runc / crun)            |
+-------------------------------------------------------+
                           |
+-------------------------------------------------------+
| Linux Kernel (Namespaces, cgroups, Capabilities)      |
+-------------------------------------------------------+
```

### Docker vs Podman Architecture Comparison

| Feature | Docker Engine | Podman |
|---|---|---|
| **Architecture** | Client-Server Daemon (`dockerd`) | Daemonless (direct process execution) |
| **Privileges** | Traditionally root daemon required | Native Rootless by default |
| **Systemd Integration** | Managed via Docker service | Native systemd unit generation & Quadlets |
| **CLI Syntax** | `docker <command>` | `podman <command>` (drop-in alias compatible) |
| **Socket Dependency** | `/var/run/docker.sock` | Optional user socket (`unix:///run/user/1000/podman/podman.sock`) |

---

## Production-Grade Docker CLI Workflows

### Comprehensive Command Reference Matrix

| Category | Command | Description | Production Options |
|---|---|---|---|
| **Lifecycle** | `docker run` | Create & start a container | `-d`, `--restart=unless-stopped`, `--health-cmd` |
| **Lifecycle** | `docker stop` | Gracefully stop running container | `-t 30` (timeout before `SIGKILL`) |
| **Lifecycle** | `docker rm` | Remove stopped container | `-f` (force), `-v` (remove associated volumes) |
| **Inspection** | `docker ps` | List containers | `-a` (all), `--filter "status=exited"`, `--format` |
| **Inspection** | `docker inspect` | Output low-level JSON details | `--format '{{.State.Health.Status}}'` |
| **Inspection** | `docker logs` | Retrieve container stdout/stderr | `-f` (follow), `--tail 100`, `--timestamps` |
| **Execution** | `docker exec` | Execute command in running container | `-it` (interactive tty), `-u root` |
| **Storage** | `docker volume` | Manage persistent volumes | `create`, `ls`, `inspect`, `prune` |
| **Networking**| `docker network` | Manage container networks | `create --driver bridge`, `connect`, `ls` |
| **Maintenance**| `docker system` | Manage Docker disk space | `prune -a --volumes` (reclaim dead resources) |

### Advanced Production CLI Examples

```bash
# 1. Start a production Nginx container with resource limits, security flags, and health checks
docker run -d \
  --name web-prod \
  --restart unless-stopped \
  --cpus="1.5" \
  --memory="512m" \
  --memory-swap="512m" \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --tmpfs /var/cache/nginx:rw,noexec,nosuid \
  --tmpfs /var/run:rw,noexec,nosuid \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --security-opt=no-new-privileges:true \
  --health-cmd="curl -f http://localhost/ || exit 1" \
  --health-interval=10s \
  --health-retries=3 \
  --health-timeout=5s \
  -p 80:80 \
  nginx:alpine-slim

# 2. Inspect container resource consumption dynamically
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# 3. Extract specific JSON metadata using formatted templates
docker inspect --format '{{.Name}} -> IP: {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web-prod

# 4. Stream real-time container logs with timestamps and filtering
docker logs -f --timestamps --tail 200 web-prod

# 5. Clean up unused resources safely (containers, networks, images, and cache)
docker system prune --all --volumes --force
```

---

## Dockerfile Deep Dive & Multi-Stage Optimization

A `Dockerfile` is an automated build script defining step-by-step instructions to create an OCI container image. Writing optimized Dockerfiles reduces attack surface area, minimizes storage footprints, and speeds up CI/CD pipelines.

### Multi-Stage Build Pattern (Go Web Service Example)

```dockerfile
# ==========================================
# STAGE 1: Build Environment (Heavy Toolchain)
# ==========================================
FROM golang:1.22-alpine AS builder

# Set mandatory build flags and working directory
ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

WORKDIR /build

# Optimize layer caching by copying go.mod and downloading dependencies first
COPY go.mod go.sum ./
RUN go mod download && go mod verify

# Copy source code and compile statically linked binary
COPY . .
RUN go build -ldflags="-w -s" -o server ./cmd/server

# ==========================================
# STAGE 2: Minimal Production Runtime
# ==========================================
FROM alpine:3.19 AS runner

# Install security certificates and add a non-root system user/group
RUN apk add --no-cache ca-certificates tzdata && \
    addgroup -S -g 10001 appgroup && \
    adduser -S -u 10001 -G appgroup -h /app appuser

WORKDIR /app

# Copy compiled binary from builder stage
COPY --from=builder --chown=appuser:appgroup /build/server /app/server

# Enforce Security & Non-Root Execution
USER 10001:10001

# Expose target port
EXPOSE 8080

# Health check configuration
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD ["/app/server", "-healthcheck"]

# Entry point execution
ENTRYPOINT ["/app/server"]
```

### Dockerfile Hardening & Optimization Rules
1. **Never Run as Root:** Explicitly create an unprivileged system user (`USER 10001:10001`).
2. **Use Minimal Base Images:** Prefer `alpine`, `distroless`, or `scratch` over bloated `ubuntu` or `debian` bases.
3. **Minimize Layers:** Combine related `RUN` commands using `&&` and clean cache directories within the same step (e.g., `apt-get clean && rm -rf /var/lib/apt/lists/*`).
4. **Leverage `.dockerignore`:** Exclude local binaries, `.git` repositories, environment files (`.env`), and node modules from build contexts.

#### Example `.dockerignore`:
```ignore
.git
.gitignore
Dockerfile
docker-compose*.yml
.env
*.log
dist/
node_modules/
```

---

## Docker Compose for Multi-Container Infrastructure

Docker Compose orchestrates multi-container applications, defining services, persistent storage volumes, secret management, and custom network topologies inside a declarative YAML specification (`docker-compose.yml`).

### Production Architecture Stack (Nginx + Python Web App + PostgreSQL)

```yaml
version: '3.8'

services:
  # -------------------------------------------------------------
  # Frontend / Reverse Proxy Service
  # -------------------------------------------------------------
  proxy:
    image: nginx:1.25-alpine
    container_name: prod_proxy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - cert_data:/etc/letsencrypt:ro
    networks:
      - frontend_net
    depends_on:
      app:
        condition: service_healthy
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # -------------------------------------------------------------
  # Backend Web Application Service
  # -------------------------------------------------------------
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: prod_backend
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - DB_HOST=db
      - DB_PORT=5432
      - DB_NAME=${POSTGRES_DB:-app_db}
      - DB_USER=${POSTGRES_USER:-app_user}
      - DB_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    networks:
      - frontend_net
      - backend_net
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s
    depends_on:
      db:
        condition: service_healthy

  # -------------------------------------------------------------
  # Database Service (Isolated Network)
  # -------------------------------------------------------------
  db:
    image: postgres:16-alpine
    container_name: prod_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-app_db}
      POSTGRES_USER: ${POSTGRES_USER:-app_user}
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend_net
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 1G
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-app_user} -d ${POSTGRES_DB:-app_db}"]
      interval: 5s
      timeout: 3s
      retries: 5

# -------------------------------------------------------------
# Storage Volume Definitions
# -------------------------------------------------------------
volumes:
  postgres_data:
    driver: local
  cert_data:
    driver: local

# -------------------------------------------------------------
# Network Topology Definitions
# -------------------------------------------------------------
networks:
  frontend_net:
    driver: bridge
    internal: false
  backend_net:
    driver: bridge
    internal: true  # Prevents external egress/ingress directly to DB

# -------------------------------------------------------------
# Secrets Definitions
# -------------------------------------------------------------
secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### Essential Docker Compose CLI Commands
```bash
# Validate and render active Compose configuration
docker compose config

# Build images and launch entire stack in background
docker compose up -d --build

# View real-time log outputs across all services
docker compose logs -f --tail=100 app

# Scale backend application instances dynamically
docker compose up -d --scale app=3

# Gracefully stop stack and purge network infrastructure
docker compose down --remove-orphans
```

---

## Container Networking & Storage Architecture

### Container Network Drivers

```
+-----------------------------------------------------------------------+
| BRIDGE DRIVER (Default)                                               |
| Host Interface (eth0) <--> iptables NAT <--> docker0 <--> veth <--> App|
+-----------------------------------------------------------------------+
| HOST DRIVER                                                           |
| Container directly binds to Host Interface (eth0) (No port isolation)|
+-----------------------------------------------------------------------+
| MACVLAN / IPVLAN DRIVER                                               |
| Assigns unique MAC/IP directly on physical LAN subnet                |
+-----------------------------------------------------------------------+
```

1. **Bridge (`bridge`):** Creates a virtual software bridge (`docker0` or custom) on the host. Containers receive private IPs (`172.17.0.0/16`) and use `iptables` NAT rules for external access.
2. **Host (`host`):** Bypasses container network isolation. The container directly uses host interfaces and ports.
3. **None (`none`):** Disables networking entirely; container has only a loopback interface (`lo`).
4. **Macvlan / Ipvlan:** Assigns a MAC address directly to container interfaces, making them appear as physical nodes on your LAN.

#### Inspecting Low-Level Network Interfaces:
```bash
# List Linux bridge devices
ip link show type bridge

# Inspect active iptables NAT rules managed by Docker
sudo iptables -t nat -L DOCKER -n -v
```

### Storage Patterns: Volumes vs Bind Mounts vs Tmpfs

```
+--------------------------------------------------------------------+
| Docker Host Filesystem                                             |
|                                                                    |
|  /var/lib/docker/volumes/  <--> [ Named Volume ] (Managed by Engine)|
|  /home/user/project/conf   <--> [ Bind Mount ]   (Host Dependent)  |
|  Host RAM / Swap Memory    <--> [ Tmpfs Mount ]  (In-Memory Only)  |
+--------------------------------------------------------------------+
```

| Type | Target Path | Managed By | Use Case |
|---|---|---|---|
| **Named Volume** | `/var/lib/docker/volumes/<name>/_data` | Docker Engine | Databases, persistent app state |
| **Bind Mount** | Arbitrary host path (e.g. `/etc/nginx`) | Administrator | Development code hot-reloading, host configs |
| **Tmpfs** | Mounts directly in host RAM | Host Kernel | Ephemeral secrets, non-persistent cache |

---

## Production Security Hardening & Daemon Configuration

### Production `/etc/docker/daemon.json` Configuration
To secure Docker in enterprise production environments, configure `/etc/docker/daemon.json`:

```json
{
  "userns-remap": "default",
  "live-restore": true,
  "no-new-privileges": true,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "20m",
    "max-file": "5",
    "compress": "true"
  },
  "storage-driver": "overlay2",
  "icc": false,
  "userland-proxy": false,
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64535,
      "Soft": 32768
    }
  }
}
```

- **`live-restore`:** Keeps containers running even if the Docker daemon restarts or crashes.
- **`userns-remap`:** Maps container root UID `0` to an unprivileged UID on the host.
- **`icc: false`:** Disables inter-container communication on the default bridge network unless explicitly linked.
- **`userland-proxy: false`:** Passes container traffic via iptables rules directly, avoiding memory overhead from userland proxies.

---

## Comprehensive Troubleshooting Matrix

| Symptom / Error | Root Cause | Immediate Diagnostic Command | Resolution Strategy |
|---|---|---|---|
| **Container exits immediately with `Exit 0`** | Container PID 1 process completed or detached from standard input | `docker logs <container_id>` | Ensure entrypoint process runs in foreground (e.g., `nginx -g 'daemon off;'` instead of background daemon). |
| **Container terminated with `Exit 137`** | Out Of Memory (OOM) Killer terminated the container process | `docker inspect <id> --format '{{.State.OOMKilled}}'` | Increase container RAM limit (`--memory`), fix memory leaks, or adjust host swap limits. |
| **Port binding failure (`address already in use`)** | Another host process or container is listening on the target host port | `sudo ss -tulnp \| grep :<port>` | Identify blocking process PID, stop conflicting service, or assign alternative host port mapping. |
| **Storage full: Host disk at 100%** | Unrotated container stdout/stderr logs or dangling images accumulated | `docker system df -v` | Execute `docker system prune -a --volumes` and configure log size caps in `/etc/docker/daemon.json`. |
| **Permission Denied on mounted volume** | Host directory permissions do not align with internal container UID/GID | `ls -ld /path/to/host/dir` | Run `chown -R 10001:10001 /path/to/host/dir` matching container unprivileged `USER`. |
| **DNS Resolution Fails inside container** | Invalid `/etc/resolv.conf` or blocked outbound UDP port 53 traffic | `docker exec -it <id> nslookup google.com` | Override container DNS via `--dns 8.8.8.8` flag or verify host firewall iptables rules. |

---

## Hands-On Production Labs

### Lab 1: Multi-Stage Production Build & Hardening
**Objective:** Create a secure, non-root, minimal container image from source code with embedded health checks.

```bash
# Step 1: Create a workspace directory
mkdir -p ~/container-lab1 && cd ~/container-lab1

# Step 2: Create a lightweight Go HTTP server script
cat << 'EOF' > main.go
package main

import (
	"fmt"
	"net/http"
	"os"
)

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Infrastructure Lab 1: Serving securely from non-root container!\n")
	})

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	fmt.Printf("Server listening on port %s...\n", port)
	http.ListenAndServe(":"+port, nil)
}
EOF

# Step 3: Write the multi-stage Dockerfile
cat << 'EOF' > Dockerfile
FROM golang:1.22-alpine AS build
WORKDIR /app
COPY main.go .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o webserver main.go

FROM alpine:3.19
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app
COPY --from=build --chown=appuser:appgroup /app/webserver /app/
USER appuser
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=2s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1
ENTRYPOINT ["/app/webserver"]
EOF

# Step 4: Build and test the hardened image
docker build -t micro-web:v1.0 .

# Step 5: Run with read-only root filesystem and cap drop
docker run -d \
  --name lab1-container \
  -p 8080:8080 \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges:true \
  micro-web:v1.0

# Step 6: Verification
curl http://localhost:8080
docker inspect --format '{{.State.Health.Status}}' lab1-container
docker top lab1-container
```

---

### Lab 2: Multi-Tier Isolated Infrastructure with Docker Compose
**Objective:** Deploy Nginx, Python Web App, and PostgreSQL with strict network segmentation.

```bash
# Step 1: Create project directory
mkdir -p ~/container-lab2/nginx ~/container-lab2/secrets && cd ~/container-lab2

# Step 2: Store database password secret securely
echo "SuperSecretPass123!" > secrets/db_password.txt
chmod 600 secrets/db_password.txt

# Step 3: Write Nginx custom configuration
cat << 'EOF' > nginx/nginx.conf
events { worker_connections 1024; }
http {
    server {
        listen 80;
        location / {
            proxy_pass http://app:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

# Step 4: Write Docker Compose file
cat << 'EOF' > docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "8082:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - public_net
    depends_on:
      - app

  app:
    image: python:3.11-slim
    command: python -c "import http.server; http.server.test(HandlerClass=http.server.SimpleHTTPRequestHandler, port=8080)"
    networks:
      - public_net
      - private_net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080"]
      interval: 5s
      timeout: 3s
      retries: 3

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass
      POSTGRES_DB: appdb
    secrets:
      - db_pass
    networks:
      - private_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

secrets:
  db_pass:
    file: ./secrets/db_password.txt

networks:
  public_net:
    driver: bridge
  private_net:
    driver: bridge
    internal: true
EOF

# Step 5: Start the infrastructure stack
docker compose up -d

# Step 6: Verify network isolation (App can reach DB, but DB cannot egress to Internet)
docker compose exec db ping -c 2 google.com || echo "Isolated backend successfully blocked public egress!"
```

---

### Lab 3: Deep Kernel Inspection of Container Namespaces & Cgroups
**Objective:** Inspect native Linux namespaces and cgroup constraints using core system administration commands.

```bash
# Step 1: Run an isolated background container
docker run -d --name kernel-demo --cpus="0.5" --memory="128m" alpine sleep 3600

# Step 2: Get the host PID of the container's PID 1 process
HOST_PID=$(docker inspect --format '{{.State.Pid}}' kernel-demo)
echo "Container Process Host PID: $HOST_PID"

# Step 3: Inspect active namespaces associated with the PID
sudo lsns -p $HOST_PID

# Step 4: Execute commands inside the container's namespace directly from the host
sudo nsenter --target $HOST_PID --net ip addr show
sudo nsenter --target $HOST_PID --pid ps aux

# Step 5: Inspect cgroup v2 limits assigned to this container
CGROUP_PATH=$(cat /proc/$HOST_PID/cgroup | cut -d: -f3)
echo "Cgroup relative path: $CGROUP_PATH"
cat /sys/fs/cgroup${CGROUP_PATH}/memory.max
cat /sys/fs/cgroup${CGROUP_PATH}/cpu.max

# Clean up
docker rm -f kernel-demo
```

---

### Lab 4: Daemonless & Rootless Operations with Podman
**Objective:** Execute rootless containers and integrate them with systemd services.

```bash
# Step 1: Ensure Podman is available (or install via package manager)
podman --version

# Step 2: Run a rootless web container as standard user
podman run -d --name rootless-web -p 8085:8080 micro-web:v1.0

# Step 3: Verify execution user context inside container
podman top rootless-web user huser

# Step 4: Generate a systemd unit file for the container
mkdir -p ~/.config/systemd/user/
podman generate systemd --name rootless-web --files --new --workdir ~/.config/systemd/user/

# Step 5: Manage container service with systemctl
systemctl --user daemon-reload
podman stop rootless-web
systemctl --user start container-rootless-web.service
systemctl --user status container-rootless-web.service

# Clean up
systemctl --user stop container-rootless-web.service
podman rm -f rootless-web
```

---

### Lab 5: Automated Log Management & Incident Response
**Objective:** Troubleshoot an Out-Of-Disk emergency caused by container logs and recover service state.

```bash
# Step 1: Simulate a container emitting aggressive logs
docker run -d --name noisy-app alpine sh -c "while true; do echo 'CRITICAL_ERROR: Memory leak at offset 0x992384' >> /var/log/app.log; echo 'Log spamming...'; done"

# Step 2: Locate the container's log file on the host filesystem
LOG_PATH=$(docker inspect --format '{{.LogPath}}' noisy-app)
echo "Active Container Log Path: $LOG_PATH"
ls -lh $LOG_PATH

# Step 3: Truncate the log file to reclaim host disk space safely
sudo truncate -s 0 $LOG_PATH
echo "Reclaimed disk space without killing container process."

# Step 4: Configure automated log truncation in docker-compose or daemon.json
# Clean up
docker rm -f noisy-app
```

---

## Self-Check & Verification Checklist

- [ ] Can you explain the fundamental architectural difference between Virtual Machines and Linux Containers?
- [ ] Can you detail how `namespaces`, `cgroups`, and `OverlayFS` collaborate to instantiate a container?
- [ ] Can you write a secure multi-stage Dockerfile that drops `root` privileges and builds a sub-20MB image?
- [ ] Can you configure a multi-tier `docker-compose.yml` stack with health checks, resource constraints, and isolated networks?
- [ ] Can you inspect low-level container namespaces using `nsenter` and `lsns`?
- [ ] Can you configure `/etc/docker/daemon.json` for production security (live-restore, log rotation, userns-remap)?
- [ ] Can you diagnose container start failures, OOM kills (`Exit 137`), port conflicts, and log disk exhaustion?

---

## Progress Tracker

- [x] Executive Summary & Fundamentals
- [x] Kernel Primitives: Namespaces, cgroups v2, & OverlayFS
- [x] OCI Standards & Container Runtime Stack
- [x] Production Docker CLI Workflows
- [x] Multi-Stage Dockerfile Optimization & Hardening
- [x] Multi-Tier Docker Compose Deployment
- [x] Networking & Storage Deep Dive
- [x] Production Security & Daemon Hardening
- [x] Comprehensive Troubleshooting Matrix
- [x] Hands-On Labs 1 through 5 Completed

---

## Recommended Resources & Further Study

1. **Docker Engine Official Manual:** https://docs.docker.com/engine/
2. **Open Container Initiative (OCI) Specifications:** https://opencontainers.org/
3. **Podman Documentation:** https://docs.podman.io/
4. **OCI Image & Runtime Specification GitHub:** https://github.com/opencontainers/runtime-spec
5. **Red Hat Container Guide (cgroups v2 & namespaces):** https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9
6. **Container Security Guide (NIST SP 800-190):** https://csrc.nist.gov/publications/detail/sp/800-190/final

---

## Next Topic
→ [[09 - CI]]
