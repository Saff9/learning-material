# 09 - Continuous Integration & Continuous Delivery (CI/CD) Infrastructure

> **Phase:** 1 (Core Linux & Systems Infrastructure) · **Time:** ~3 weeks · **Difficulty:** ⭐⭐⭐⭐

---

## Executive Summary & Architectural Overview

**Continuous Integration (CI)** is the foundational software engineering and systems practice of automatically compiling, testing, linting, and validating code changes whenever developers push updates to a central version control system (VCS) like Git. **Continuous Delivery / Continuous Deployment (CD)** extends CI by automatically packaging, staging, verifying, and releasing validated build artifacts directly into target infrastructure (e.g., Kubernetes clusters, cloud Virtual Machines, or bare-metal servers).

From a **Linux Systems Administrator and Infrastructure Engineer** perspective, CI/CD is not merely a software developer tool—it is a critical, high-throughput compute workload running on enterprise Linux infrastructure. CI runners execute arbitrary code, spawn transient containers, pull down vast network assets, consume CPU/RAM bursts, and require strict security isolation, network policies, storage management, and access controls.

```
+---------------------------------------------------------------------------------------------------+
|                                      CI/CD PIPELINE ARCHITECTURE                                  |
+---------------------------------------------------------------------------------------------------+

 Developers                     VCS Server (Git)                   CI Orchestrator / Controller
+----------+                   +------------------+                +--------------------------+
| Dev Work |  Git Push         |  GitHub / GitLab |  Webhook Event |  GitHub Actions Manager  |
| Station  | ----------------> |  Bitbucket /     | -------------> |  GitLab Server /         |
+----------+                   |  Self-Hosted Git |                |  Jenkins Master          |
                               +------------------+                +--------------------------+
                                                                                 |
                                                                   Assign Job to | Runner Pool
                                                                                 v
+---------------------------------------------------------------------------------------------------+
| LINUX RUNNER INFRASTRUCTURE POOL (Ephemeral Container / VM Nodes)                                  |
|                                                                                                   |
|  +---------------------------+  +---------------------------+  +-------------------------------+  |
|  | Runner 01 (Docker)        |  | Runner 02 (Docker)        |  | Runner N (Bare-Metal/K8s)     |  |
|  | - Checkout Code           |  | - Security Scan (Trivy)   |  | - Build Container Image       |  |
|  | - Lint & Unit Tests       |  | - SAST & Secret Audit     |  | - Sign Artifact (Cosign)      |  |
|  +---------------------------+  +---------------------------+  +-------------------------------+  |
+---------------------------------------------------------------------------------------------------+
           |                                   |                                   |
           v                                   v                                   v
+-----------------------+           +-----------------------+           +---------------------------+
| Artifact Cache        |           | Vulnerability Reports |           | Container Registry        |
| (MinIO / S3 Bucket)   |           | (Security Dashboard)  |           | (Harbor / GHCR / ECR)     |
+-----------------------+           +-----------------------+           +---------------------------+
                                                                                   |
                                                                     Automated     v
                                                                     Deploy  +-------------------+
                                                                             | Staging / Prod K8s|
                                                                             +-------------------+
```

### CI/CD Platform Comparative Analysis Matrix

| Feature / Metric | GitHub Actions | GitLab CI/CD | Jenkins | Drone / Tekton |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Architecture** | Cloud-managed controller + hosted/self-hosted runners | Integrated SaaS/Self-Hosted controller + runners | Self-hosted Controller/Agent model (Java-based) | Cloud-Native / Kubernetes CRD native execution |
| **Configuration Syntax** | YAML (`.github/workflows/*.yml`) | YAML (`.gitlab-ci.yml`) | Groovy DSL (`Jenkinsfile`) | YAML / Kubernetes Manifests |
| **Default Execution Context** | Ephemeral VMs / Docker containers | Docker-in-Docker (dind), Shell, K8s executor | Shared agents / Docker sidecars / K8s pods | Ephemeral Kubernetes Pods per step |
| **Caching Mechanism** | Action-based artifact & cache stores | Native path & S3-compatible object cache | Workspace persistence & plugin caches | S3/GCS volume plugins & persistent volumes |
| **Self-Hosting Complexity** | Low (Single binary runner process) | Low-Medium (`gitlab-runner` service) | High (Master node management, plugin updates) | Medium-High (Requires K8s cluster management) |
| **Enterprise Best For** | GitHub-native codebases & public/private SaaS | Integrated DevOps platforms & self-hosted Git | Legacy workflows, deep custom toolchain hooks | Native Kubernetes GitOps pipelines |

---

## Core Concepts & Pipeline Mechanics

### 1. Pipeline Lifecycle & Component Topology

Every modern CI workflow follows a deterministic state transition lifecycle triggered by events:

```
[ Git Event ] ──> [ Webhook Dispatch ] ──> [ Job Scheduler ] ──> [ Runner Provisioning ]
                                                                       │
[ Artifact Release ] <── [ Security Gate ] <── [ Build & Test ] <── [ Workspace Checkout ]
```

- **Event Triggers**: Push to branch, Pull Request state change, Git Tag creation, scheduled Cron schedule (`schedule`), or manual API call (`workflow_dispatch`).
- **Jobs & Parallelism**: Independent pipeline execution blocks. By default, jobs execute in parallel unless explicitly bounded by dependency DAGs (`needs:` or `dependencies:`).
- **Steps**: Sequential command execution units inside a single job. Steps run on the exact same runner shell context or container environment, sharing local workspace state.
- **Workspaces & Persistence**: Temporary directories where source code is fetched. Workspaces are non-persistent by default across separate jobs; state must be explicitly saved via **Artifacts** or **Caches**.

### 2. Execution Contexts & Runner Isolation Models

Selecting the runner execution model impacts security isolation, build performance, and infrastructure costs:

1. **Bare-Metal / Host Shell Executor**:
   - *Mechanics*: Executes commands directly on the runner host operating system under a specific Linux user account.
   - *Pros*: Highest execution speed, raw I/O performance, direct access to host GPU/hardware.
   - *Cons*: High security risk of host compromise; build pollution across jobs (leftover files, modified system packages).
2. **Container Executor (Docker / Podman)**:
   - *Mechanics*: Each job runs inside a freshly instantiated container image (e.g., `ubuntu:22.04` or custom tooling images).
   - *Pros*: Completely isolated environment, reproducible dependency set, clean state guaranteed.
   - *Cons*: Minor container startup latency; requires Docker daemon access or Docker-in-Docker setup.
3. **Kubernetes Ephemeral Executors**:
   - *Mechanics*: The CI controller dynamically requests a Kubernetes Pod for each pipeline job via the K8s API. Pod terminates immediately on job completion.
   - *Pros*: Infinite horizontal scalability, zero idle compute costs, strong namespace isolation.
   - *Cons*: Network latency for pulling large container images; requires dedicated K8s cluster management.

### 3. Caching Strategies & Optimization Mechanics

Build speed is heavily dependent on caching strategies. Infrastructure engineers must distinguish between three distinct storage layers:

- **Dependency Caches (`actions/cache`, GitLab Cache)**: Stores downloaded package archives (e.g., `~/.cache/pip`, `node_modules/`, `~/.m2/repository`). Caches are keyed by content hashes of lockfiles (e.g., `package-lock.json`, `requirements.txt`).
- **Docker Layer Caching (BuildKit / Registry Inline Cache)**: Caching intermediate container build steps using flags like `--cache-from` and `--cache-to type=inline` or `type=registry`. Prevents re-downloading base layers and re-compiling unchanged layers.
- **Build Artifacts**: Immutable outputs (compiled binaries, tarballs, test logs) generated by one pipeline stage and consumed by downstream stages or exported for deployment.

### 4. DevSecOps Security Gates & Supply Chain Protection

Modern CI pipelines act as enforcement gates for organizational security policies:

```
Source Code ──> [ Secret Scan (Gitleaks) ] ──> [ SAST (Bandit/Semgrep) ] ──> [ Container Scan (Trivy) ] ──> [ SBOM (Syft) ] ──> Release
```

- **Secret Detection**: Scanning commit deltas for exposed API keys, SSH private keys, and passwords using tools like `gitleaks` or `trufflehog`.
- **Static Application Security Testing (SAST)**: Analyzing source code without execution to identify injection flaws, memory safety issues, and insecure library calls.
- **Software Bill of Materials (SBOM)**: Generating structural manifests listing every dependency, component, and library packaged into a build artifact using tools like `syft`.
- **Container Vulnerability Scanning**: Inspecting built base images for known Common Vulnerabilities and Exposures (CVEs) using `trivy` or `grype`.

---

## Production Configurations & Multi-Platform Blueprints

### 1. Enterprise GitHub Actions Workflow

Below is a production-grade, hardened GitHub Actions pipeline (`.github/workflows/production-pipeline.yml`). It features dependency caching, static security scanning, multi-version unit testing, containerized vulnerability enforcement, and image publishing.

```yaml
# .github/workflows/production-pipeline.yml
# Production-grade GitHub Actions CI/CD Pipeline
name: Enterprise Production Pipeline

on:
  push:
    branches: [ "main", "release/*" ]
    tags: [ "v*.*.*" ]
  pull_request:
    branches: [ "main" ]

# Grant minimal permissions to the automatically generated GITHUB_TOKEN
permissions:
  contents: read
  packages: write
  id-token: write

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ---------------------------------------------------------------------------
  # STAGE 1: Code Linting & Static Security Analysis (SAST)
  # ---------------------------------------------------------------------------
  lint-and-security:
    name: Code Quality & Security Audit
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Full history required for secret git history scanning

      - name: Set up Python Environment
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Restore Pip Dependency Cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install Linting & Security Tools
        run: |
          python -m pip install --upgrade pip
          pip install flake8 black bandit gitleaks

      - name: Execute Secret Scan (Gitleaks)
        run: |
          echo "==> Auditing repository for leaked credentials..."
          # Scan repository and fail if hardcoded secrets exist
          gitleaks detect --source . --verbose

      - name: Run Code Style Checks
        run: |
          echo "==> Verifying Python syntax and PEP8 formatting..."
          black --check .
          flake8 . --max-line-length=88 --ignore=E203,W503

      - name: Run SAST Vulnerability Analysis (Bandit)
        run: |
          echo "==> Running Static Security Testing on Python code..."
          bandit -r ./src -ll -ii

  # ---------------------------------------------------------------------------
  # STAGE 2: Automated Unit Testing across Matrix Matrix
  # ---------------------------------------------------------------------------
  unit-test:
    name: Unit Tests (Python ${{ matrix.python-version }})
    needs: lint-and-security
    runs-on: ubuntu-latest
    strategy:
      fail-fast: true
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Restore Pip Cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-test-${{ matrix.python-version }}-${{ hashFiles('**/requirements*.txt') }}

      - name: Install Application Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Execute Pytest Suite with Coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term-missing tests/

      - name: Upload Test Coverage Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: test-coverage-py${{ matrix.python-version }}
          path: coverage.xml
          retention-days: 7

  # ---------------------------------------------------------------------------
  # STAGE 3: Container Image Build, Vulnerability Scan, & Package Publish
  # ---------------------------------------------------------------------------
  build-and-publish:
    name: Build Docker Image & Security Scan
    needs: unit-test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v'))

    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry (GHCR)
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Docker Metadata & Tags
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=semver,pattern={{version}}
            type=sha,format=long
            type=ref,event=branch

      - name: Build Container Image locally for Security Scan
        uses: docker/build-push-action@v5
        with:
          context: .
          load: true # Load image into local Docker engine daemon
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:local-scan
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run Trivy Vulnerability Scan on Built Image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:local-scan
          format: 'table'
          exit-code: '1' # Fail pipeline if CRITICAL vulnerabilities exist
          ignore-unfixed: true
          severity: 'CRITICAL,HIGH'

      - name: Push Container Image to Registry
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

### 2. Enterprise GitLab CI Pipeline

The following `.gitlab-ci.yml` file provides a complete multi-stage pipeline utilizing Docker-in-Docker, native dependency caching, artifact retention, and environment-based deployments.

```yaml
# .gitlab-ci.yml
# Production GitLab CI Pipeline for Containerized Microservices

stages:
  - lint
  - test
  - build
  - security
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  RELEASE_TAG: $CI_REGISTRY_IMAGE:latest

# Shared cache rule across python jobs
cache:
  key: "${CI_COMMIT_REF_SLUG}-pip"
  paths:
    - .cache/pip/
    - venv/

# Default base docker image for python jobs
default:
  image: python:3.11-slim

# -----------------------------------------------------------------------------
# STAGE: LINT
# -----------------------------------------------------------------------------
lint:python:
  stage: lint
  before_script:
    - python -m venv venv/
    - source venv/bin/activate
    - pip install --upgrade pip
    - pip install flake8 black
  script:
    - black --check .
    - flake8 . --max-line-length=88

# -----------------------------------------------------------------------------
# STAGE: TEST
# -----------------------------------------------------------------------------
test:unittest:
  stage: test
  before_script:
    - python -m venv venv/
    - source venv/bin/activate
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
  script:
    - pytest --cov=src --cov-report=term --cov-report=html:coverage_html tests/
  artifacts:
    name: "coverage-${CI_COMMIT_SHA}"
    paths:
      - coverage_html/
    expire_in: 1 week

# -----------------------------------------------------------------------------
# STAGE: BUILD
# -----------------------------------------------------------------------------
build:docker:
  stage: build
  image: docker:24.0.5
  services:
    - docker:24.0.5-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - echo "==> Building Docker image with layer caching..."
    - docker pull $RELEASE_TAG || true
    - docker build --cache-from $RELEASE_TAG -t $IMAGE_TAG -t $RELEASE_TAG .
    - docker push $IMAGE_TAG
    - docker push $RELEASE_TAG
  only:
    - main

# -----------------------------------------------------------------------------
# STAGE: SECURITY
# -----------------------------------------------------------------------------
security:trivy-scan:
  stage: security
  image:
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy image --exit-code 1 --severity HIGH,CRITICAL $IMAGE_TAG
  only:
    - main

# -----------------------------------------------------------------------------
# STAGE: DEPLOY
# -----------------------------------------------------------------------------
deploy:staging:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - echo "==> Deploying to Staging Kubernetes Cluster..."
    - kubectl config set-cluster staging --server=$KUBE_STAGING_SERVER
    - kubectl config set-credentials ci-user --token=$KUBE_STAGING_TOKEN
    - kubectl config set-context staging --cluster=staging --user=ci-user
    - kubectl config use-context staging
    - kubectl set image deployment/myapp-api myapp=$IMAGE_TAG -n staging
  environment:
    name: staging
    url: https://staging-api.example.com
  only:
    - main
```

---

### 3. Production Jenkins Declarative Pipeline

Below is an enterprise `Jenkinsfile` written in Declarative Groovy syntax. It handles secret credential bindings, parallel test stages, Docker container execution, and slack notifications.

```groovy
// Jenkinsfile
// Enterprise Declarative Pipeline for Linux Infrastructure Workloads

pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u 0:0'
        }
    }

    options {
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
        ansiColor('xterm')
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    environment {
        REGISTRY_CREDS = credentials('jenkins-docker-hub-credentials')
        APP_NAME       = 'infrastructure-api'
        IMAGE_TAG      = "company/${env.APP_NAME}:${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout & Environment Info') {
            steps {
                sh '''
                    echo "==> Execution Node Details:"
                    uname -a
                    python3 --version
                    git log -1 --stat
                '''
            }
        }

        stage('Code Quality & SAST') {
            steps {
                sh '''
                    pip install --upgrade pip
                    pip install flake8 bandit
                    flake8 --max-line-length=88 .
                    bandit -r ./src -ll
                '''
            }
        }

        stage('Parallel Test Execution') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh '''
                            pip install -r requirements.txt pytest
                            pytest tests/unit/
                        '''
                    }
                }
                stage('Integration Tests') {
                    steps {
                        sh '''
                            pip install -r requirements.txt pytest
                            pytest tests/integration/ || true
                        '''
                    }
                }
            }
        }

        stage('Build & Push Container Image') {
            steps {
                script {
                    sh "docker build -t ${env.IMAGE_TAG} ."
                    sh "echo ${env.REGISTRY_CREDS_PSW} | docker login -u ${env.REGISTRY_CREDS_USR} --password-stdin"
                    sh "docker push ${env.IMAGE_TAG}"
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo "Pipeline succeeded! Build #${env.BUILD_NUMBER} complete."
        }
        failure {
            echo "Pipeline FAILED on Build #${env.BUILD_NUMBER}! Inspect logs."
        }
    }
}
```

---

## Self-Hosted Runner Infrastructure Administration

Operating production self-hosted CI runners requires system administration skills in process isolation, security privileges, resource cgroups, and automated cleanup maintenance.

### 1. GitHub Actions Self-Hosted Runner Administration on Ubuntu/RHEL

#### Step 1: Provision System Service User & File Hierarchy

Always run CI runners under an unprivileged user account. Never run CI runners as `root`.

```bash
# 1. Create a dedicated system user for the runner without interactive shell access
sudo useradd -m -s /bin/bash -c "GitHub Actions Runner System User" runner

# 2. Add runner to docker group to allow container builds without root privileges
sudo usermod -aG docker runner

# 3. Create runner installation directory hierarchy
sudo mkdir -p /opt/actions-runner && sudo chown -R runner:runner /opt/actions-runner
cd /opt/actions-runner
```

#### Step 2: Download, Verify, & Configure Runner Binary

```bash
# Switch to unprivileged runner user context
sudo -u runner -i
cd /opt/actions-runner

# Download official runner tarball (replace version as needed)
RUNNER_VERSION="2.317.0"
curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L \
  https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Verify SHA256 Checksum integrity
echo "9e8872f4db3561ed088142340b10e6cb1b7e214b908f17e6573b37eba92f34a8  actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz" | sha256sum -c -

# Extract archive
tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Configure runner non-interactively against repository
# (Obtain runner token from GitHub Repository Settings -> Actions -> Runners)
./config.sh --url https://github.com/your-org/your-repo \
  --token AGENT_REGISTRATION_TOKEN_HERE \
  --name "prod-runner-node-01" \
  --labels "linux,x64,docker,ubuntu22" \
  --work "_work" \
  --unattended --replace
```

#### Step 3: Configure Hardened Systemd Service Unit

Create `/etc/systemd/system/actions-runner.service` to supervise the runner process, manage resource limits, and auto-restart on crashes.

```ini
# /etc/systemd/system/actions-runner.service
[Unit]
Description=GitHub Actions Self-Hosted Runner Node 01
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=runner
Group=runner
WorkingDirectory=/opt/actions-runner
ExecStart=/opt/actions-runner/bin/runsvc.sh
KillMode=process
KillSignal=SIGTERM
TimeoutStopSec=5min
Restart=always
RestartSec=10s

# Security Hardening & Resource Control (cgroups)
LimitNOFILE=65536
MemoryMax=16G
CPUWeight=100
TasksMax=8192
PrivateTmp=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
```

Enable and activate the system service:

```bash
# Reload systemd configuration manager
sudo systemctl daemon-reload

# Enable runner service to start on system boot
sudo systemctl enable --now actions-runner.service

# Verify service operational status
sudo systemctl status actions-runner.service

# Tail real-time system logs
sudo journalctl -u actions-runner.service -f --output=cat
```

#### Step 4: Automated Maintenance & Resource Pruning Script

Build jobs generate substantial disk bloat (dangling Docker images, unused volumes, leftover build workspaces). Create `/usr/local/bin/ci-runner-cleanup.sh`:

```bash
#!/usr/bin/env bash
# /usr/local/bin/ci-runner-cleanup.sh
# Automated Nightly Maintenance Script for Self-Hosted CI Runners
set -euo pipefail

LOG_FILE="/var/log/ci-runner-cleanup.log"
exec >> "${LOG_FILE}" 2>&1

echo "================================================================="
echo "Starting CI Runner Maintenance Cleanup at $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "================================================================="

# 1. Prune unused Docker container objects older than 24 hours
echo "==> Pruning stopped containers and unused networks..."
docker container prune -f --filter "until=24h"
docker network prune -f --filter "until=24h"

# 2. Remove dangling Docker build images and build cache
echo "==> Pruning dangling images and BuildKit cache..."
docker image prune -f --filter "until=48h"
docker builder prune -a -f --filter "until=72h"

# 3. Clean up leftover runner workspace directories older than 7 days
echo "==> Cleaning stale runner workspace build folders..."
find /opt/actions-runner/_work/ -maxdepth 3 -mindepth 2 -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true

# 4. Check system disk space utilization
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
echo "==> Current Root Disk Usage: ${DISK_USAGE}%"

if [ "${DISK_USAGE}" -gt 85 ]; then
    echo "WARNING: Disk space exceeded 85%! Performing emergency Docker system prune..."
    docker system prune -a --volumes -f
fi

echo "Maintenance Cleanup completed successfully."
```

Make the maintenance script executable and add it to root system cron:

```bash
sudo chmod +x /usr/local/bin/ci-runner-cleanup.sh

# Add cron job to run nightly at 02:00 AM
echo "0 2 * * * root /usr/local/bin/ci-runner-cleanup.sh" | sudo tee /etc/cron.d/ci-runner-cleanup
```

---

### 2. GitLab Runner Infrastructure Setup (`gitlab-runner`)

```bash
# 1. Add official GitLab Runner repository
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash

# 2. Install gitlab-runner package
sudo apt-get install gitlab-runner -y

# 3. Register runner non-interactively with Docker executor
sudo gitlab-runner register \
  --non-interactive \
  --url "https://gitlab.com/" \
  --registration-token "GL_REGISTRATION_TOKEN_HERE" \
  --executor "docker" \
  --docker-image "ubuntu:22.04" \
  --description "production-docker-runner-01" \
  --tag-list "docker,ubuntu,linux" \
  --run-untagged="true" \
  --locked="false" \
  --docker-privileged="false" \
  --docker-volumes "/var/run/docker.sock:/var/run/docker.sock" \
  --docker-volumes "/cache"
```

Configure global runner concurrency in `/etc/gitlab-runner/config.toml`:

```toml
# /etc/gitlab-runner/config.toml
concurrent = 8
check_interval = 5

[session_server]
  session_timeout = 1800

[[runners]]
  name = "production-docker-runner-01"
  url = "https://gitlab.com/"
  id = 123456
  token = "glrt-AGENT_TOKEN_HERE"
  token_obtained_at = 2026-01-01T00:00:00Z
  token_expires_at = 0001-01-01T00:00:00Z
  executor = "docker"
  [runners.custom_build_dir]
  [runners.cache]
    MaxUploadedArchiveSize = 524288000
    Type = "s3"
    Shared = true
    [runners.cache.s3]
      ServerAddress = "minio.internal.example.com:9000"
      AccessKey = "MINIO_ACCESS_KEY"
      SecretKey = "MINIO_SECRET_KEY"
      BucketName = "gitlab-runner-cache"
      Insecure = false
  [runners.docker]
    tls_verify = false
    image = "ubuntu:22.04"
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache"]
    shm_size = 2147483648
```

---

## Enterprise Security & Supply Chain Protection in CI/CD

### 1. OIDC Passwordless Authentication for Cloud Deployment

Long-lived API tokens stored in CI secrets pose severe security risks if leaked. **OpenID Connect (OIDC)** allows CI runners to acquire short-lived, ephemeral cloud credentials directly from AWS, GCP, or Azure without saving static access keys in repository secrets.

```
+------------------+         1. Request OIDC Token (JWT)        +-------------------+
| GitHub Actions   | -----------------------------------------> | GitHub OIDC Provider|
| CI Runner        | <----------------------------------------- | (issuer)          |
+------------------+         2. Return Signed JWT Token         +-------------------+
         |
         | 3. Present JWT & Assume IAM Role
         v
+------------------+         4. Validate JWT Claims             +-------------------+
| AWS STS / GCP    | -----------------------------------------> | Verify Issuer &   |
| Security Token   | <----------------------------------------- | Subject Claim     |
+------------------+         5. Return Ephemeral AWS Credentials+-------------------+
```

#### AWS IAM Trust Policy for GitHub Actions OIDC

To establish OIDC trust between GitHub Actions and AWS IAM, define the following JSON trust policy on the target AWS IAM Role (`arn:aws:iam::123456789012:role/GitHubActionsK8sDeployerRole`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:your-org/your-repo:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

Using OIDC in GitHub Actions step:

```yaml
    steps:
      - name: Configure AWS Ephemeral Credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsK8sDeployerRole
          aws-region: us-east-1

      - name: Verify AWS Caller Identity
        run: |
          aws sts get-caller-identity
```

### 2. Supply Chain Verification: SBOM & Image Signing with Cosign

```bash
# 1. Generate Software Bill of Materials (SBOM) for container image using Syft
syft ghcr.io/your-org/your-repo:latest -o spdx-json > sbom.spdx.json

# 2. Scan generated SBOM for known vulnerabilities using Grype
grype sbom:sbom.spdx.json --fail-on high

# 3. Sign container image in registry keylessly using Cosign & OIDC
cosign sign --yes ghcr.io/your-org/your-repo:latest

# 4. Verify image signature prior to deployment
cosign verify ghcr.io/your-org/your-repo:latest \
  --certificate-identity-regexp "https://github.com/your-org/your-repo/.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com"
```

---

## Real-World Infrastructure Scenarios

### Scenario 1: High-Throughput Kubernetes Microservice Pipeline with Helm & Trivy Security Gates

**Context**: An enterprise e-commerce platform processes 50 microservice builds per hour. Security requires strict zero-trust vulnerability gates: no container image containing `CRITICAL` CVEs can be deployed to production, and Kubernetes manifests must pass syntax linting and dry-run API validation prior to merging.

**Solution Architecture & Workflow**:

```
[ Developer PR ] ──> [ Helm Lint & Schema Check ] ──> [ Build Docker Image ]
                                                             │
[ Deploy K8s ] <── [ K8s Dry-Run ] <── [ Trivy CRITICAL Scan ] <──┘
```

**Implementation Shell Script Enforcement (`scripts/ci-gate-check.sh`)**:

```bash
#!/usr/bin/env bash
# scripts/ci-gate-check.sh
# Custom Infrastructure Enforcement Script for Kubernetes & Container Security Gates
set -euo pipefail

IMAGE_REF="${1:-ghcr.io/company/cart-service:latest}"
HELM_CHART_DIR="${2:-./helm/cart-service}"

echo "================================================================"
echo "Starting Enterprise Infrastructure Security Gate Verification"
echo "Target Image: ${IMAGE_REF}"
echo "Target Chart: ${HELM_CHART_DIR}"
echo "================================================================"

# 1. Validate Helm Chart Syntax and Render Templates
echo "==> Step 1: Executing Helm Linting..."
helm lint "${HELM_CHART_DIR}"

echo "==> Step 2: Rendering Helm Templates for Client Validation..."
helm template test-release "${HELM_CHART_DIR}" --values "${HELM_CHART_DIR}/values.yaml" > /tmp/rendered-manifests.yaml

# 2. Perform Container Image Vulnerability Audit with Trivy
echo "==> Step 3: Scanning Container Image for High/Critical CVEs..."
if ! trivy image --exit-code 1 --severity CRITICAL,HIGH --ignore-unfixed "${IMAGE_REF}"; then
    echo "ERROR: Vulnerability Gate FAILED! Image contains unresolved CRITICAL/HIGH vulnerabilities."
    exit 1
fi
echo "SUCCESS: Container Image passed vulnerability scan."

# 3. Validate Rendered Manifests Against Live Kubernetes OpenAPI Schema (Dry-Run)
if [ -n "${KUBECONFIG:-}" ]; then
    echo "==> Step 4: Performing Server-Side Kubernetes API Dry-Run Validation..."
    kubectl apply --dry-run=server -f /tmp/rendered-manifests.yaml
fi

echo "================================================================"
echo "ALL INFRASTRUCTURE GATES PASSED SUCCESSFULLY"
echo "================================================================"
```

---

### Scenario 2: Air-Gapped Enterprise CI Cluster with MinIO S3 Caching & Private Harbor Registry

**Context**: A financial software company operates an isolated, air-gapped on-premises Linux data center. Pipelines cannot access external internet registries or public dependency caches. All builds must pull from a local Harbor container registry, use an internal S3 object store (MinIO) for pipeline caching, and trust an internal Enterprise Certificate Authority (CA).

**Implementation Blueprint**:

1. **Import Corporate Root CA into Runner System Store**:

```bash
# Copy enterprise internal CA certificate to system store
sudo cp enterprise-root-ca.crt /usr/local/share/ca-certificates/enterprise-root-ca.crt
sudo update-ca-certificates

# Verify certificate bundle includes root CA
openssl verify /usr/local/share/ca-certificates/enterprise-root-ca.crt
```

2. **Configure Docker Daemon to Trust Private Harbor Registry (`/etc/docker/daemon.json`)**:

```json
{
  "insecure-registries": [],
  "registry-mirrors": [
    "https://harbor.internal.example.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "5"
  }
}
```

3. **Air-Gapped Workflow Configuration utilizing MinIO Cache**:

```yaml
# .github/workflows/airgapped-ci.yml
name: Air-Gapped Enterprise CI Pipeline

on:
  push:
    branches: [ main ]

env:
  HARBOR_REGISTRY: harbor.internal.example.com
  IMAGE_NAME: harbor.internal.example.com/finance/ledger-service

jobs:
  build-airgapped:
    runs-on: [ self-hosted, air-gapped, linux ]

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Log in to Private Harbor Registry
        run: |
          echo "${{ secrets.HARBOR_PASSWORD }}" | docker login -u "${{ secrets.HARBOR_USERNAME }}" --password-stdin https://${{ env.HARBOR_REGISTRY }}

      - name: Build Container Image pointing to Local Base Mirror
        run: |
          docker build \
            --build-arg BASE_IMAGE=harbor.internal.example.com/base-images/python:3.11-slim \
            -t ${{ env.IMAGE_NAME }}:${{ github.sha }} .

      - name: Push Container Image to Harbor
        run: |
          docker push ${{ env.IMAGE_NAME }}:${{ github.sha }}
```

---

## Comprehensive Troubleshooting & Diagnostics Matrix

| Symptom / Error Message | Suspected Root Cause | Diagnostic & Verification Command | Production Remediation |
| :--- | :--- | :--- | :--- |
| `permission denied while trying to connect to the Docker daemon socket` | Runner user lacks read/write permissions on `/var/run/docker.sock`. | `ls -la /var/run/docker.sock`<br>`id runner` | Add runner user to docker group: `sudo usermod -aG docker runner && sudo systemctl restart actions-runner`. |
| `No space left on device` during Docker build phase | Unused Docker build layers, dangling images, or volume bloat consuming system disk. | `df -h /`<br>`docker system df` | Run prune command: `docker system prune -a --volumes -f`. Setup automated nightly cleanup cron script. |
| `Cache restoration failed: connection refused / timeout` | S3/MinIO cache backend unreachable, incorrect credentials, or firewall block. | `curl -Iv https://minio.internal.example.com:9000/minio/health/live` | Verify S3 endpoint routing, check MinIO access keys, and ensure runner network policy allows outbound port 9000. |
| `GitHub Actions OIDC Token Invalid / InvalidIdentityToken` | AWS IAM Role trust policy `sub` claim mismatch or clock skew between runner host and AWS STS. | `aws sts get-caller-identity`<br>`chronyc tracking` | Update AWS IAM Role Trust policy JSON `sub` pattern to match repository branch (`repo:org/repo:ref:refs/heads/main`). Resync system clock via `chrony`. |
| `GitLab dind: Cannot connect to the Docker daemon at unix:///var/run/docker.sock` | Docker-in-Docker service missing `DOCKER_TLS_CERTDIR` or missing service declaration. | Inspect `.gitlab-ci.yml` `services:` block and container logs. | Set `DOCKER_TLS_CERTDIR: "/certs"` and ensure `services: - docker:24.0.5-dind` is properly defined. |
| `Runner service enters CrashLoopBackOff / inactive (dead)` | Runner binary lost registration token, host OOM kill, or corrupt workspace permissions. | `sudo systemctl status actions-runner.service`<br>`journalctl -u actions-runner -n 100` | Re-run `./config.sh --replace` with fresh registration token. Increase system memory limits in `/etc/systemd/system/actions-runner.service`. |
| `x509: certificate signed by unknown authority` | Private registry or enterprise proxy uses custom SSL certificate untrusted by runner host OS. | `openssl s_client -connect harbor.internal.example.com:443 -showcerts` | Add CA certificate to `/usr/local/share/ca-certificates/` and execute `sudo update-ca-certificates`. |
| `Job timed out after 60m0s` | Deadlock in test suite, infinite loop, or hanging interactive prompt (`sudo`, `apt-get` without `-y`). | Check pipeline step log at hang timestamp. | Add non-interactive flags (`DEBIAN_FRONTEND=noninteractive apt-get install -y`). Set step timeouts (`timeout-minutes: 15`). |
| `Gitleaks detected secret leak in commit history` | Plaintext API key, private key, or password committed in Git history delta. | `gitleaks detect --source . --verbose` | Revoke exposed credential immediately. Purge secret from Git history using `git-filter-repo` or BFG Repo-Cleaner before force pushing. |
| `OutOfMemory Error (OOM Killed)` | Pipeline build step exceeded container/process RAM ceiling allocated by cgroups. | `dmesg -T \| grep -i oom`<br>`journalctl -k \| grep -i docker` | Increase systemd limit `MemoryMax=16G` or tune compiler/test runner concurrency (e.g., `pytest -n 2` instead of `-n auto`). |

---

## Hands-On Laboratory Exercises

### Lab 1: Local Workflow Simulation & Debugging with `act`

**Objective**: Install and configure `act` to run and debug GitHub Actions workflows locally inside Docker containers without pushing test commits to remote repositories.

#### Step 1: Install `act` Runner Utility on Linux Host

```bash
# Download and install latest release of act
curl -shttps://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash -s -- -b /usr/local/bin

# Verify installation
act --version
```

#### Step 2: Create Local Configuration & Secrets Mock File

Create `~/.actrc` to specify default container images:

```text
-P ubuntu-latest=catthehacker/ubuntu:act-latest
-P ubuntu-22.04=catthehacker/ubuntu:act-22.04
```

Create `.secrets` file in project repository root:

```ini
DOCKER_USERNAME=localtestuser
DOCKER_PASSWORD=mockpassword123
GITHUB_TOKEN=mockgithubtoken456
```

#### Step 3: Run and Debug Local Workflows

```bash
# List all jobs in repository workflows
act -l

# Run entire default workflow locally
act

# Run specific job (e.g., lint-and-security) with local secrets
act -j lint-and-security --secret-file .secrets

# Run workflow in dry-run mode
act -n
```

---

### Lab 2: Deploying & Hardening an Enterprise Self-Hosted Runner Service

**Objective**: Provision a dedicated, isolated self-hosted GitHub Actions runner service on an Ubuntu Linux server using a non-root system account, custom systemd unit controls, and cgroups memory limits.

#### Step 1: Setup Unprivileged System Account & Isolation Paths

```bash
# Create runner account
sudo useradd -m -s /bin/bash -c "CI Service Account" gh-runner
sudo usermod -aG docker gh-runner

# Prepare workspace directory
sudo mkdir -p /var/ci/actions-runner
sudo chown -R gh-runner:gh-runner /var/ci/actions-runner
```

#### Step 2: Extract & Register Runner Agent

```bash
cd /var/ci/actions-runner
sudo -u gh-runner curl -o runner.tar.gz -L https://github.com/actions/runner/releases/download/v2.317.0/actions-runner-linux-x64-2.317.0.tar.gz
sudo -u gh-runner tar xzf runner.tar.gz

# Note: Substitute your valid GitHub token below
sudo -u gh-runner ./config.sh \
  --url https://github.com/your-username/your-repo \
  --token YOUR_RUNNER_REGISTRATION_TOKEN \
  --name "hardened-linux-runner-01" \
  --unattended --replace
```

#### Step 3: Install & Start Hardened Systemd Service

Create `/etc/systemd/system/gh-runner.service`:

```ini
[Unit]
Description=Hardened GitHub Actions Runner Service
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=gh-runner
Group=gh-runner
WorkingDirectory=/var/ci/actions-runner
ExecStart=/var/ci/actions-runner/bin/runsvc.sh
KillMode=process
Restart=always
RestartSec=5s

# Cgroup Resource Controls
MemoryMax=8G
CPUWeight=100
TasksMax=4096

[Install]
WantedBy=multi-user.target
```

Activate service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gh-runner.service
sudo systemctl status gh-runner.service
```

---

### Lab 3: Building a Complete DevSecOps Pipeline Shell Audit Script

**Objective**: Author a standalone DevSecOps verification script (`devsecops-audit.sh`) that integrates Gitleaks, Bandit, Flake8, Syft, and Trivy into a unified security audit executable for Linux CI runners.

#### Step 1: Write Script (`devsecops-audit.sh`)

```bash
#!/usr/bin/env bash
# devsecops-audit.sh - Automated Linux DevSecOps Local Audit Tool
set -euo pipefail

PROJECT_DIR="${1:-.}"
REPORT_DIR="${PROJECT_DIR}/security-reports"

mkdir -p "${REPORT_DIR}"
echo "================================================================="
echo "Starting DevSecOps Security Suite Execution on: ${PROJECT_DIR}"
echo "Reports directory: ${REPORT_DIR}"
echo "================================================================="

# 1. Gitleaks Secret Audit
if command -v gitleaks &> /dev/null; then
    echo "[1/4] Running Gitleaks Secret Detection..."
    gitleaks detect --source "${PROJECT_DIR}" -r "${REPORT_DIR}/gitleaks-report.json" -f json || echo "WARNING: Leaked secrets detected!"
else
    echo "[1/4] Skipping Gitleaks (not installed)."
fi

# 2. Python SAST with Bandit
if command -v bandit &> /dev/null; then
    echo "[2/4] Running Bandit Python SAST..."
    bandit -r "${PROJECT_DIR}/src" -f json -o "${REPORT_DIR}/bandit-report.json" || echo "WARNING: SAST issues found!"
else
    echo "[2/4] Skipping Bandit (not installed)."
fi

# 3. Generate SBOM using Syft
if command -v syft &> /dev/null; then
    echo "[3/4] Generating Software Bill of Materials (SBOM)..."
    syft dir:"${PROJECT_DIR}" -o spdx-json > "${REPORT_DIR}/sbom.spdx.json"
    echo "SUCCESS: SBOM written to ${REPORT_DIR}/sbom.spdx.json"
else
    echo "[3/4] Skipping Syft (not installed)."
fi

# 4. Trivy File System Vulnerability Audit
if command -v trivy &> /dev/null; then
    echo "[4/4] Running Trivy Filesystem Vulnerability Scan..."
    trivy fs "${PROJECT_DIR}" --severity HIGH,CRITICAL -f json -o "${REPORT_DIR}/trivy-fs-report.json"
else
    echo "[4/4] Skipping Trivy (not installed)."
fi

echo "================================================================="
echo "DevSecOps Audit Complete. Reports generated in ${REPORT_DIR}"
echo "================================================================="
```

#### Step 2: Make Executable & Test Run

```bash
chmod +x devsecops-audit.sh
./devsecops-audit.sh .
ls -la security-reports/
```

---

## Self-Check & Verification Checklist

- [ ] **Architecture & Platform Knowledge**: Can you explain the core differences between GitHub Actions, GitLab CI, and Jenkins, including their execution contexts and isolation boundaries?
- [ ] **Workflow Creation**: Can you write an enterprise GitHub Actions or GitLab CI YAML pipeline containing linting, matrix unit testing, container building, and deployment gates from scratch?
- [ ] **Self-Hosted Runner Administration**: Can you provision a non-root self-hosted CI runner on Ubuntu/RHEL under systemd with cgroup memory limits and automated nightly prune crons?
- [ ] **Local Simulation**: Can you debug workflow failures locally using `act` with custom mock `.secrets` and `.actrc` images?
- [ ] **DevSecOps & Supply Chain**: Can you integrate Gitleaks secret detection, Trivy image vulnerability scanning, Syft SBOM generation, and Cosign image signing into CI pipelines?
- [ ] **Cloud OIDC Integration**: Can you explain how OpenID Connect (OIDC) replaces static API keys for cloud deployment tasks in GitHub Actions?
- [ ] **Troubleshooting Mastery**: Can you diagnose Docker socket permission errors, out-of-space disk failures, CA certificate errors, and OOM kills on CI runner nodes?

---

## Recommended Learning Resources & Next Steps

1. **GitHub Actions Official Documentation**: [https://docs.github.com/en/actions](https://docs.github.com/en/actions)
2. **GitLab CI/CD Architecture Guide**: [https://docs.gitlab.com/ee/ci/](https://docs.gitlab.com/ee/ci/)
3. **Jenkins User Handbook**: [https://www.jenkins.io/doc/book/](https://www.jenkins.io/doc/book/)
4. **Aqua Security Trivy Documentation**: [https://aquasecurity.github.io/trivy/](https://aquasecurity.github.io/trivy/)
5. **Cosign / Sigstore Supply Chain Security**: [https://docs.sigstore.dev/cosign/overview/](https://docs.sigstore.dev/cosign/overview/)
6. **Nektos Act Local GitHub Actions Runner**: [https://github.com/nektos/act](https://github.com/nektos/act)

→ **Next Step**: Proceed to [[10 - Cloud Foundations]]