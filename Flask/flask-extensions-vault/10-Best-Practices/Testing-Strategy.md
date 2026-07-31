---
title: Testing Strategy
tags:
  - flask
  - testing
  - strategy
  - qa
  - ci
  - coverage
  - fixtures
  - mocking
  - test-pyramid
aliases:
  - Flask testing strategy
  - Flask test pyramid
  - Flask test plan
  - Flask CI testing
  - Flask flaky tests
related:
  - "[[Pytest-Flask]]"
  - "[[Flask-Testing]]"
  - "[[Factory-Boy]]"
  - "[[Performance-Optimization]]"
  - "[[Flask-SQLAlchemy]]"
  - "[[Security-Best-Practices]]"
  - "[[Production-Deployment]]"
created: 2024-01-15
updated: 2024-01-15
---

# Testing Strategy

#flask #testing #strategy #qa #ci #coverage #fixtures #mocking #test-pyramid

> [!info] The blueprint for a Flask test suite that scales
> [[Pytest-Flask]] and [[Flask-Testing]] cover the *tools* — fixtures, test client, assertion helpers. [[Factory-Boy]] covers the *test data*. This note covers the *strategy*: what to test, what to skip, how to isolate, how to design fixtures, what coverage numbers to aim for, how to wire the suite into CI, and how to keep tests from going flaky as the codebase grows. If the tool notes are the ingredients, this is the recipe.

A test suite is a **liability that earns its keep**. A good suite catches regressions before they ship, documents the system's intended behavior, and lets you refactor with confidence. A bad suite is a 30-minute wait between every commit, a wall of "random failures" that nobody investigates, and a pull request blocker that everyone learns to bypass with `[skip ci]`. The difference between the two is not the tools — it's the strategy. The same pytest can produce a 5-second suite that catches real bugs or a 5-minute suite that catches nothing.

> [!tip] The single most important metric
> Not coverage. Not test count. **Wall-clock time of the suite, run on every commit, on a developer's laptop.** If a developer can run `pytest` and get a green check in under 10 seconds, they will. If it takes 5 minutes, they won't — and the suite becomes a CI artifact instead of a development tool. Optimize for this number first; everything else follows.

---

## 1. Overview & Metaphor

### Why Flask apps need a testing strategy

A Flask app is a function from `request` to `response`. That sounds simple, but the inputs are HTTP requests (with headers, cookies, query strings, JSON bodies, file uploads), the function calls into your service layer, which calls into your ORM, which calls into PostgreSQL, and possibly into Redis, an external API, an S3 bucket, a Celery queue, and an email service. Every one of those is a possible test target — and a possible test failure. Without strategy, you end up testing everything end-to-end (slow, brittle) or nothing (regressions ship).

### The three questions a strategy answers

1. **What should I test?** Which layers, which behaviors, which edges.
2. **How should I test it?** Which tools, which fixtures, which isolation boundary.
3. **When should I run it?** Locally on save, on push, on PR, on merge, on deploy.

### Mermaid: the test pyramid for Flask

```mermaid
graph TD
    E2E["End-to-end / browser<br/>Playwright, Selenium<br/>slowest • fewest • brittle"]
    COMP["Component / contract<br/>external API mocks, real DB<br/>medium • medium"]
    INT["Integration<br/>test_client + real DB<br/>fast • many"]
    UNIT["Unit<br/>pure functions, model methods, schemas<br/>instant • hundreds"]
    E2E --> COMP --> INT --> UNIT
    style E2E fill:#f8d7da
    style COMP fill:#fff3cd
    style INT fill:#d1ecf1
    style UNIT fill:#d4edda
```

The pyramid says: **most** of your tests are unit tests (fast, isolated, deterministic). A **moderate** number are integration tests (exercise the seams between your code and Flask/SQLAlchemy). A **few** are end-to-end tests (slow, brittle, but the only ones that prove "the whole thing actually works for a user").

The pyramid is not a law; it's a heuristic. The flat shape (everything is integration tests) is what most Flask projects start with. The goal is to push *down* — extract pure functions from views, test them as units, and let the integration layer shrink.

### Mermaid: what to test at each layer

```mermaid
mindmap
  root((What to test))
    Unit
      Pure functions
        slugify
        parse_query
        compute_total
      Model methods
        User.full_name
        Post.is_published
        Order.can_be_cancelled
      Schema validation
        Marshmallow .load() raises on bad input
        Custom validators
      Service functions
        with mocked DB
        with mocked external APIs
    Integration
      View + DB
        POST /posts creates a row
        GET /users/404 returns 404
      Auth flow
        login → cookie set → /api works
      Form submission
        CSRF token validates
        Invalid input → 422 + errors
      Background task
        Celery task + DB
    Contract
      External API client
        Mock the upstream
        Assert request shape
        Assert response handling
      Webhook receiver
        Replay real payloads
    End-to-end
      Critical user journeys
        Signup → confirm email → first login
        Checkout → payment → receipt email
        Admin → suspend user → user can't login
```

### Mermaid: what NOT to test

```mermaid
mindmap
  root((Don't test))
    Framework itself
      Flask routes requests correctly
      Jinja2 renders templates
      SQLAlchemy commits work
    Third-party libraries
      Werkzeug password hashing
      Marshmallow field types
      Celery task queueing
    Trivial code
      Getters / setters
      Dataclass __init__
      Pure pass-throughs
    Untestable-by-design
      print debugging
      Side effects in __init__
      Time-based code without DI
```

If you're testing that Flask's `url_for` correctly builds a URL, you're testing Flask, not your app. Trust the framework; test your glue.

---

## 2. The Test Pyramid in Detail

### Unit tests — the foundation

A unit test exercises a single function or method in isolation. "Isolation" means: no database, no network, no filesystem, no time-dependent randomness. If the function takes inputs and returns outputs, the test passes inputs and asserts outputs.

```python
# app/services/pricing.py
def compute_total(items, tax_rate=0.0, discount=0.0):
    subtotal = sum(item["price"] * item["qty"] for item in items)
    discounted = subtotal * (1 - discount)
    return round(discounted * (1 + tax_rate), 2)

# tests/unit/test_pricing.py
def test_compute_total_with_tax_and_discount():
    items = [{"price": 10.00, "qty": 2}, {"price": 5.00, "qty": 1}]
    assert compute_total(items, tax_rate=0.08, discount=0.10) == 24.30

def test_compute_total_zero_items():
    assert compute_total([]) == 0.0

def test_compute_total_negative_discount_clamped():
    # Document the edge case — discounts above 100% shouldn't refund
    with pytest.raises(ValueError):
        compute_total([{"price": 10, "qty": 1}], discount=1.5)
```

These tests run in microseconds. They catch regressions in the pricing logic without spinning up Flask or PostgreSQL. The vast majority of your business logic should live in pure functions like this, *precisely* so it can be unit-tested.

### Integration tests — the middle layer

An integration test exercises multiple components together: a view function with the test client and a real (test) database, a Celery task with a real broker, a Marshmallow schema with a real model. These are slower (10-100ms each) but prove that the seams between your code work.

```python
# tests/integration/test_posts_api.py
def test_create_post_requires_auth(client):
    resp = client.post("/api/posts", json={"title": "Hello", "body": "World"})
    assert resp.status_code == 401

def test_create_post_validates_payload(client, auth_header):
    resp = client.post("/api/posts", json={"title": ""}, headers=auth_header)
    assert resp.status_code == 422
    assert "title" in resp.json["errors"]

def test_create_post_persists(client, auth_header, db_session):
    resp = client.post("/api/posts", json={"title": "Hello", "body": "World"}, headers=auth_header)
    assert resp.status_code == 201
    post_id = resp.json["id"]
    from app.models import Post
    assert Post.query.get(post_id).title == "Hello"
```

### End-to-end tests — the top of the pyramid

An end-to-end (E2E) test drives a real browser (Playwright, Selenium) against a running server with a real database, real Redis, and (mocked) external services. These are slow (5-30 seconds each) and brittle (browser timing, screenshot diffs). Reserve them for **critical user journeys** — signup, checkout, password reset — not for every page.

```python
# tests/e2e/test_signup.py
def test_signup_sends_confirmation_email(live_server, page, mailbox):
    page.goto(f"{live_server.url}/signup")
    page.fill("#email", "alice@example.com")
    page.fill("#password", "hunter2hunter2")
    page.click("button[type=submit]")
    page.wait_for_url("**/signup/pending")

    email = mailbox.wait_for_email(to="alice@example.com", timeout=10)
    assert "Confirm your account" in email.subject
    confirm_link = extract_link(email.body)
    page.goto(confirm_link)
    page.wait_for_url("**/dashboard")
```

### Mermaid: test lifecycle (single feature)

```mermaid
journey
    title Test lifecycle for a new feature: "user can upload avatar"
    section Write unit tests
      Test ImageResizer.resize returns 100x100: 5: Dev
      Test ImageResizer raises on non-image: 5: Dev
      Test validate_mime rejects executable: 5: Dev
    section Write integration tests
      Test POST /avatar requires auth: 5: Dev
      Test POST /avatar with valid image persists: 4: Dev
      Test POST /avatar with >5MB returns 413: 4: Dev
    section Write one E2E test
      Login → upload → see avatar in navbar: 3: Dev
    section Run locally
      pytest tests/unit/: 5: Dev
      pytest tests/integration/: 5: Dev
      pytest tests/e2e/test_avatar.py: 4: Dev
    section Push
      CI runs all three layers: 5: Team
      Coverage delta <0: 4: Team
    section Merge
      Green build merges: 5: Team
```

---

## 3. What to Test

### Models — test methods, not columns

Don't test that `User(email="x").email == "x"`. That's testing SQLAlchemy. **Do** test custom model methods:

```python
# app/models/user.py
class User(db.Model):
    # ...
    def can_access(self, resource):
        if self.is_admin:
            return True
        return resource.owner_id == self.id

    def display_name(self):
        return self.full_name or self.email.split("@")[0]

# tests/unit/test_user_model.py
def test_admin_can_access_anything():
    admin = User(is_admin=True)
    resource = Resource(owner_id=999)
    assert admin.can_access(resource)

def test_non_admin_cannot_access_others_resources():
    user = User(id=1, is_admin=False)
    resource = Resource(owner_id=999)
    assert not user.can_access(resource)

def test_display_name_falls_back_to_email_local_part():
    user = User(email="alice@example.com", full_name=None)
    assert user.display_name() == "alice"
```

These tests need a model instance but don't need DB persistence — `User(is_admin=True)` without `db.session.add()` works fine. Faster, simpler.

### Views — test behavior, not implementation

Test the *observable behavior* of a view: status code, response body, side effects (DB rows, sent emails). Don't test that the view "calls `PostService.create()`" — that's testing your call graph, which changes every refactor.

```python
def test_create_post_returns_201_with_post_data(client, auth_header):
    resp = client.post("/api/posts", json={"title": "Hi", "body": "World"}, headers=auth_header)
    assert resp.status_code == 201
    assert resp.json["title"] == "Hi"

def test_create_post_persists_to_db(client, auth_header, db_session):
    client.post("/api/posts", json={"title": "Hi", "body": "World"}, headers=auth_header)
    from app.models import Post
    assert Post.query.filter_by(title="Hi").count() == 1

def test_create_post_sends_notification(client, auth_header, mock_mailer):
    client.post("/api/posts", json={"title": "Hi", "body": "World"}, headers=auth_header)
    assert mock_mailer.called
    assert mock_mailer.calls[0]["subject"] == "New post published"
```

### API — test contracts

For APIs, treat the response shape as a contract. Assert every field the client expects:

```python
def test_post_response_shape(client, auth_header):
    post = PostFactory.create()
    resp = client.get(f"/api/posts/{post.id}", headers=auth_header)
    assert resp.status_code == 200
    body = resp.json
    assert set(body.keys()) >= {"id", "title", "body", "author", "created_at"}
    assert set(body["author"].keys()) == {"id", "display_name"}
    assert isinstance(body["id"], int)
    assert isinstance(body["created_at"], str)  # ISO 8601
```

If you change the response shape, these tests break — which is exactly what you want. Frontend developers can read the test file as the API contract.

### Templates — test rendering

For server-rendered apps, test that the right template renders with the right context:

```python
def test_post_list_renders_template(client):
    PostFactory.create_batch(3)
    resp = client.get("/posts")
    assert resp.status_code == 200
    assert b"<h1>Recent Posts</h1>" in resp.data
    assert resp.data.count(b"<article") == 3
```

For Jinja macros and partials, render them directly:

```python
def test_post_card_macro_renders_title_and_author():
    from app.templatetags import render_macro
    html = render_macro("macros/post_card.html", "post_card",
                        post=PostFactory.build(title="Hi", author=UserFactory.build()))
    assert "<h2>Hi</h2>" in html
```

### Background tasks — test the task body, not Celery

Don't test that Celery queues a task — test that the task body works:

```python
# tasks.py
@celery.task
def send_welcome_email(user_id):
    user = User.query.get(user_id)
    if user is None:
        return  # idempotent
    mailer.send(to=user.email, subject="Welcome", body="...")

# tests/unit/test_send_welcome_email.py
def test_send_welcome_email_sends_to_user(mock_mailer):
    user = UserFactory.create()
    send_welcome_email(user.id)
    assert mock_mailer.calls[0]["to"] == user.email

def test_send_welcome_email_silent_on_missing_user(mock_mailer):
    send_welcome_email(99999)  # no exception, no email
    assert not mock_mailer.called

def test_send_welcome_email_idempotent(mock_mailer):
    user = UserFactory.create()
    send_welcome_email(user.id)
    send_welcome_email(user.id)  # second call — depends on your idempotency design
```

For testing the *queueing* (eager mode, mocking `.delay`), see [[Celery]] §Testing.

---

## 4. Test Isolation

### The golden rule: tests must not affect each other

If running `test_a` before `test_b` makes `test_b` fail (or pass when it shouldn't), your suite is broken. Test isolation means each test starts from a known state and ends in a cleanable state.

Three sources of cross-test contamination:

1. **Database state.** Rows created by one test are visible to the next.
2. **In-memory state.** Module-level caches, `current_app` config mutated mid-test, `g.user` left over.
3. **External state.** Files written to disk, emails sent, messages published to a queue.

### Database isolation — the transactional fixture pattern

The cleanest pattern: wrap each test in a transaction that rolls back at the end. SQLAlchemy's `Session.begin_nested()` (a SAVEPOINT) is the primitive; pytest-flask-sqlalchemy provides it as a fixture.

```python
# tests/conftest.py
import pytest
from app import create_app, db as _db

@pytest.fixture(scope="session")
def app():
    app = create_app(testing=True)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope="function")
def db_session(app):
    """Each test gets a fresh transaction that rolls back at the end."""
    connection = _db.engine.connect()
    transaction = connection.begin()
    options = {"bind": connection, "binds": {}}
    session = _db.create_scoped_session(options=options)

    _db.session = session  # patch the global session

    yield session

    session.remove()
    transaction.rollback()
    connection.close()
```

Now any `db.session.add(...); db.session.commit()` inside a test runs in a savepoint; at teardown, the savepoint rolls back. The next test sees an empty database. Tests run in milliseconds because there's no schema drop/recreate.

> [!tip] The session-rollback pattern is the single biggest test speedup
> Most Flask test suites spend 90% of their time in `db.create_all()` / `db.drop_all()` cycles. Switching to the savepoint pattern cuts a 60-second suite to 6 seconds. It's the highest-leverage testing optimization in Flask.

### Mermaid: test isolation flow

```mermaid
sequenceDiagram
    participant Pytest
    participant Fixture
    participant DB
    participant Test
    Pytest->>Fixture: ask for `db_session`
    Fixture->>DB: BEGIN
    Fixture->>DB: SAVEPOINT
    Fixture-->>Test: inject session
    Test->>DB: INSERT user
    Test->>DB: INSERT post
    Test->>DB: SELECT (sees both rows)
    Test->>Test: assertions pass
    Test-->>Pytest: test done
    Pytest->>Fixture: teardown
    Fixture->>DB: ROLLBACK TO SAVEPOINT
    Fixture->>DB: RELEASE SAVEPOINT
    Fixture->>DB: ROLLBACK (outer)
    Note over DB: Database is empty for next test
```

### In-memory state isolation

For caches, globals, and `current_app` config:

```python
@pytest.fixture(autouse=True)
def reset_caches():
    """Clear any module-level caches before each test."""
    from app.services import caching
    caching.clear_all()
    yield
    caching.clear_all()
```

For `current_app.config` mutations:

```python
@pytest.fixture
def app_config(app):
    """Snapshot config so mutations don't leak to other tests."""
    original = dict(app.config)
    yield app.config
    app.config.clear()
    app.config.update(original)
```

### External state isolation

For emails, queues, file writes — use mocks or in-memory fakes:

```python
# tests/conftest.py
@pytest.fixture
def mock_mailer(monkeypatch):
    calls = []
    def fake_send(**kwargs):
        calls.append(kwargs)
    monkeypatch.setattr("app.services.mail.send", fake_send)
    return calls  # tests assert on the list
```

```python
@pytest.fixture
def tmp_upload_dir(tmp_path, monkeypatch):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    monkeypatch.setattr("app.config.UPLOAD_DIR", str(upload_dir))
    yield upload_dir
```

---

## 5. The Database in Tests

### Three strategies

| Strategy | Speed | Fidelity | When to use |
|---|---|---|---|
| SQLite in-memory | Fastest | Low — different SQL dialect, no concurrency | Small apps, unit tests with light DB use |
| PostgreSQL in Docker | Medium | High — same engine as prod | Anything beyond trivial |
| Testcontainers (ephemeral PG per session) | Medium | High — full isolation | CI, especially with parallel test workers |

### SQLite pitfalls

- No `ARRAY` type, no `JSONB`, no `INTERVAL`.
- No `CONCURRENTLY` — your migrations can't use it.
- No row-level locking; tests that depend on `SELECT ... FOR UPDATE` behave differently.
- Type coercion is loose — `User.query.filter_by(id="42")` works in SQLite, fails in PostgreSQL.

> [!warning] SQLite in tests, PostgreSQL in prod = false confidence
> A test suite that passes on SQLite can fail spectacularly on PostgreSQL. The classic case: a migration with `postgresql_concurrently=True` runs fine on SQLite (which ignores the kwarg) and dies on PostgreSQL (because there's no transaction). Run your test suite against PostgreSQL — at minimum in CI, ideally locally too. Docker makes this cheap.

### Docker PostgreSQL pattern

```yaml
# docker-compose.test.yml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app_test
    ports:
      - "55432:5432"  # non-default port to avoid clashing with dev
    tmpfs:
      - /var/lib/postgresql/data  # in-memory for speed
```

```python
# tests/conftest.py
import pytest
import testing.postgresql  # or testcontainers-python

@pytest.fixture(scope="session")
def postgres_url():
    with testing.postgresql.Postgresql() as pg:
        yield pg.url()

@pytest.fixture(scope="session")
def app(postgres_url):
    app = create_app(testing=True, sql_database_url=postgres_url)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()
```

---

## 6. Mocking External Services

### Rule: mock at the boundary, not deep inside

Mock the function that calls the external service, not the HTTP library two layers down:

```python
# GOOD — mock the service interface
@pytest.fixture
def mock_stripe(monkeypatch):
    class FakeStripe:
        def __init__(self):
            self.charges = []
        def create_charge(self, amount_cents, customer_id):
            self.charges.append({"amount": amount_cents, "customer": customer_id})
            return {"id": "ch_fake_123", "amount": amount_cents}
    fake = FakeStripe()
    monkeypatch.setattr("app.services.payments.stripe_client", fake)
    return fake

# BAD — mock requests.post and assert on URL strings
def test_charge_calls_stripe(monkeypatch):
    monkeypatch.setattr("requests.post", lambda url, **kw: MockResponse(...))
    # ... then assert that requests.post was called with "https://api.stripe.com/v1/charges"
    # This breaks if you switch from requests to httpx, or change the URL format.
```

### VCR / cassette pattern for real-shape mocks

For one-off integration tests where you want the *real* response shape (e.g., testing your Stripe webhook handler), use [vcrpy](https://vcrpy.readthedocs.io/):

```python
import vcr

@vcr.use_cassette("tests/cassettes/stripe_webhook.yaml")
def test_stripe_webhook_handler(client):
    payload = load_fixture("stripe_invoice_paid_event.json")
    resp = client.post("/webhooks/stripe", json=payload,
                       headers={"Stripe-Signature": "t=...,v1=..."})
    assert resp.status_code == 200
    # The cassette records the real Stripe API call on first run;
    # subsequent runs replay it without hitting Stripe.
```

The first run hits the real API and records the request/response to a YAML file. Subsequent runs replay the cassette — fast, deterministic, no API key needed in CI. Check the cassettes into git.

### Mermaid: mock layering

```mermaid
flowchart TD
    Test["Test function"] --> Svc["Service layer"]
    Svc -->|"uses via interface"| Stripe["StripeClient"]
    Stripe -.->|"mocked at this boundary"| FakeStripe["FakeStripe (in-memory)"]
    Stripe -.->|"or"| VCR["vcrpy cassette"]
    FakeStripe --> Assert["Test asserts on FakeStripe.charges"]
    VCR --> Assert

    Bad["❌ Bad: mock requests.post<br/>inside Service"] -.->|"breaks on refactor"| Bad
    style FakeStripe fill:#d4edda
    style VCR fill:#d4edda
    style Bad fill:#f8d7da
```

---

## 7. Fixture Design

### Fixtures are the API of your test suite

A test file with no fixtures — every test does its own setup — is unreadable. A test file with too many fixtures — every test pulls in five layers of magic — is un-understandable. Aim for the middle: a small set of composable fixtures, each doing one thing, named after what they provide.

### The fixture stack

A medium Flask app's fixture stack typically looks like:

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def app(postgres_url): ...

@pytest.fixture(scope="session")
def db(app): ...  # engine, metadata

@pytest.fixture(autouse=True)
def reset_caches(): ...

@pytest.fixture
def db_session(db): ...  # transactional, function scope

@pytest.fixture
def client(app, db_session): ...

@pytest.fixture
def user_factory(db_session): ...

@pytest.fixture
def user(user_factory): ...

@pytest.fixture
def admin(user_factory): ...

@pytest.fixture
def auth_header(user): ...

@pytest.fixture
def admin_auth_header(admin): ...

@pytest.fixture
def mock_mailer(monkeypatch): ...

@pytest.fixture
def mock_stripe(monkeypatch): ...
```

Each fixture builds on the ones above. Tests pull in only what they need:

```python
def test_anonymous_cannot_create_post(client):
    resp = client.post("/api/posts", json={...})
    assert resp.status_code == 401

def test_user_can_create_post(client, auth_header):
    resp = client.post("/api/posts", json={...}, headers=auth_header)
    assert resp.status_code == 201

def test_post_triggers_email(client, auth_header, mock_mailer):
    client.post("/api/posts", json={...}, headers=auth_header)
    assert mock_mailer.calls
```

### Fixture scopes

| Scope | When to use | Example |
|---|---|---|
| `session` | Expensive to build, never changes | `app`, `db` engine, Faker seed |
| `package` / `module` | Per-module setup (rare) | A heavy fixture only some test modules use |
| `class` | Shared by tests in a class (rare in pytest) | — |
| `function` | Default — fresh per test | `db_session`, `client`, `user`, mocks |

> [!tip] The `client` fixture should depend on `db_session`
> If `client` is session-scoped but `db_session` is function-scoped, the test client's requests will hit a stale session. Make `client` function-scoped, or have it depend on the session-scoped app and re-bind the session per test.

### Factory fixtures

Pair [[Factory-Boy]] factories with pytest fixtures:

```python
@pytest.fixture
def user_factory(db_session):
    """Returns the factory class. Tests call user_factory.create(...)."""
    return UserFactory

@pytest.fixture
def user(user_factory):
    """A default user — for tests that need exactly one."""
    return user_factory.create()
```

Tests that need a special user override:

```python
def test_banned_user_cannot_login(client, user_factory):
    user = user_factory.create(is_active=False, deleted_at=datetime.utcnow())
    resp = client.post("/login", json={"email": user.email, "password": "password"})
    assert resp.status_code == 403
```

---

## 8. Test Coverage Targets

### The 80% rule (and why 100% is a trap)

Aim for **80% line coverage** of meaningful code as a floor. Below 80%, you have untested code paths likely hiding bugs. Above 95%, you're testing boilerplate (`__init__`, getters) or writing contrived tests to hit branches that don't matter.

```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

The `term-missing` report shows which lines aren't covered:

```
Name                              Stmts   Miss  Cover   Missing
----------------------------------------------------------------
app/__init__.py                       5      0   100%
app/models/user.py                   42      3    93%   38-40
app/services/payments.py             87     12    86%   51, 78-89
app/views/admin.py                  103     41    60%   22-31, 55-90, 102-118
----------------------------------------------------------------
TOTAL                               820    112    86%
```

`app/views/admin.py` at 60% is the red flag. Either it's untested (bad), or it's dead code that should be deleted (also bad). Investigate.

### Branch coverage, not just line coverage

Line coverage counts executed lines. Branch coverage counts executed branches (if/else forks). A line-coverage report can show 100% on a function with an untested `else` branch:

```python
def get_role(user):
    if user.is_admin:
        return "admin"
    return "user"
```

Line coverage: 100% if you call `get_role(admin)`. Branch coverage: 50% — the `else` branch is never exercised.

```bash
pytest --cov=app --cov-branch --cov-report=term-missing
```

### Mermaid: coverage targets by code type

```mermaid
pie showData
    title Recommended coverage targets by code type
    "Business logic (services, models) — 95%+" : 35
    "API views — 90%+" : 25
    "Utility functions — 90%+" : 15
    "Configuration / glue — 70%" : 15
    "Error handlers / edge cases — 80%" : 10
```

Business logic deserves the highest coverage because bugs there cost the most. Glue code (e.g., `register_extensions(app)`) is hard to unit-test and low-value; an integration test that boots the app is enough.

### What coverage doesn't tell you

Coverage measures **which lines ran**, not **whether they did the right thing**. A test that calls `compute_total(items)` and asserts nothing still counts as coverage. **Coverage is necessary but not sufficient.** Always pair coverage with a human review of the tests: "would this test fail if I broke the function?"

---

## 9. CI/CD Testing Pipeline

### Mermaid: CI pipeline stages

```mermaid
flowchart TD
    Push["`git push`"] --> Lint["Lint: ruff / flake8<br/>+ black --check"]
    Lint --> Type["Type-check: mypy --strict"]
    Type --> Unit["Unit tests<br/>fast • no DB"]
    Unit --> Int["Integration tests<br/>PostgreSQL in Docker"]
    Int --> Migrations["Migration test<br/>flask db upgrade<br/>+ flask db downgrade -1"]
    Migrations --> Coverage["Coverage report<br/>+ delta vs main"]
    Coverage --> Security["Security scan<br/>pip-audit / bandit"]
    Security --> E2E["E2E tests<br/>only on PR to main"]
    E2E --> Deploy["Deploy to staging"]

    Lint -.->|fail| Fail["Block PR"]
    Type -.->|fail| Fail
    Unit -.->|fail| Fail
    Int -.->|fail| Fail
    Migrations -.->|fail| Fail
    Security -.->|fail| Fail

    style Unit fill:#d4edda
    style Int fill:#fff3cd
    style E2E fill:#f8d7da
    style Fail fill:#f8d7da
```

### Stage-by-stage

| Stage | Tool | Time budget | What it catches |
|---|---|---|---|
| Lint | ruff | <5s | Style violations, unused imports, common bugs |
| Type-check | mypy --strict | 10-30s | Type errors, None-safety, signature mismatches |
| Unit tests | pytest tests/unit/ | <30s | Logic bugs in services, models, schemas |
| Integration tests | pytest tests/integration/ | 1-3 min | View + DB + auth bugs |
| Migration test | `flask db upgrade && flask db downgrade -1` | 10s | Broken `downgrade()` functions |
| Coverage delta | diff-cover | <5s | New code without tests |
| Security scan | pip-audit, bandit | 10-30s | Known-vulnerable deps, common code patterns |
| E2E | Playwright | 5-10 min | User-journey regressions |

> [!tip] Stage gates are stronger than summary gates
> Don't run all tests in one big `pytest` invocation and gate on the result. Run unit, integration, and E2E as separate CI steps, each gating the next. A failure in unit tests should fail the build *before* you spend 5 minutes on E2E. This shaves minutes off the typical CI cycle.

### Parallelism

```bash
pytest -n auto  # pytest-xdist: one worker per CPU core
```

Each worker gets its own database (or schema, or savepoint scope) — without isolation, parallel tests corrupt each other's state. pytest-xdist handles worker fixtures, but you have to ensure your DB fixture is worker-local:

```python
@pytest.fixture(scope="session")
def postgres_url(worker_id):
    """Each xdist worker gets its own database."""
    db_name = f"app_test_{worker_id}"
    create_database(db_name)  # CREATE DATABASE in shared postgres
    yield f"postgresql://app:app@localhost/{db_name}"
    drop_database(db_name)
```

### Pre-merge vs post-merge

- **Pre-merge (PR):** lint, type-check, unit, integration, migration test, coverage delta. Should run in <5 min so developers get fast feedback.
- **Post-merge (main):** everything above + E2E + nightly security scans + performance benchmarks.
- **Nightly:** full suite against prod-like data, long-running tests that don't fit in PR cycle.

### Mermaid: CI wall-clock budget

```mermaid
gantt
    title CI pipeline wall-clock (target: <5 min pre-merge)
    dateFormat ss
    axisFormat %Ss
    section Fast
    Lint (ruff) :a1, 00, 05s
    Type-check (mypy) :a2, after a1, 20s
    section Medium
    Unit tests :b1, after a2, 25s
    Integration tests :b2, after b1, 120s
    Migration test :b3, after b2, 10s
    Coverage delta :b4, after b3, 05s
    section Slow (post-merge only)
    E2E (Playwright) :c1, after b4, 300s
    Security scan :c2, after c1, 30s
```

---

## 10. Flaky Test Prevention

A flaky test is one that passes sometimes and fails sometimes *without any code change*. Flaky tests destroy trust in the suite — within a month, developers stop investigating failures and just re-run until green.

### Sources of flakiness

| Source | Symptom | Fix |
|---|---|---|
| Time-based logic | Test passes at 2pm, fails at midnight | Inject a clock; never call `datetime.now()` directly |
| Order-dependent tests | Passes in isolation, fails in full suite | Test left rows in DB; add isolation fixtures |
| Floating-point comparison | `0.1 + 0.2 != 0.3` | Use `pytest.approx` or fixed-point decimals |
| External API calls | Fails when API is down or rate-limited | Mock the API; never hit real services in CI |
| Race conditions | Async code without proper synchronization | Use `pytest-asyncio` with deterministic event loops |
| Faker generating edge values | `Faker('email')` occasionally returns a 254-char string | Pin Faker seed; validate input before asserting |
| Filesystem state | Test reads `/tmp/foo` left by previous run | Use `tmp_path` fixture; never hard-code paths |
| Random.shuffle / random.random | Test asserts on order | Use `random.seed(0)` per test |

### The clock injection pattern

```python
# DON'T
def is_expired(token):
    return token.expires_at < datetime.utcnow()

# DO
def is_expired(token, now=None):
    now = now or datetime.utcnow()
    return token.expires_at < now

# Test
def test_is_expired_at_boundary():
    token = Token(expires_at=datetime(2024, 1, 1, 12, 0, 0))
    assert is_expired(token, now=datetime(2024, 1, 1, 12, 0, 1))
    assert not is_expired(token, now=datetime(2024, 1, 1, 11, 59, 59))
```

This makes the test 100% deterministic — no waiting for a specific time of day.

### The "retry until green" anti-pattern

```bash
# DON'T do this
pytest --retries 3
```

If a test is flaky, fix it. Retrying hides the flakiness and lets it accumulate. Within a month, you'll have 20 flaky tests and no signal.

> [!danger] Mark flaky tests with `@pytest.mark.flaky` only as a last resort
> pytest-rerunfailures provides `@pytest.mark.flaky(reruns=3)`. It's a useful escape hatch for genuinely nondeterministic tests (e.g., a race you can't fix in third-party code). But every `@flaky` marker is technical debt — schedule a ticket to fix it. If you have >5 flaky markers, your suite has a systemic problem.

### Mermaid: flaky test triage

```mermaid
flowchart TD
    Fail["Test failed in CI"] --> Local{"Reproduces locally?"}
    Local -->|yes| Debug["Real bug — fix code"]
    Local -->|"no, passes locally"| ReRun["Re-run in CI"]
    ReRun --> Pass2{"Passes on re-run?"}
    Pass2 -->|yes| Flaky["Flaky — investigate"]
    Pass2 -->|"no, consistent"| Debug2["CI-specific bug<br/>(timing, env, parallelism)"]
    Flaky --> Time{Time-dependent?}
    Time -->|yes| InjectClock["Inject a clock fixture"]
    Time -->|no| Order{Order-dependent?}
    Order -->|yes| Isolate["Add isolation fixture"]
    Order -->|no| Ext{Hits external service?}
    Ext -->|yes| Mock["Mock the service"]
    Ext -->|no| Random{Uses randomness?}
    Random -->|yes| Seed["Seed Faker / random"]
    Random -->|no| Deep["Deep dive:<br/>logging, async, threads"]

    style Debug fill:#d4edda
    style InjectClock fill:#d4edda
    style Isolate fill:#d4edda
    style Mock fill:#d4edda
    style Seed fill:#d4edda
    style Deep fill:#f8d7da
```

---

## 11. Common Patterns

### Pattern: snapshot testing for stable outputs

For responses with many fields, snapshot testing avoids re-typing every assertion:

```python
# pip install syrupy
def test_post_response_shape(client, auth_header, snapshot):
    post = PostFactory.create()
    resp = client.get(f"/api/posts/{post.id}", headers=auth_header)
    assert resp.json == snapshot
```

First run: writes `test_post_response_shape.ambr` with the actual response. Subsequent runs: diffs the response against the snapshot. To update snapshots: `pytest --snapshot-update`.

### Pattern: parametrized tests for matrix coverage

```python
@pytest.mark.parametrize("role,expected_status", [
    ("anonymous", 401),
    ("user", 403),
    ("editor", 200),
    ("admin", 200),
])
def test_admin_endpoint_access(client, auth_header_for_role, role, expected_status):
    headers = auth_header_for_role(role)
    resp = client.get("/admin/dashboard", headers=headers)
    assert resp.status_code == expected_status
```

One test function, four cases. CI reports each as a separate row, so a single failing role is obvious.

### Pattern: golden master for complex outputs

For things like generated PDFs, HTML reports, or large JSON payloads, save a "golden master" and diff against it:

```python
def test_invoice_pdf_matches_golden(client, snapshot_pdf):
    resp = client.get("/invoices/42.pdf")
    assert resp.data == snapshot_pdf("invoice_42.pdf")
```

Update the golden master with `--snapshot-update` after a deliberate change.

### Pattern: contract testing for external APIs

If your app calls another service, write a contract test that runs against the real service in a staging environment (separate from your unit tests). Daily CI verifies the contract still holds; PRs run mocked tests against the cached contract.

---

## 12. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Tests pass locally, fail in CI | Different DB engine, missing env var, parallel worker corruption | Run CI's `pytest` command locally; check engine; ensure worker isolation |
| Test suite takes >2 min | DB create/drop per test; too many integration tests; no parallelism | Switch to transactional fixtures; extract units; use pytest-xdist |
| Coverage stuck at 60% | Dead code, untested branches, or `# pragma: no cover` everywhere | Run `--cov-report=term-missing`, target the largest gaps |
| Flaky test rate >1% | Time-based logic, order dependency, external calls | Apply the patterns in §10 |
| New tests don't get written | Setup is painful, no factory pattern, no fixtures | Invest in `conftest.py`; pair with [[Factory-Boy]] |
| Tests are brittle to refactors | Tests assert on implementation (call counts, internal state) | Rewrite to assert on observable behavior (responses, DB state) |
| E2E tests flake on browser timing | `page.click` racing with JS rendering | Use Playwright's auto-waiting; assert on URL/text, not on absence of spinner |
| Migration tests fail in CI but not locally | Local DB has stale state | Drop and recreate test DB; ensure CI starts from empty |

---

## 13. Best Practices

> [!tip] Testing strategy checklist
> 1. **Optimize for wall-clock first.** A 5-second suite gets run on every save; a 5-minute suite gets skipped.
> 2. **Push tests down the pyramid.** Extract pure functions from views; test them as units.
> 3. **Test behavior, not implementation.** Assert on responses and DB state, not call counts.
> 4. **Isolate via transactional fixtures.** The single biggest speedup in Flask.
> 5. **Mock at boundaries.** Mock the service interface, not `requests.post`.
> 6. **Pin Faker and seed it.** Deterministic tests are reproducible tests.
> 7. **Target 80% meaningful coverage.** Don't chase 100%; investigate gaps, not totals.
> 8. **Run unit + integration separately in CI.** Faster feedback, clearer failures.
> 9. **Treat flaky tests as bugs.** Fix them or quarantine them; don't retry.
> 10. **Inject a clock.** Never call `datetime.now()` directly in code under test.
> 11. **Test migrations in both directions.** `upgrade → downgrade → upgrade` in CI.
> 12. **Use the production DB engine in tests.** SQLite hides bugs.
> 13. **E2E for critical journeys only.** 5-10 E2E tests, not 100.
> 14. **Document the test suite.** New developers should know which fixtures exist and when to use which.

---

## 14. Related Vault Notes

- [[Pytest-Flask]] — the recommended test runner; provides `app`, `client`, `cli`, `live_server` fixtures and pytest's full fixture/parametrization machinery
- [[Flask-Testing]] — legacy `unittest`-style alternative; same testing strategy applies, different tools
- [[Factory-Boy]] — declarative test-data factories; pair with pytest fixtures for the recommended pattern
- [[Performance-Optimization]] — test suite performance is itself a performance problem; the same profiling mindset applies
- [[Flask-SQLAlchemy]] — the ORM whose models factories build and whose session needs per-test isolation
- [[Security-Best-Practices]] — security-specific tests (auth bypass, IDOR, CSRF) deserve their own category in the test plan
- [[Production-Deployment]] — the CI pipeline this strategy plugs into; deploy gating, blue-green, and rollback testing
