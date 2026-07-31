# 09 - CI

> **Phase:** 1 (Core Linux) · **Time:** ~3 weeks · **Difficulty:** ⭐⭐⭐⭐

## What it is
**CI (Continuous Integration)** is the practice of automatically testing and building software each time code is committed to version control (usually Git). It aims to catch integration errors early, reduce manual QA, and speed up releases.\n\n**CD (Continuous Deployment/Delivery)** extends CI to automatically deploy validated code to staging or production. In practice, CI and CD are often bundled under the term **DevOps pipelines**.\n\nPopular tools:\n- **GitHub Actions** (cloud, GitHub-hosted)\n- **GitLab CI** (GitLab-hosted)\n- **Jenkins** (self-hosted, plugin ecosystem)\n- **GitHub Actions** is free for public repos; others have tiered pricing for private repos.

Why it matters:
- **Speed**: Automated testing and deployment reduce manual time.\n- **Reliability**: Early bug detection prevents broken builds.\n- **Quality**: Standardizes linting, testing, security scans.\n- **Scalability**: Cloud-native runners handle varying workloads.\n- **Collaboration**: Shared pipelines integrate workflows (reviews, comments).

## Core concepts — detailed

### 1. Typical CI pipeline stages
1. **Push**: triggers workflow (on `push`, `pull_request`, schedule, etc.)\n2. **Checkout**: fetch code from Git.\n3. **Setup**: install dependencies (language‑specific tools, caches).\n4. **Build/Test**: compile, run unit/integration tests, lint, type‑check.\n5. **Security**: static analysis, secret scanning, vulnerability checks.\n6. **Publish**: push artifacts (Docker images, packages) to registries.\n7. **Deploy** (optional): deploy to staging/production.\n
> Modern CI platforms call these **jobs** (parallel steps) and **steps** (commands) within each job.

### 2. GitHub Actions syntax (most common)
`.github/workflows/<workflow-name>.yml`:
```yaml
name: CI Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        pytest tests/

    - name: Lint
      run: |
        black --check .
        flake8 .

    - name: Security scan
      run: |
        pip install safety
        safety check

  publish:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Build and push Docker image
      run: |
        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin docker.io
        docker build -t myapp .
        docker push myapp
      env:
        DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
        DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
```

**Key elements:**\n- `name`: human‑readable title.\n- `on`: events that trigger the workflow.\n- `jobs`: independent parallel jobs.\n- `steps`: sequential commands within a job.\n- `uses`: pre‑built actions (third‑party or official) – easiest for common tasks.\n- `run`: shell commands executed locally on the runner.\n- `secrets`: securely passed environment variables (`\${{ secrets.SECRET_KEY }}`).\n
### 3. Local CI simulation (for learning)
\`\`\`bash\n# Install act (GitHub Actions runner in Docker)\ncurl -fsSL https://github.com/nektos/act/releases/download/v0.2.83/act_linux_amd64 -o /tmp/act\nchmod +x /tmp/act\nsudo mv /tmp/act /usr/local/bin/act\n\n# Run a workflow locally\nact -W .github/workflows/<workflow-name>.yml\`\`\`
### 4. Best practices
- **Fail fast**: Abort pipeline on first failure (use `|| true` for non‑critical steps).\n- **Caching**: Persist dependencies (`actions/cache`).\n- **Branch protection**: Require CI passing before merging.\n- **Secrets management**: Use repo secrets.\n- **Parallel testing**: Use `matrix` strategies to split tests.\n- **Artifacts**: Store test results (`actions/upload-artifact`).\n
## Free resources — curated for self‑learners
\n1. **GitHub Actions Documentation**: https://docs.github.com/en/actions\n2. **GitLab CI Tutorial**: https://docs.gitlab.com/ee/ci/\n3. **Jenkins Official Docs**: https://www.jenkins.io/doc/\n4. **DigitalOcean: CI/CD with GitHub Actions**: https://www.digitalocean.com/tutorials/github-actions-ci-cd-pipeline\n5. **Zero to Hero: GitHub Actions (free blog series)**: https://dev.to/isonadev/zero-to-hero-github-actions-44n6\n6. **CI/CD with GitLab CI**: https://about.gitlab.com/get-started/ci/\n7. **Jenkins Groovy pipeline basics**: https://jenkins.io/doc/pipeline/groovy/\n8. **Actions/cache usage examples**: https://github.com/actions/toolkit/blob/main/docs/cache/README.md\n## Practice labs (use a free GitHub account for real CI testing)\n\n### Lab 1: Local GitHub Actions simulation (using `act`)\n```bash\n# Install act (GitHub Actions runner in Docker)\ncurl -fsSL https://github.com/nektos/act/releases/download/v0.2.83/act_linux_amd64 -o /tmp/act\nchmod +x /tmp/act\nsudo mv /tmp/act /usr/local/bin/act\n# Run a workflow locally\nsudo act -W .github/workflows/<workflow-name>.yml\n```\n\n### Lab 2: Create a GitHub Actions workflow for a Python project\n\nCreate `.github/workflows/ci.yml`:\n\n```yaml\nname: Python CI\n\non:\n  push:\n    branches: [main]\n  pull_request:\n    branches: [main]\n\njobs:\n  test:\n    runs-on: ubuntu-latest\n\n    steps:\n    - uses: actions/checkout@v4\n\n    - name: Set up Python\n      uses: actions/setup-python@v4\n      with:\n        python-version: \"3.11\"\n\n    - name: Install dependencies\n      run: |\n        python -m pip install --upgrade pip\n        pip install -r requirements.txt\n\n    - name: Run tests\n      run: |\n        pytest tests/\n\n    - name: Lint\n      run: |\n        black --check .\n        flake8 .\n\n    - name: Security scan\n      run: |\n        pip install safety\n        safety check\n```\n### Lab 3: Create a GitHub Actions workflow for a Docker project\n\nCreate `.github/workflows/docker.yml`:\n```yaml\nname: Docker CI\n\non:\n  push:\n    branches: [main]\n\njobs:\n  build:\n    runs-on: ubuntu-latest\n\n    steps:\n    - uses: actions/checkout@v4\n\n    - name: Build Docker image\n      run: |\n        docker build -t myapp .\n\n    - name: Run container tests\n      run: |\n        docker run myapp pytest -v tests/\n\n    - name: Push to Docker Hub (optional)\n      run: |\n        echo \"\"$DOCKER_PASSWORD\"\" | docker login -u \"$DOCKER_USERNAME\" --password-stdin\n        docker push myapp\n      env:\n        DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}\n        DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}\n```\n## Self‑check (can you…)\n- [ ] Create a GitHub Actions workflow for a Python project\n- [ ] Use `act` to test workflows locally\n- [ ] Interpret GitHub Actions logs and troubleshoot\n- [ ] Use repository secrets and environment variables\n- [ ] Create a Docker build workflow\n- [ ] Apply best practices for CI pipelines\n## Progress\n- [ ] Created a Python CI GitHub Actions workflow\n- [ ] Simulated it locally using `act`\n- [ ] Explored secrets management\n- [ ] Created a Docker CI workflow\n- [ ] Reviewed best practices\n## Next\n→ [[10 - Cloud Foundations]]\n