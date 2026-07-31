# Roadmap

> Your learning path from Python developer to production-ready Flask engineer.

This roadmap is divided into four phases. Each phase builds upon the previous one. Do not skip phases — the foundations are essential for understanding advanced topics.

---

## Phase 1: Foundations (Weeks 1-2)

**Goal**: Understand how the internet works before writing any Flask code.

| Order | Topic | File | Why It Matters |
|-------|-------|------|----------------|
| 1 | Internet Basics | [[00-Foundations/Internet-Basics]] | Understand the network that connects everything |
| 2 | Browser | [[00-Foundations/Browser]] | Know how users interact with your application |
| 3 | DNS | [[00-Foundations/DNS]] | Understand how domain names resolve to servers |
| 4 | IP Addresses | [[00-Foundations/IP-Addresses]] | Learn how devices find each other on networks |
| 5 | Ports | [[00-Foundations/Ports]] | Understand how multiple services run on one machine |
| 6 | TCP and UDP | [[00-Foundations/TCP-UDP]] | Learn how data actually travels between machines |
| 7 | TLS and HTTPS | [[00-Foundations/TLS-HTTPS]] | Understand secure communication |
| 8 | HTTP | [[00-Foundations/HTTP]] | Master the protocol that Flask speaks |
| 9 | HTTP/2 and HTTP/3 | [[00-Foundations/HTTP2-HTTP3]] | Learn modern protocol improvements |
| 10 | Cookies and Sessions | [[00-Foundations/Cookies-Sessions]] | Understand state management |
| 11 | REST APIs | [[00-Foundations/REST-APIs]] | Learn the architecture behind modern APIs |
| 12 | JSON | [[00-Foundations/JSON]] | Master the data format of web APIs |
| 13 | Web Technologies | [[00-Foundations/Web-Technologies]] | HTML, CSS, JavaScript basics |

> [!TIP]
> Phase 1 contains no Flask code. This is intentional. You cannot build a house without understanding the ground it stands on. Every Flask concept maps to an HTTP concept — if you skip this phase, you will memorize Flask syntax without understanding why it works.

**Milestone**: You can explain to someone how typing "google.com" into a browser results in a webpage appearing, describing every step from DNS through TCP to HTTP.

---

## Phase 2: Flask Core (Weeks 3-4)

**Goal**: Build a solid understanding of Flask's core mechanics.

| Order | Topic | File | Key Concepts |
|-------|-------|------|--------------|
| 1 | Flask Architecture | [[01-Flask-Core/Flask-Architecture]] | WSGI, Request-Response cycle, Thread locals |
| 2 | Routing | [[01-Flask-Core/Routing]] | `@app.route()`, URL rules, endpoint mapping |
| 3 | URL Converters | [[01-Flask-Core/URL-Converters]] | Built-in converters, custom converters |
| 4 | Request and Response | [[01-Flask-Core/Request-Response]] | `request` object, `make_response()`, `Response` class |
| 5 | Request Context | [[01-Flask-Core/Request-Context]] | `test_request_context()`, context locals |
| 6 | Application Context | [[01-Flask-Core/Application-Context]] | `app_context()`, `current_app`, `g` |
| 7 | Sessions | [[01-Flask-Core/Sessions]] | Server-side sessions, session configuration |
| 8 | Cookies | [[01-Flask-Core/Cookies]] | Setting, reading, modifying cookies |
| 9 | Static Files | [[01-Flask-Core/Static-Files]] | `static` folder, `url_for('static')` |
| 10 | Templates | [[01-Flask-Core/Templates]] | `render_template()`, Jinja2 integration |
| 11 | Error Handling | [[01-Flask-Core/Error-Handling]] | `errorhandler`, custom error pages |
| 12 | Flask CLI | [[01-Flask-Core/Flask-CLI]] | `flask run`, custom commands, `FLASK_APP` |
| 13 | Configuration | [[01-Flask-Core/Configuration]] | Config classes, `config` object, env vars |

**Milestone**: You can build a multi-page Flask application with proper routing, templates, error handling, and configuration.

---

## Phase 3: Templates and Databases (Weeks 5-7)

**Goal**: Build dynamic applications with database persistence.

### Jinja2 Deep Dive (Week 5)

| Order | Topic | File |
|-------|-------|------|
| 1 | Jinja2 Overview | [[02-Jinja2/Jinja2-Overview]] |
| 2 | Template Syntax | [[02-Jinja2/Template-Syntax]] |
| 3 | Template Inheritance | [[02-Jinja2/Template-Inheritance]] |
| 4 | Filters | [[02-Jinja2/Filters]] |
| 5 | Tests | [[02-Jinja2/Tests]] |
| 6 | Macros | [[02-Jinja2/Macros]] |
| 7 | Custom Filters | [[02-Jinja2/Custom-Filters]] |
| 8 | Context Processors | [[02-Jinja2/Context-Processors]] |

### Database Mastery (Weeks 6-7)

| Order | Topic | File |
|-------|-------|------|
| 1 | Database Fundamentals | [[03-Database/Database-Fundamentals]] |
| 2 | SQL Fundamentals | [[03-Database/SQL-Fundamentals]] |
| 3 | SQLAlchemy ORM | [[03-Database/SQLAlchemy-ORM]] |
| 4 | Flask-SQLAlchemy | [[03-Database/Flask-SQLAlchemy]] |
| 5 | Models | [[03-Database/Models]] |
| 6 | Queries | [[03-Database/Queries]] |
| 7 | Relationships | [[03-Database/Relationships]] |
| 8 | Query Optimization | [[03-Database/Query-Optimization]] |
| 9 | SQLAlchemy Migrations | [[03-Database/SQLAlchemy-Migrations]] |
| 10 | Flask-Migrate | [[03-Database/Flask-Migrate]] |

**Milestone**: You can design a database schema, create models with relationships, write efficient queries, and manage schema migrations.

---

## Phase 4: Authentication and Application Building (Weeks 8-10)

**Goal**: Build a complete, secure blog application.

### Authentication (Week 8)

| Order | Topic | File |
|-------|-------|------|
| 1 | Authentication Overview | [[04-Authentication/Authentication-Overview]] |
| 2 | Password Hashing | [[04-Authentication/Password-Hashing]] |
| 3 | Flask-WTF | [[04-Authentication/Flask-WTF]] |
| 4 | WTForms | [[04-Authentication/WTForms]] |
| 5 | Forms | [[04-Authentication/Forms]] |
| 6 | Flask-Login | [[04-Authentication/Flask-Login]] |
| 7 | User Registration | [[04-Authentication/User-Registration]] |
| 8 | Login System | [[04-Authentication/Login-System]] |
| 9 | Flask-Mail | [[04-Authentication/Flask-Mail]] |
| 10 | Account Management | [[04-Authentication/Account-Management]] |

### Blog Application (Weeks 9-10)

| Order | Topic | File |
|-------|-------|------|
| 1 | Blog Overview | [[05-Blog-Application/Blog-Overview]] |
| 2 | Project Setup | [[05-Blog-Application/Project-Setup]] |
| 3 | Database Design | [[05-Blog-Application/Database-Design]] |
| 4 | CRUD Operations | [[05-Blog-Application/CRUD-Operations]] |
| 5 | User Profiles | [[05-Blog-Application/User-Profiles]] |
| 6 | Pagination | [[05-Blog-Application/Pagination]] |
| 7 | Email Integration | [[05-Blog-Application/Email-Integration]] |
| 8 | Custom Error Pages | [[05-Blog-Application/Custom-Error-Pages]] |

**Milestone**: You have built a complete blog application with user registration, login, post creation, editing, deletion, user profiles, and pagination.

---

## Phase 5: Production Architecture (Weeks 11-12)

**Goal**: Prepare your application for real-world deployment.

### Blueprints and Refactoring (Week 11)

| Order | Topic | File |
|-------|-------|------|
| 1 | Blueprints | [[06-Blueprints/Blueprints]] |
| 2 | Application Factory | [[06-Blueprints/Application-Factory]] |
| 3 | Refactoring | [[06-Blueprints/Refactoring]] |
| 4 | Blueprint Organization | [[06-Blueprints/Blueprint-Organization]] |

### Deployment (Week 12)

| Order | Topic | File |
|-------|-------|------|
| 1 | Deployment Overview | [[07-Deployment/Deployment-Overview]] |
| 2 | Linux Server | [[07-Deployment/Linux-Server]] |
| 3 | Gunicorn | [[07-Deployment/Gunicorn]] |
| 4 | Nginx | [[07-Deployment/Nginx]] |
| 5 | HTTPS | [[07-Deployment/HTTPS]] |
| 6 | Domains | [[07-Deployment/Domains]] |
| 7 | Environment Variables | [[07-Deployment/Environment-Variables]] |
| 8 | Production Checklist | [[07-Deployment/Production-Checklist]] |

**Milestone**: Your blog application is deployed on a VPS with HTTPS, served by Gunicorn behind Nginx, using environment variables for configuration.

---

## Phase 6: Security and Testing (Weeks 13-14)

### Security (Week 13)

| Order | Topic | File |
|-------|-------|------|
| 1 | Security Overview | [[08-Security/Security-Overview]] |
| 2 | CSRF Protection | [[08-Security/CSRF-Protection]] |
| 3 | XSS Prevention | [[08-Security/XSS-Prevention]] |
| 4 | SQL Injection | [[08-Security/SQL-Injection]] |
| 5 | Security Headers | [[08-Security/Security-Headers]] |
| 6 | Rate Limiting | [[08-Security/Rate-Limiting]] |
| 7 | Session Security | [[08-Security/Session-Security]] |

### Testing (Week 14)

| Order | Topic | File |
|-------|-------|------|
| 1 | Testing Overview | [[09-Testing/Testing-Overview]] |
| 2 | pytest Basics | [[09-Testing/pytest-Basics]] |
| 3 | Flask Test Client | [[09-Testing/Flask-Test-Client]] |
| 4 | Fixtures | [[09-Testing/Fixtures]] |
| 5 | Integration Testing | [[09-Testing/Integration-Testing]] |
| 6 | Mocking | [[09-Testing/Mocking]] |
| 7 | Test Coverage | [[09-Testing/Test-Coverage]] |

**Milestone**: Your application has comprehensive tests and is hardened against common web vulnerabilities.

---

## Phase 7: Advanced Topics (Weeks 15-16)

**Goal**: Master advanced Flask concepts and modern DevOps practices.

| Order | Topic | File | Difficulty |
|-------|-------|------|------------|
| 1 | Signals | [[10-Advanced/Signals]] | Intermediate |
| 2 | Middleware | [[10-Advanced/Middleware]] | Advanced |
| 3 | Caching | [[10-Advanced/Caching]] | Intermediate |
| 4 | Logging | [[10-Advanced/Logging]] | Intermediate |
| 5 | Async Flask | [[10-Advanced/Async-Flask]] | Advanced |
| 6 | REST API Development | [[10-Advanced/REST-API-Development]] | Intermediate |
| 7 | JWT Authentication | [[10-Advanced/JWT-Authentication]] | Intermediate |
| 8 | WebSockets | [[10-Advanced/WebSockets]] | Advanced |
| 9 | Docker | [[10-Advanced/Docker]] | Intermediate |
| 10 | CI/CD | [[10-Advanced/CI-CD]] | Intermediate |

**Milestone**: You can build and deploy production-grade Flask applications with caching, logging, containerization, and automated deployment pipelines.

---

## Extension Deep Dives

After completing the main chapters, study the [[Appendix]] for detailed coverage of every Flask extension:

| Extension | File | Purpose |
|-----------|------|---------|
| Flask | [[Appendix/Flask]] | The core framework |
| Werkzeug | [[Appendix/Werkzeug]] | WSGI utilities |
| Jinja2 | [[Appendix/Jinja2]] | Template engine |
| Flask-WTF | [[Appendix/Flask-WTF]] | Forms and CSRF |
| WTForms | [[Appendix/WTForms]] | Form validation |
| Flask-Login | [[Appendix/Flask-Login]] | User sessions |
| Flask-Mail | [[Appendix/Flask-Mail]] | Email sending |
| Flask-SQLAlchemy | [[Appendix/Flask-SQLAlchemy]] | Database ORM |
| SQLAlchemy | [[Appendix/SQLAlchemy]] | SQL toolkit |
| Alembic | [[Appendix/Alembic]] | Migrations engine |
| Flask-Migrate | [[Appendix/Flask-Migrate]] | Migration commands |
| Pillow | [[Appendix/Pillow]] | Image processing |
| email-validator | [[Appendix/email-validator]] | Email validation |
| itsdangerous | [[Appendix/itsdangerous]] | Data signing |
| Gunicorn | [[Appendix/Gunicorn]] | WSGI server |
| python-dotenv | [[Appendix/python-dotenv]] | Environment variables |

---

## Projects

Apply your knowledge with the structured projects in [[Projects]]:

1. **Personal Blog** — Complete blogging platform (follows Chapter 5)
2. **REST API Service** — JSON API with authentication (follows Chapter 10)
3. **Real-time Chat** — WebSocket-based messaging app (follows Chapter 10)
4. **Docker Deployment** — Containerized Flask application (follows Chapter 10)

---

## Time Estimate

| Phase | Duration | Daily Commitment |
|-------|----------|------------------|
| Phase 1 | 2 weeks | 1-2 hours |
| Phase 2 | 2 weeks | 1-2 hours |
| Phase 3 | 3 weeks | 2 hours |
| Phase 4 | 3 weeks | 2-3 hours |
| Phase 5 | 2 weeks | 2-3 hours |
| Phase 6 | 2 weeks | 2 hours |
| Phase 7 | 2 weeks | 2-3 hours |

**Total: 16 weeks (4 months)** at a comfortable pace.

> [!NOTE]
> This timeline assumes you are learning part-time. Full-time learners can compress this into 8-10 weeks.

---

## How to Track Progress

Mark chapters as complete in your Obsidian vault:

- `#in-progress` — Currently reading
- `#completed` — Finished with exercises
- `#review` — Needs revisiting

---

*Return to [[README]] | Browse the [[INDEX]]*