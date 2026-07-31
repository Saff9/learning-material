# 08 - Containers

> **Phase:** 1 (Core Linux) · **Time:** ~4 weeks · **Difficulty:** ⭐⭐⭐⭐

## What it is
**Containers** allow you to package an application, its dependencies, and its environment into a single, portable unit that runs reliably across different environments (local dev, CI, cloud). The most popular container runtime on Linux is **Docker**, plus emerging alternatives like **Podman** (daemon‑less), **Containerd** (low‑level runtime), and **CRI‑O**.

Containers share the host kernel, making them lightweight compared to virtual machines (VMs), which require full OS layers.

## Why it matters
- **Consistency:** Works identically from dev to production.
- **Speed:** Seconds to deploy.
- **Isolation:** Application boundaries, resource limits.
- **DevOps enablement:** CI/CD pipelines, orchestration (Kubernetes), multi‑cloud deployments.
- **Cost‑effective:** Fewer servers needed.

## Core concepts — detailed

### 1. Docker architecture
```
+----------------------+     +-------------------+
|   Docker Client CLI  | --> | Docker Daemon API  |
+----------------------+     +-------------------+
         |                           |
   +-----------+    +-------------------+    +------------------+
   | Images     |    | Container         |    | Filesystem       |
   | +-------+ |    | +---------------+ |    | +--------------+
   | | Layers | |    | | Process Tree   | |    | | Read‑Only      |
   | | etc   | |    | | Exec driver    | |    | | Layers        |
   | +-------+ |    | +---------------+ |    +--------------+
   +-----------+    +-------------------+
```

- **Image** = layered filesystem (read‑only, cached). Each change (RUN, COPY, ADD) creates a new layer.
- **Container** = runtime instance of an image (read/write layers on top of image).
- **Dockerfile** = script defining how to build an image.

### 2. Docker workflow commands
| Command | What it does |
|---|---|
| `docker build -t <image> <path>` | Build image from Dockerfile |
| `docker run [options] <image>` | Create and start a container |
| `docker run -d` | Detach (background) mode |
| `docker ps` | List running containers |
| `docker exec -it <container> <cmd>` | Run command inside a container |
| `docker logs <container>` | Show container stdout/stderr |
| `docker attach <container>` | Attach terminal to running container |
| `docker stop <container>` | Stop a running container |
| `docker rm <container>` | Remove stopped containers |
| `docker rmi <image>` | Remove an image |
| `docker images` | List local images |

### 3. Docker Compose (multi‑container apps)
- YAML file (`docker-compose.yml`) defines services, networks, volumes.
- `docker compose up -d` → builds + starts all services.
- `docker compose down` → stops and removes containers, networks, images (if `--rmi all`).

### 4. Container security and isolation
- **User namespace mapping** (`--user`).
- **Read‑only root filesystem** (`--read‑only`).
- **Capabilities** (`--cap‑drop`).
- **Resource limits** (`--cpus`, `--memory`).
- **Volumes**: named volumes (`-v`) for persistent data.
- **Docker socket injection** (`-v /var/run/docker.sock`) for tool integration (caution: less secure).

### 5. Podman alternatives
- **Podman**: daemon‑less, rootless, OCI compliant.
- **Buildah**: build images without runtime.
- **Skopeo**: copy images between registries.
- **MRI (Multi‑arch Image)**: use `docker manifest` for multi‑arch support.

## Free resources — curated for self‑learners

1. **Docker Official Docs:** https://docs.docker.com/engine/
2. **Docker Compose Spec:** https://docs.docker.com/compose/compose-file/
3. **Kubernetes Docs (if interested):** https://kubernetes.io/docs/home/
4. **Linux Foundation: Containers for Everybody (free e‑book):** https://training.linuxfoundation.org/resources/containers-for-everybody/
5. **Docker Hub:** https://hub.docker.com/ (public registry of images)
6. **Container Journal:** https://containerjournal.net/ (articles, news)
7. **Dockerize Python:** https://dockerizing-python.readthedocs.io/ (specific to Python apps)

## Practice labs (run in any environment that supports Docker: local, WSL2, cloud)

### Lab 1: Hello‑world container
```bash
# Pull the official Nginx image (or use a simple busybox)
sudo docker pull nginx:alpine

# Run a container exposing port 80
sudo docker run -d -p 8080:80 --name web nginx:alpine

# Verify
ps aux | grep nginx
sudo netstat -tulnp | grep 8080
```

### Lab 2: Docker Compose setup
```bash
# Create a docker-compose.yml
cat > docker-compose.yml <<EOF
services:
  web:
    image: httpd:alpine
    ports:
      - "8081:80"
    volumes:
      - ./html:/usr/local/apache2/htdocs
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
EOF

# Build and start containers
sudo docker compose up -d

# List containers
sudo docker ps
```

### Lab 3: Dockerfile build
```bash
# Create a simple Dockerfile
cat > Dockerfile <<EOF
FROM alpine:latest
RUN apk add --no-cache bash
COPY script.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/script.sh
CMD ["/usr/local/bin/script.sh"]
EOF

# Create a dummy script
cat > script.sh <<EOF
#!/bin/bash
echo "Hello from inside container"
sleep 3600
EOF

# Build image
sudo docker build -t myapp .

# Run container
sudo docker run -d --name myapp-container myapp

# Inspect image layers
sudo docker history myapp
```

### Lab 4: Volumes for persistence
```bash
# Create a named volume
sudo docker volume create mydata

# Mount it in a container
sudo docker run -d -v mydata:/data --name data-container alpine sh -c "while true; echo data >> /data/log.txt; sleep 5"

# Check contents inside the volume (via another container)
sudo docker run -it --volumes-from data-container alpine cat /data/log.txt
```

### Lab 5: Security best practices
```bash
# Run container with reduced capabilities
sudo docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE -p 80:80 nginx:alpine

# Use a read‑only root filesystem (requires Docker 20.10+)
sudo docker run --read-only --tmpfs /run myapp:latest
```

## Self‑check (can you…)
- [ ] Explain the difference between Docker image and container
- [ ] Build an image from a Dockerfile and run it
- [ ] Use `docker compose` to orchestrate a multi‑service app
- [ ] Use volumes for data persistence across container restarts
- [ ] Secure a container with capabilities, read‑only FS, and non‑root user
- [ ] List, start, stop, and inspect containers

## Progress
- [ ] Created and ran a basic container (Hello‑world)
- [ ] Set up a Docker Compose multi‑service stack
- [ ] Built an image from a Dockerfile and tested it
- [ ] Used named volumes for persistent data
- [ ] Configured a container with security best practices

## Next
→ [[09 - CI]]
