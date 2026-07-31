---
title: Deployment Overview
description: Everything you need to deploy a Flask application to production — architecture, process, and checklist
chapter: 07-Deployment
tags:
  - deployment
  - production
  - gunicorn
  - nginx
  - linux
  - vps
difficulty: Intermediate
prerequisites:
  - [[01-Flask-Core/Flask-Architecture]]
  - [[00-Foundations/TLS-HTTPS]]
---

# Deployment Overview

> Deploying a Flask application to production involves much more than running `flask run`. It requires a web server, a reverse proxy, HTTPS, environment configuration, monitoring, and security hardening. This chapter provides the complete picture of production deployment.

## Learning Objectives

After completing this chapter, you will be able to:

- Explain the complete production architecture for Flask applications
- Describe the roles of Gunicorn, Nginx, and the Flask app in the request flow
- Understand the deployment process from code to live application
- Follow a production deployment checklist
- Choose between deployment options (VPS, PaaS, containers)
- Monitor and maintain a production Flask application

## Production Architecture

A production Flask deployment typically uses a multi-layer architecture:

```mermaid
graph LR
    User[Browser] -->|HTTPS| Nginx[Nginx<br/>Port 443]
    Nginx -->|Proxy| Gunicorn[Gunicorn<br/>WSGI Server<br/>Port 8000]
    Gunicorn -->|WSGI| Flask[Flask App]
    Flask -->|SQL| DB[(Database)]
    Flask -->|Cache| Redis[(Redis)]
    
    style Nginx fill:#c8e6c9
    style Gunicorn fill:#e3f2fd
    style Flask fill:#fff3e0
```

### Request Flow

```mermaid
sequenceDiagram
    participant B as Browser
    participant N as Nginx
    participant G as Gunicorn
    participant F as Flask
    
    B->>N: HTTPS Request
    N->>N: SSL Termination
    N->>N: Static file? Serve directly
    N->>G: Proxy to Gunicorn
    G->>F: WSGI environ
    F-->>G: WSGI response
    G-->>N: HTTP Response
    N-->>B: HTTPS Response
```

### Component Roles

| Component | Role | Why It Is Needed |
|-----------|------|-----------------|
| **Nginx** | Reverse proxy, static file server, SSL termination | Handles HTTPS, serves static files efficiently, load balancing |
| **Gunicorn** | WSGI HTTP server | Runs Python WSGI apps, manages worker processes |
| **Flask** | Application logic | Your code — handles requests, talks to database |
| **PostgreSQL** | Database | Persistent data storage |
| **Redis** | Cache, session store, task queue | Speeds up responses, offloads database |

## Why Not Just `flask run`?

Flask's development server is not suitable for production:

| Aspect | Development Server | Production Server |
|--------|-------------------|-------------------|
| Workers | Single thread | Multiple workers |
| SSL | Not supported | Full TLS support |
| Static files | Served by Flask | Served by Nginx |
| Security | No hardening | Hardened |
| Performance | Poor | Optimized |
| Stability | Crashes on errors | Handles gracefully |
| Logging | Console only | Structured, rotated |

## Deployment Options

### Virtual Private Server (VPS)

You manage the entire stack on a virtual machine.

**Pros:** Full control, cost-effective, learning opportunity
**Cons:** You manage everything (OS, security, updates)

**Providers:** DigitalOcean, Linode, Vultr, AWS EC2, Google Compute Engine

### Platform as a Service (PaaS)

Deploy code; the platform manages infrastructure.

**Pros:** Zero server management, easy scaling, built-in CI/CD
**Cons:** Less control, vendor lock-in, can be expensive

**Services:** Heroku, PythonAnywhere, AWS Elastic Beanstalk, Google App Engine, Render, Railway

### Containers (Docker + Kubernetes)

Package the application with all dependencies.

**Pros:** Consistent across environments, easy scaling, portable
**Cons:** Added complexity, learning curve

**Services:** Docker, Kubernetes, AWS ECS, Google GKE, Azure AKS

### Serverless

Run code without managing servers.

**Pros:** Pay per request, auto-scaling, no server management
**Cons:** Cold starts, limited execution time, vendor lock-in

**Services:** AWS Lambda, Google Cloud Functions, Azure Functions

## The Deployment Process

### 1. Prepare the Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx postgresql redis-server

# Create application user
sudo useradd -m -s /bin/bash flaskapp
```

### 2. Set Up the Application

```bash
# Create project directory
sudo mkdir -p /var/www/myapp
sudo chown flaskapp:flaskapp /var/www/myapp

# Clone code
cd /var/www/myapp
git clone https://github.com/your/repo.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=run.py
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export DATABASE_URL=postgresql://user:pass@localhost/myapp
```

### 3. Configure Gunicorn

```bash
# Test Gunicorn
gunicorn -w 4 -b 127.0.0.1:8000 run:app
```

Create a Gunicorn service file:

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=Gunicorn instance for myapp
After=network.target

[Service]
User=flaskapp
Group=www-data
WorkingDirectory=/var/www/myapp
Environment="PATH=/var/www/myapp/venv/bin"
Environment="SECRET_KEY=your-secret"
Environment="DATABASE_URL=postgresql://..."
ExecStart=/var/www/myapp/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 run:app

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start myapp
sudo systemctl enable myapp
```

### 4. Configure Nginx

```nginx
# /etc/nginx/sites-available/myapp
server {
    listen 80;
    server_name example.com www.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /var/www/myapp/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /uploads {
        alias /var/www/myapp/uploads;
        internal;  # Only accessible via X-Accel-Redirect
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

### 5. Enable HTTPS

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d example.com -d www.example.com

# Auto-renewal is configured automatically
```

### 6. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres createdb myapp
sudo -u postgres createuser flaskapp
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE myapp TO flaskapp;"

# Run migrations
flask db upgrade
```

## Environment Variables in Production

Use a systemd service file or `.env` file for production environment variables. Never hardcode secrets.

```bash
# /var/www/myapp/.env
SECRET_KEY=your-production-secret
DATABASE_URL=postgresql://flaskapp:password@localhost/myapp
MAIL_SERVER=smtp.example.com
MAIL_USERNAME=noreply@example.com
MAIL_PASSWORD=mail-password
```

Ensure the `.env` file is readable only by the application user:

```bash
chmod 600 /var/www/myapp/.env
chown flaskapp:flaskapp /var/www/myapp/.env
```

## Production Checklist

```
[ ] Use Gunicorn (not development server)
[ ] Use Nginx as reverse proxy
[ ] Enable HTTPS with valid SSL certificate
[ ] Set secure SECRET_KEY
[ ] Use PostgreSQL (not SQLite)
[ ] Set DEBUG=False
[ ] Configure logging to files
[ ] Set up log rotation
[ ] Enable firewall (UFW)
[ ] Close unused ports
[ ] Run as non-root user
[ ] Set secure cookie attributes
[ ] Configure CORS if needed
[ ] Set up monitoring
[ ] Configure backups
[ ] Set up CI/CD pipeline
[ ] Test the deployment
```

## Monitoring

Monitor your production application:

```bash
# Check Gunicorn status
sudo systemctl status myapp

# View logs
sudo journalctl -u myapp -f

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Monitor resources
htop
```

## Common Mistakes

**Mistake: Using the development server in production**
Always use Gunicorn or uWSGI.

**Mistake: Not using a reverse proxy**
Gunicorn should not be exposed directly to the internet.

**Mistake: Running as root**
Always run the application as a non-root user.

**Mistake: Not setting DEBUG=False**
Debug mode exposes stack traces and the interactive debugger.

**Mistake: Hardcoding secrets**
Use environment variables for all secrets.

## Best Practices

- Use Gunicorn with multiple workers (typically `2 * CPU cores + 1`)
- Use Nginx for SSL termination and static files
- Keep the application server on localhost only
- Use PostgreSQL for production databases
- Set up automated backups
- Monitor logs for errors
- Use a process manager (systemd) to auto-restart on crash
- Deploy using CI/CD pipelines
- Test deployments in a staging environment first

## Exercises

1. **Local Setup**: Set up Gunicorn and Nginx locally to serve a Flask app.

2. **SSL Certificate**: Use Certbot to obtain and configure an SSL certificate.

3. **Systemd Service**: Create a systemd service file for Gunicorn.

4. **Firewall**: Configure UFW to allow only SSH, HTTP, and HTTPS traffic.

5. **Monitoring**: Set up log rotation and basic monitoring for your application.

## Quiz

**Question 1**: What is the role of Gunicorn in a production Flask deployment?

**Question 2**: Why use Nginx as a reverse proxy instead of exposing Gunicorn directly?

**Question 3**: What is SSL termination, and why does Nginx handle it?

**Question 4**: Why should you not use the Flask development server in production?

**Question 5**: What is the purpose of a systemd service file for Gunicorn?

## Interview Questions

1. "Explain the production architecture for a Flask application."

2. "What is the difference between Gunicorn and Nginx? Why use both?"

3. "How would you deploy a Flask application to a VPS?"

4. "What security measures should you take when deploying a Flask app?"

5. "How would you handle static files in production?"

6. "Explain how you would set up HTTPS for a Flask application."

## Related Chapters

- [[07-Deployment/Gunicorn]] — Deep dive into Gunicorn
- [[07-Deployment/Nginx]] — Nginx configuration
- [[07-Deployment/HTTPS]] — SSL/TLS setup
- [[07-Deployment/Linux-Server]] — Server hardening
- [[10-Advanced/Docker]] — Containerized deployment
- [[10-Advanced/CI-CD]] — Automated deployment

## Official Documentation References

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Certbot Documentation](https://eff-certbot.readthedocs.io/)
- [Flask Deployment Options](https://flask.palletsprojects.com/en/latest/deploying/)

---

*Next: [[07-Deployment/Gunicorn]]*