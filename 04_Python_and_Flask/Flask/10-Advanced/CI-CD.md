---
title: CI/CD
description: Continuous Integration and Continuous Deployment for Flask applications
chapter: 10-Advanced
tags:
  - ci-cd
  - github-actions
  - gitlab-ci
  - automation
  - testing
  - deployment
difficulty: Advanced
prerequisites:
  - [[10-Advanced/Docker]]
  - [[09-Testing/Testing-Overview]]
---

# CI/CD

> Continuous Integration (CI) and Continuous Deployment (CD) automate the process of testing, building, and deploying your Flask application. A good CI/CD pipeline catches bugs before they reach production, ensures consistent deployments, and enables rapid iteration. This chapter covers building production-ready CI/CD pipelines for Flask.

## Learning Objectives

After completing this chapter, you will be able to:

- Explain CI/CD concepts and their benefits
- Build a CI pipeline with GitHub Actions for a Flask application
- Implement automated testing, linting, and security scanning
- Create a CD pipeline that deploys to staging and production
- Use Docker in CI/CD pipelines
- Implement blue-green and rolling deployment strategies

## What Is CI/CD?

**Continuous Integration (CI):** Automatically build and test code changes when they are committed.

**Continuous Deployment (CD):** Automatically deploy code that passes CI to production.

```mermaid
graph LR
    Commit[Code Commit] --> CI[CI Pipeline<br/>Test, Lint, Build]
    CI -->|Pass| Staging[Staging Deploy]
    Staging -->|Manual Gate| Prod[Production Deploy]
    CI -->|Fail| Notify[Notify Developer]
    
    style CI fill:#e3f2fd
    style Staging fill:#e8f5e9
    style Prod fill:#c8e6c9
```

## GitHub Actions for Flask

GitHub Actions is a popular CI/CD platform integrated with GitHub repositories.

### Basic CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
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
          pip install -r requirements-dev.txt
      
      - name: Lint with flake8
        run: flake8 myapp tests
      
      - name: Type check with mypy
        run: mypy myapp
      
      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret
        run: pytest --cov=myapp --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### CD Pipeline (Deploy to VPS)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /var/www/myapp
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            flask db upgrade
            sudo systemctl restart myapp
```

### Docker CI/CD Pipeline

```yaml
# .github/workflows/docker.yml
name: Docker Build and Deploy

on:
  push:
    branches: [main]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## CI/CD Best Practices

### 1. Fast Feedback

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - run: |
          pip install flake8 black
          flake8 myapp
          black --check myapp
  
  test:
    runs-on: ubuntu-latest
    needs: lint  # Only run tests if lint passes
    # ... test steps
```

### 2. Matrix Testing

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
    database: [sqlite, postgresql]
```

### 3. Security Scanning

```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myapp:latest
    format: 'sarif'
    output: 'trivy-results.sarif'
```

### 4. Staging Deployment

```yaml
- name: Deploy to staging
  if: github.ref == 'refs/heads/develop'
  run: |
    docker-compose -f docker-compose.staging.yml up -d

- name: Run smoke tests
  run: |
    sleep 10
    curl -f https://staging.example.com/health
```

## Deployment Strategies

### Rolling Deployment

```yaml
# docker-compose.prod.yml
deploy:
  replicas: 4
  update_config:
    parallelism: 1
    delay: 10s
    failure_action: rollback
    order: start-first
```

Update one container at a time. Zero downtime, but during deployment, different versions run simultaneously.

### Blue-Green Deployment

```bash
# Deploy new version alongside old
# Test new version
# Switch traffic
# Keep old version for rollback

docker-compose -f docker-compose.green.yml up -d
# Run health checks
# Update Nginx to point to green
docker-compose -f docker-compose.blue.yml down
```

Two identical production environments. Zero downtime, instant rollback, but requires double the resources.

## Monitoring Deployments

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    channel: '#deployments'
    text: 'Deployment to production: ${{ job.status }}'
```

## Exercises

1. **GitHub Actions**: Create a CI pipeline that lints, type-checks, and tests your Flask app.

2. **Docker CI**: Build a Docker image in CI and push it to a registry.

3. **Deploy Pipeline**: Create a CD pipeline that deploys to a staging server on every push to develop.

4. **Security Scan**: Add vulnerability scanning to your CI pipeline.

## Quiz

**Question 1**: What is the difference between Continuous Integration and Continuous Deployment?

**Question 2**: What are the benefits of CI/CD for Flask applications?

**Question 3**: What is a deployment strategy? Name two.

**Question 4**: Why should you run security scans in CI?

**Question 5**: What is the purpose of a staging environment?

## Interview Questions

1. "Explain CI/CD and why it is important for Flask applications."

2. "How would you set up a CI/CD pipeline for a Flask app using GitHub Actions?"

3. "What deployment strategies exist, and when would you use each?"

4. "How would you handle database migrations in a CI/CD pipeline?"

5. "What checks should run in a CI pipeline before code is deployed?"

## Related Chapters

- [[10-Advanced/Docker]] — Containerization
- [[09-Testing/Testing-Overview]] — Testing fundamentals
- [[07-Deployment/Deployment-Overview]] — Production deployment

## Official Documentation References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI Documentation](https://docs.gitlab.com/ee/ci/)
- [Docker Build GitHub Action](https://github.com/docker/build-push-action)

---

*Previous: [[10-Advanced/Docker]] | Next: [[10-Advanced/REST-API-Development]]*