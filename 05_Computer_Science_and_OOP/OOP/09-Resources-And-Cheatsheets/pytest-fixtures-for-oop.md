---
title: pytest Fixtures for OOP
tags:
  - oop
  - testing
  - pytest
  - fixtures
  - dependency-injection
aliases:
  - pytest Fixtures
  - Fixtures for Classes
  - conftest Patterns
created: 2025-01-20
---

> [!note] Why this note exists
> In [[testing-oop-code]] we said *"fixtures ARE dependency injection."* This note takes that idea seriously. We treat pytest's fixture machinery as a real DI container and explore how its features — scopes, composition, factories, params, `yield` — map onto the design challenges of testing object-oriented code: shared expensive resources, polymorphic hierarchies, mutable state, and complex object graphs.

Related: [[testing-oop-code]], [[exception-handling-in-oop]], [[solid-principles#Dependency Inversion Principle DIP]], [[composition-over-inheritance]], [[best-practices]], [[common-pitfalls-and-anti-patterns]], [[what-is-oop]].

---

## 1. Fixtures as the bridge between OOP design and testing

A class under test is rarely alone. It depends on collaborators (repositories, gateways, clocks, factories, policies). In production, those collaborators are wired up by your application's composition root. In tests, **pytest is the composition root**.

```mermaid
flowchart TB
    subgraph Production
        PC[Composition Root<br/>DI container / main]
        PC --> P1[RealDatabase]
        PC --> P2[RealClock]
        PC --> P3[OrderService<br/>uses Database + Clock]
    end
    subgraph Test
        TC[pytest fixture graph]
        TC --> T1[FakeDatabase<br/>fixture]
        TC --> T2[FrozenClock<br/>fixture]
        TC --> T3[OrderService<br/>fixture: takes Fake + Frozen]
        T3 --> T4[test_checkout_records_correct_timestamp]
    end
```

Three properties make this work:

1. **Declaration by parameter name.** The test declares what it needs; pytest supplies it. This is *constructor injection for functions*.
2. **Caching by scope.** A fixture's result can be reused across many tests, removing redundant setup without leaking global state.
3. **Composition.** A fixture can take other fixtures as parameters — the same way one class's constructor takes other classes. The graph is built bottom-up by pytest.

> [!tip] The DI correspondence
> | pytest concept | DI / OOP concept |
> |---|---|
> | fixture function | provider / factory |
> | test function declaring a fixture param | constructor injection |
> | `conftest.py` | composition root / DI container config |
> | fixture scope | singleton vs transient lifecycle |
> | parametrized fixture | provider that yields many instances |

---

## 2. Fixture scopes: function, class, module, session

Scope controls **how often** the fixture runs. Pick the smallest scope that still gives acceptable performance.

| Scope | Created | Torn down | Use for |
|---|---|---|---|
| `function` (default) | Once per test function | After each test | Most objects: carts, accounts, value objects, mocks |
| `class` | Once per test class | After last test in class | Shared setup for a group of related tests |
| `module` | Once per test file | After all tests in file | Expensive objects reused across one file |
| `session` | Once per pytest run | At interpreter exit | Truly expensive resources: DB connection, web server, schema setup |

```python
import pytest

@pytest.fixture
def function_scoped():
    return []  # fresh list per test

@pytest.fixture(scope="class")
def class_scoped():
    return {"created_at": "once-per-class"}

@pytest.fixture(scope="module")
def module_scoped():
    return {"created_at": "once-per-module"}

@pytest.fixture(scope="session")
def session_scoped():
    return {"created_at": "once-per-session"}
```

> [!warning] Scope widening is a one-way street
> A higher-scope fixture can depend on a lower-scope fixture (e.g. a `session` fixture using a `function` fixture is impossible — pytest will refuse). The rule is: **the dependent's scope must be ≥ the dependency's scope**. Equivalently, "a long-lived object cannot hold a reference to a short-lived one."

```mermaid
flowchart LR
    SESSION[session] --> MODULE[module]
    MODULE --> CLASS[class]
    CLASS --> FUNCTION[function]
    style SESSION fill:#fcd
    style MODULE fill:#fce
    style CLASS fill:#fde
    style FUNCTION fill:#fef
```

A `function`-scoped fixture can use anything. A `session`-scoped fixture can only use other `session`-scoped fixtures.

---

## 3. `conftest.py`: the composition root of your tests

`conftest.py` is a special file pytest auto-loads. Fixtures defined there are available to every test in the same directory and below — **without imports**. This is your test-side composition root.

```
project/
├─ src/
│  └─ shop/
│     ├─ cart.py
│     ├─ repository.py
│     └─ pricing.py
└─ tests/
   ├─ conftest.py            ← root: shared fixtures for the whole suite
   ├─ shop/
   │  ├─ conftest.py         ← shared fixtures for shop tests only
   │  ├─ test_cart.py
   │  └─ test_repository.py
   └─ test_smoke.py
```

### 3.1 A typical root `conftest.py`

```python
# tests/conftest.py
from __future__ import annotations
import pytest
from datetime import datetime

from src.shop.repository import Repository
from tests.fakes import InMemoryRepository


@pytest.fixture
def frozen_clock():
    """A callable clock so tests can advance time explicitly."""
    state = {"now": datetime(2024, 1, 1, 9, 0, 0)}

    class _Clock:
        def now(self) -> datetime:
            return state["now"]
        def advance(self, **kwargs) -> None:
            state["now"] = state["now"].replace(**{k: state["now"].timetuple().__getattribute__("_replace") and v for k, v in kwargs.items()})  # simplified below
        def set(self, value: datetime) -> None:
            state["now"] = value

    return _Clock()


@pytest.fixture
def repo() -> Repository:
    return InMemoryRepository()
```

> [!example] A simpler fake clock (clean version)
> ```python
> @pytest.fixture
> def frozen_clock():
>     class _Clock:
>         def __init__(self):
>             self.now_value = datetime(2024, 1, 1, 9, 0, 0)
>         def now(self) -> datetime:
>             return self.now_value
>         def advance(self, days: int = 0) -> None:
>             from datetime import timedelta
>             self.now_value += timedelta(days=days)
>     return _Clock()
> ```
> Use this pattern — never mind the convoluted one above, which is intentionally a reminder to keep fakes *simple*.

### 3.2 Local `conftest.py`

A `tests/shop/conftest.py` can add fixtures that only `tests/shop/` sees — for example, a domain-specific `product_catalog` fixture. The root `conftest.py` does not see them, keeping the root clean.

> [!tip] Don't import fixtures; let pytest find them
> Fixtures in `conftest.py` are picked up automatically. Importing them explicitly works but breaks the "no-import" rule and confuses readers. Treat `conftest.py` as the DI configuration — pytest reads it for you.

---

## 4. Fixture composition and dependency injection

A fixture can declare other fixtures as parameters. pytest resolves the graph in dependency order.

```python
import pytest
from src.shop.cart import ShoppingCart
from src.shop.repository import Repository
from src.shop.pricing import PricingPolicy, StandardPricing


@pytest.fixture
def catalog() -> dict[str, int]:
    return {"book": 1200, "pen": 150}


@pytest.fixture
def pricing() -> PricingPolicy:
    return StandardPricing()


@pytest.fixture
def cart(catalog, pricing) -> ShoppingCart:
    # ↑ takes two other fixtures; pytest builds them first.
    return ShoppingCart(catalog=catalog, pricing=pricing)


def test_empty_cart(cart: ShoppingCart):
    assert cart.total() == 0


def test_add_then_total(cart: ShoppingCart):
    cart.add("book", qty=2)
    assert cart.total() == 2400
```

### The dependency graph

```mermaid
flowchart TB
    CAT[fixture catalog] --> CART[fixture cart]
    PRICE[fixture pricing] --> CART
    REPO[fixture repo] --> CART
    CART --> T1[test_empty_cart]
    CART --> T2[test_add_then_total]
    style CAT fill:#bef
    style PRICE fill:#bef
    style REPO fill:#bef
    style CART fill:#bef
    style T1 fill:#fde
    style T2 fill:#fde
```

> [!note] The power of composition
> Because fixtures compose, the *structure* of your test setup mirrors the *structure* of your object graph. When a constructor changes, you update one fixture and every dependent fixture (and every test) is automatically correct. This is the same reason [[composition-over-inheritance]] scales in production code.

---

## 5. Parametrized fixtures for polymorphic hierarchies

A single fixture can be **parametrized** to yield multiple values. Combined with the contract-test pattern from [[testing-oop-code#Testing class hierarchies]], this lets you write the *same* test once and run it against every subtype.

```python
import pytest
from src.shapes import Shape, Circle, Square, Triangle


@pytest.fixture(params=[
    Circle(1),
    Square(2),
    Triangle(base=2, height=3),
], ids=lambda s: type(s).__name__)
def shape(request) -> Shape:
    return request.param


def test_area_is_positive(shape: Shape):
    assert shape.area() > 0


def test_perimeter_is_positive(shape: Shape):
    assert shape.perimeter() > 0
```

The `ids` argument makes the test report readable: `test_area_is_positive[Circle]`, `test_area_is_positive[Square]`, etc.

### The shared fixture pattern for hierarchies

A more powerful pattern: parametrize a *factory* fixture, then have higher-level fixtures build on top.

```python
@pytest.fixture(params=["circle", "square", "triangle"])
def shape_factory(request):
    """Returns a callable that builds a fresh shape with a given size."""
    builders = {
        "circle":   lambda size: Circle(size),
        "square":   lambda size: Square(size),
        "triangle": lambda size: Triangle(base=size, height=size),
    }
    return builders[request.param]


def test_doubling_size_changes_area(shape_factory):
    small = shape_factory(1)
    big = shape_factory(2)
    # For all three shapes, doubling the size multiplies area by 4 (circles and squares)
    # or by 4 (triangles with base==height scaled together).
    assert big.area() == pytest.approx(4 * small.area(), rel=1e-6)
```

> [!tip] Why this is so valuable
> Adding a new shape (`Hexagon`) means adding one entry to `params`. Every test that uses the parametrized fixture now also runs against `Hexagon` — automatically. This is the testing analog of [[composition-over-injection]] and the Open/Closed Principle.

---

## 6. Factory fixtures: `@pytest.fixture` returning a function

Sometimes a test needs **multiple instances** of the same object, or instances configured differently per assertion. A *factory fixture* is a fixture that returns a builder function rather than an object.

```python
import pytest
from src.shop.cart import ShoppingCart

@pytest.fixture
def make_cart(catalog):
    """Returns a factory. Tests call make_cart() to get a fresh cart."""
    created: list[ShoppingCart] = []

    def _build(discount: float = 0.0) -> ShoppingCart:
        c = ShoppingCart(catalog=catalog, discount=discount)
        created.append(c)
        return c

    # expose the list of created carts for advanced introspection if needed
    _build.all_created = created  # type: ignore[attr-defined]
    return _build


def test_multiple_carts_independent(make_cart):
    c1 = make_cart()
    c2 = make_cart()
    c1.add("book", qty=1)
    assert c2.total() == 0  # carts do not share state


def test_discounted_cart(make_cart):
    c = make_cart(discount=0.10)
    c.add("book", qty=1)  # 1200 cents
    assert c.total() == 1080  # 10% off
```

> [!example] Factory vs parametrized fixture — when to use which
> - **Parametrized fixture** — the *same* test logic against many pre-built instances. Best for contract tests.
> - **Factory fixture** — the test needs to *create* multiple instances itself, with control over construction. Best for interaction tests.

### Factory + cleanup pattern

If your factory creates resources that need teardown, attach the cleanup to the fixture using `yield`.

```python
@pytest.fixture
def make_temp_repo(tmp_path):
    created = []
    def _build():
        from src.shop.repository import SqliteRepository
        path = tmp_path / f"db_{len(created)}.sqlite"
        repo = SqliteRepository(path)
        created.append(repo)
        return repo
    yield _build
    for r in created:
        r.close()
```

---

## 7. Session-scoped fixtures for expensive resources

Some resources are too expensive to recreate per test: a real PostgreSQL connection, a schema migration, a seeded dataset, an in-process web server. Use `scope="session"`.

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.shop.orm import Base


@pytest.fixture(scope="session")
def engine():
    """One engine for the whole session. Created once, torn down at exit."""
    e = create_engine("postgresql://test:test@localhost/test_shop", echo=False)
    Base.metadata.create_all(e)
    yield e
    Base.metadata.drop_all(e)
    e.dispose()


@pytest.fixture(scope="session")
def session_factory(engine):
    return sessionmaker(bind=engine)


@pytest.fixture
def db_session(session_factory):
    """Function-scoped: each test gets a fresh transaction it can roll back."""
    Session = session_factory()
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
```

> [!danger] Don't share mutable state across function-scoped tests
> If `db_session` were `session`-scoped, every test would see the previous test's inserts — and tests would become order-dependent. The pattern above (session-scoped engine, function-scoped session that rolls back) gives both speed **and** isolation.

### The "transactional test" pattern

The combination above is the standard SQLAlchemy pattern: a long-lived engine + per-test transaction that always rolls back. Variants exist for Django (`TestCase`), pytest-django (`django_db(transaction=False)`), and others — all built on the same idea.

```mermaid
sequenceDiagram
    participant T as Test function
    participant F as db_session fixture
    participant E as session engine
    participant DB as PostgreSQL

    T->>F: request db_session
    F->>E: open session
    E->>DB: BEGIN
    F-->>T: yield session
    T->>F: do INSERTs, UPDATEs
    F->>DB: ROLLBACK (cleanup)
    F-->>T: test passes
    Note over E,DB: Engine & schema persist<br/>for next test
```

---

## 8. `yield` fixtures for setup and teardown

`yield` fixtures let you run setup *before* the test and teardown *after* — even if the test raises.

```python
import pytest
from src.shop.audit import AuditLog


@pytest.fixture
def audit_file(tmp_path):
    path = tmp_path / "audit.log"
    log = AuditLog(path)
    log.open()
    yield log
    log.close()  # always runs, even if the test raised


def test_writes_an_entry(audit_file):
    audit_file.record("hello")
    assert audit_file.read() == ["hello"]
```

> [!tip] Multiple `yield`? No.
> A fixture can only `yield` once. For complex teardown order, use `addfinalizer` on `request` or split into multiple composed fixtures.

### `addfinalizer` alternative

```python
@pytest.fixture
def audit_file(request, tmp_path):
    path = tmp_path / "audit.log"
    log = AuditLog(path)
    log.open()
    request.addfinalizer(log.close)
    return log
```

Prefer `yield` for readability; use `addfinalizer` only when you must register teardown conditionally inside a factory.

### Teardown ordering

When multiple `yield` fixtures are used, teardown runs in **reverse order** of setup (LIFO) — like nested `with` blocks. This matches the "stack" intuition: the last thing opened is the first thing closed.

---

## 9. Worked example: testing a `Repository` hierarchy with shared fixtures

### 9.1 The domain

```python
# src/shop/repository.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class NotFound(Exception): ...

class Repository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T) -> None: ...
    @abstractmethod
    def get(self, id: str) -> Optional[T]: ...
    @abstractmethod
    def delete(self, id: str) -> None: ...
    @abstractmethod
    def all(self) -> list[T]: ...


# src/shop/product.py
from dataclasses import dataclass
@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price_cents: int
```

### 9.2 Two implementations

```python
# src/shop/sqlite_repo.py
import sqlite3
from src.shop.repository import Repository, NotFound
from src.shop.product import Product


class SqliteProductRepository(Repository[Product]):
    def __init__(self, path: str) -> None:
        self._conn = sqlite3.connect(path)
        self._conn.execute("CREATE TABLE IF NOT EXISTS products (sku TEXT PRIMARY KEY, name TEXT, price_cents INTEGER)")
        self._conn.commit()

    def add(self, entity: Product) -> None:
        self._conn.execute("INSERT OR REPLACE INTO products VALUES (?,?,?)",
                           (entity.sku, entity.name, entity.price_cents))
        self._conn.commit()

    def get(self, id: str) -> Product | None:
        row = self._conn.execute("SELECT sku, name, price_cents FROM products WHERE sku=?", (id,)).fetchone()
        return Product(*row) if row else None

    def delete(self, id: str) -> None:
        self._conn.execute("DELETE FROM products WHERE sku=?", (id,))
        self._conn.commit()

    def all(self) -> list[Product]:
        return [Product(*row) for row in self._conn.execute("SELECT sku, name, price_cents FROM products")]

    def close(self) -> None:
        self._conn.close()


# tests/fakes.py
class InMemoryProductRepository(Repository[Product]):
    def __init__(self) -> None:
        self._store: dict[str, Product] = {}
    def add(self, entity: Product) -> None:
        self._store[entity.sku] = entity
    def get(self, id: str) -> Product | None:
        return self._store.get(id)
    def delete(self, id: str) -> None:
        self._store.pop(id, None)
    def all(self) -> list[Product]:
        return list(self._store.values())
```

### 9.3 The shared contract test, parametrized over both implementations

```python
# tests/conftest.py
import pytest
from src.shop.product import Product
from src.shop.repository import Repository
from tests.fakes import InMemoryProductRepository


@pytest.fixture(params=["inmemory", "sqlite"], ids=lambda x: x)
def repo_factory(request, tmp_path):
    """Returns a callable that builds a fresh Repository[Product]."""
    if request.param == "inmemory":
        def _build() -> Repository[Product]:
            return InMemoryProductRepository()
        return _build
    elif request.param == "sqlite":
        from src.shop.sqlite_repo import SqliteProductRepository
        def _build() -> Repository[Product]:
            return SqliteProductRepository(str(tmp_path / f"db_{request.node.name}.sqlite"))
        return _build


@pytest.fixture
def sample_product() -> Product:
    return Product(sku="BOOK-1", name="The Pragmatic Programmer", price_cents=2999)
```

```python
# tests/test_repository_contract.py
import pytest
from src.shop.repository import Repository
from src.shop.product import Product


class TestRepositoryContract:
    def test_get_unknown_returns_none(self, repo_factory):
        repo = repo_factory()
        assert repo.get("missing") is None

    def test_add_then_get_roundtrip(self, repo_factory, sample_product):
        repo = repo_factory()
        repo.add(sample_product)
        assert repo.get(sample_product.sku) == sample_product

    def test_delete_removes(self, repo_factory, sample_product):
        repo = repo_factory()
        repo.add(sample_product)
        repo.delete(sample_product.sku)
        assert repo.get(sample_product.sku) is None

    def test_all_returns_every_added(self, repo_factory):
        repo = repo_factory()
        p1 = Product("A", "Alpha", 100)
        p2 = Product("B", "Beta", 200)
        repo.add(p1); repo.add(p2)
        result = sorted(repo.all(), key=lambda p: p.sku)
        assert result == [p1, p2]

    def test_add_overwrites_on_same_sku(self, repo_factory):
        repo = repo_factory()
        repo.add(Product("A", "Alpha", 100))
        repo.add(Product("A", "Alpha+", 200))
        assert repo.get("A").price_cents == 200
```

> [!example] The payoff
> `repo_factory` runs each test **twice**: once against the in-memory fake, once against the real SQLite implementation. If SQLite breaks the contract (e.g. its `INTEGER` column silently truncates a huge number), the test fails on the `[sqlite]` variant and tells you instantly. The in-memory fake has just become a *reference implementation* — extremely valuable when you're not 100% sure your real backend honors the interface.

### 9.4 The fixture graph for the contract test

```mermaid
flowchart TB
    TMP[fixture tmp_path<br/>built-in] --> RF[fixture repo_factory<br/>parametrized: inmemory, sqlite]
    RF --> T1[test_get_unknown_returns_none]
    RF --> T2[test_add_then_get_roundtrip]
    SP[fixture sample_product] --> T2
    SP --> T3[test_delete_removes]
    RF --> T3
    style TMP fill:#bef
    style RF fill:#bef
    style SP fill:#bef
    style T1 fill:#fde
    style T2 fill:#fde
    style T3 fill:#fde
```

---

## 10. Common pitfalls

### 10.1 Scope mistakes

> [!danger] Using `scope="session"` for stateful objects
> A `session`-scoped cart, repository, or user object accumulates state across tests. The first test passes; the second fails because it sees leftover state from the first. **Default to `function` scope** and widen only with deliberate reason.

```python
# ❌ Bad: a cart shared across the whole session
@pytest.fixture(scope="session")
def cart(catalog):
    return ShoppingCart(catalog)

# ✅ Good: fresh cart per test
@pytest.fixture
def cart(catalog):
    return ShoppingCart(catalog)
```

### 10.2 Shared mutable state across tests

Even with `function` scope, *transitive* sharing can bite you. If fixture A (function-scoped) holds a reference to fixture B (session-scoped) that's mutable, mutating A might mutate B.

```python
# ❌ Bad: session-scoped list reused
@pytest.fixture(scope="session")
def shared_log():
    return []

@pytest.fixture
def auditor(shared_log):
    return Auditor(shared_log)  # each Auditor mutates the SAME list

def test_one_writes(auditor):
    auditor.record("first")
    # if test_two runs after, it sees "first" via shared_log
```

Fix: prefer immutability, copy-on-read, or per-test snapshots.

### 10.3 Fixture that returns `None` by accident

Forgetting `return` (or using `yield` without returning a value) makes the fixture silently `None`. The test then fails with a confusing `AttributeError` deep inside the SUT.

```python
# ❌ Bad
@pytest.fixture
def catalog():
    {"book": 10}  # expression statement, not a return

# ✅ Good
@pytest.fixture
def catalog():
    return {"book": 10}
```

> [!tip] Lint your fixtures with `mypy` or `ruff`
> Static checkers catch `None`-returning fixtures because the type annotation on the test parameter won't match. Always annotate fixture return types.

### 10.4 Over-using `autouse`

`autouse=True` runs a fixture for every test in scope, even ones that don't need it. This hides dependencies and slows tests. Reserve `autouse` for genuinely universal setup (e.g. resetting a singleton between tests) and prefer explicit declaration everywhere else.

### 10.5 Fixture name collisions

Two fixtures with the same name (one in root `conftest.py`, one in a deeper `conftest.py`) shadow each other — the deeper one wins. This is *intended* (allows overriding), but it's confusing. Document overrides explicitly with a comment.

### 10.6 Patching inside a fixture without unpatching

If a fixture uses `unittest.mock.patch` directly (not as a decorator or context manager), the patch leaks past the fixture's lifetime. Always use `with patch(...)` or `yield` + `patch.stopall()`.

```python
# ❌ Bad: leaks patch
@pytest.fixture
def fake_clock():
    patcher = patch("src.shop.clock.Clock.now", return_value=datetime(2024,1,1))
    patcher.start()
    # forgot .stop()!

# ✅ Good
@pytest.fixture
def fake_clock():
    with patch("src.shop.clock.Clock.now", return_value=datetime(2024,1,1)) as m:
        yield m
```

---

## Key Takeaways

1. **pytest is your test-side composition root.** Fixtures are providers; tests are consumers; `conftest.py` is the DI configuration.
2. **Choose the smallest scope that performs.** Default `function`; widen only for genuinely expensive resources.
3. **`conftest.py` fixtures are auto-discovered.** Don't import them — that defeats the design and confuses readers.
4. **Compose fixtures like you compose objects.** A fixture's parameters declare its dependencies; pytest builds the graph bottom-up.
5. **Parametrized fixtures = polymorphic test suites.** One fixture, many subtypes → contract tests run against every implementation automatically.
6. **Factory fixtures return functions.** Use them when the test needs to create multiple instances or control construction.
7. **Session-scoped engine, function-scoped session, always rollback.** The standard pattern for fast, isolated DB tests.
8. **`yield` for teardown, in LIFO order.** Use `addfinalizer` only for conditional teardown in factories.
9. **Beware shared mutable state.** Transitive dependencies on session-scoped mutable objects are the most common cause of order-dependent failures.

---

## Practice Exercises

> [!example] Exercise 1 — Scope the fixture correctly
> A `user` fixture returns a fresh `User` object. Decide the scope: function, class, module, or session. Justify your choice. Then describe a scenario where widening to `module` *would* be acceptable.

> [!example] Exercise 2 — Parametrize over implementations
> Given an `EmailSender` interface with `SmtpSender` (real, slow) and `ConsoleSender` (fake, fast) implementations, write a parametrized fixture `sender_factory` and three contract tests that pass for both. Add an `ids=` so the report shows `[SmtpSender]` / `[ConsoleSender]`.

> [!example] Exercise 3 — Factory fixture with cleanup
> Write a `make_temp_workspace` factory fixture that creates a fresh temporary directory under `tmp_path`, returns a `Workspace` object bound to it, and removes the directory in teardown. Demonstrate with a test that creates three workspaces and asserts they are independent.

> [!example] Exercise 4 — Replace a mock-heavy test with a fake
> Below is a brittle test using `MagicMock(spec=Repository)`. Rewrite it using an `InMemoryProductRepository` fake and a shared contract fixture. Discuss the maintenance difference.
> ```python
> def test_service_lists_products():
>     repo = MagicMock(spec=Repository)
>     repo.all.return_value = [Product("A", "Alpha", 100)]
>     service = ProductService(repo)
>     assert service.list_names() == ["Alpha"]
> ```

> [!example] Exercise 5 — Transactional DB pattern
> Adapt the session-scoped `engine` + function-scoped `db_session` (rollback) pattern to a tiny SQLite schema of your choice. Write a test that inserts a row, then another test that asserts the table is empty. Confirm both pass in any order.

> [!example] Exercise 6 — Diagnose the failure
> A test suite passes when run alone but fails on CI when run with the rest of the suite. You suspect a session-scoped fixture holds a list that's being mutated. Describe your debugging process: which pytest flags would you use (`-p no:randomly`, `--setup-show`, `--fixtures`)? What change would you make to fix the root cause?

Next: [[exception-handling-in-oop]] for how errors are modeled as objects — the other half of "testing and errors".
