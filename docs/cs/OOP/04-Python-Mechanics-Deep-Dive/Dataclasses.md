---
title: Dataclasses — Boilerplate-Free Data Containers
tags:
  - oop
  - python
  - dataclasses
  - boilerplate
  - frozen
  - slots
  - attrs
  - teaching
  - deep-dive
aliases:
  - "@dataclass"
  - dataclass
  - __post_init__
  - field()
  - dataclasses module
related:
  - "[[Magic-Methods]]"
  - "[[Type-Hints-And-OOP]]"
  - "[[Slots-And-Memory]]"
  - "[[Classes-And-Objects]]"
  - "[[Constructors-And-Destructors]]"
created: 2025-01-15
updated: 2025-01-15
---

# Dataclasses — Boilerplate-Free Data Containers

#python #dataclasses #boilerplate #teaching #deep-dive

> [!quote] PEP 557
> "This PEP describes the syntax for declaring *data classes* — classes which exist primarily to store state, with minimal boilerplate."

The `@dataclass` decorator (Python 3.7+) is the canonical modern way to write classes whose main job is to **hold data**. It auto-generates `__init__`, `__repr__`, `__eq__`, and (optionally) `__hash__`, `__lt__`, etc., based on your type-annotated attributes. The result: ~80% less boilerplate for the most common kind of class in business code.

This note covers the decorator options, field customization, the mutable-default trap, `__post_init__`, inheritance, and how dataclasses compare to `NamedTuple`, `TypedDict`, and `attrs`.

Prerequisites: [[Magic-Methods]], [[Type-Hints-And-OOP]], [[Classes-And-Objects]].

---

## 1. Why Dataclasses?

Compare:

```python
# Old style: ~25 lines of boilerplate for a 3-field class
class User:
    def __init__(self, name: str, email: str, age: int):
        self.name = name
        self.email = email
        self.age = age
    def __repr__(self):
        return f"User(name={self.name!r}, email={self.email!r}, age={self.age!r})"
    def __eq__(self, other):
        if not isinstance(other, User): return NotImplemented
        return (self.name, self.email, self.age) == (other.name, other.email, other.age)
    def __hash__(self):
        return hash((self.name, self.email, self.age))
```

```python
# Dataclass: 4 lines, same behavior
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    name: str
    email: str
    age: int
```

That's it. The decorator reads the class's annotated attributes and generates the four dunders for you. The result behaves identically to the verbose version.

> [!tip] Teaching Tip
> Show students the verbose version first — *then* the dataclass. Without seeing the boilerplate, they won't appreciate what `@dataclass` saves them from.

```mermaid
mindmap
  root((Dataclasses))
    Decorator Options
      init
        auto-generate __init__
      repr
        auto-generate __repr__
      eq
        auto-generate __eq__
      order
        generate __lt__ __le__ __gt__ __ge__
      frozen
        immutable instances
        hashable
      slots
        use __slots__ (3.10+)
      unsafe_hash
        generate __hash__ even if mutable
    Field Customization
      default
      default_factory
      init=False
      repr=False
      compare=False
      hash=None
      metadata
    Lifecycle
      __post_init__
      InitVar
    Alternatives
      NamedTuple
      TypedDict
      attrs
      Pydantic BaseModel
    Inheritance
      field order
      field override
      default rules
```

---

## 2. The Decorator Options

```python
@dataclass(
    init=True,          # generate __init__         (default: True)
    repr=True,          # generate __repr__         (default: True)
    eq=True,            # generate __eq__           (default: True)
    order=False,        # generate __lt__ etc.      (default: False)
    unsafe_hash=False,  # generate __hash__         (default: False)
    frozen=False,       # make instances immutable (default: False)
    match_args=True,    # generate __match_args__   (default: True, 3.10+)
    kw_only=False,      # all fields kw-only        (default: False, 3.10+)
    slots=False,        # add __slots__             (default: False, 3.10+)
    weakref_slot=False, # add __weakref__ slot      (default: False, 3.11+)
)
class C: ...
```

| Option | Generates / Does | When to enable |
|---|---|---|
| `init=True` | `__init__` from fields | Almost always (set False if you write your own) |
| `repr=True` | `__repr__` listing all fields | Almost always |
| `eq=True` | `__eq__` comparing fields by tuple | Almost always |
| `order=True` | `__lt__`, `__le__`, `__gt__`, `__ge__` (by field order) | When you need sorting |
| `frozen=True` | Instances immutable; `__hash__` auto-added | Value objects, dict keys |
| `unsafe_hash=True` | `__hash__` even on mutable classes | Rare — you accept the risk of mutable hashable |
| `slots=True` | Adds `__slots__`; smaller, faster | Many instances, memory matters |
| `kw_only=True` | Force all-kwargs construction | Many fields, hard to read positionally |

### 2.1 `frozen` — Immutability Done Right

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
# p.x = 5   # FrozenInstanceError
d = {p: "origin"}    # works — frozen implies hashable
```

`frozen=True` makes `__setattr__` and `__delattr__` raise `FrozenInstanceError`. It also implicitly sets `__hash__` (since equal instances must have equal hashes, and immutability guarantees that). Use `frozen` for **value objects** — money, coordinates, IDs, configurations that should not change after construction.

### 2.2 `slots=True` (Python 3.10+)

Adds `__slots__` automatically — see [[Slots-And-Memory]] for the full story. Combines the ergonomics of dataclasses with the memory savings of slots.

```python
@dataclass(slots=True)
class Pixel:
    r: int
    g: int
    b: int
# Pixel has __slots__ = ('r', 'g', 'b') — no __dict__
```

> [!warning] `frozen` and `slots` Together
> Before 3.11, combining `frozen=True` and `slots=True` was awkward (you couldn't set defaults in `__init__` because of slot restrictions). 3.11+ supports this combination cleanly.

---

## 3. Field Customization with `field()`

Not every field should be in `__init__`, `__repr__`, or equality. The `field()` function gives you per-field control:

```python
from dataclasses import dataclass, field

@dataclass
class User:
    id: int
    name: str
    email: str
    # Mutable default → must use default_factory
    tags: list[str] = field(default_factory=list)
    # Computed, not in __init__
    display_name: str = field(init=False, default="")
    # Internal, hidden from repr and equality
    _cache: dict = field(default_factory=dict, repr=False, compare=False)
    # Extra metadata for serializers
    role: str = field(default="user", metadata={"json_key": "role"})

    def __post_init__(self):
        if not self.display_name:
            self.display_name = self.name.title()
```

| `field(...)` argument | Effect |
|---|---|
| `default=x` | Static default value (must be immutable) |
| `default_factory=callable` | Called with no args to produce a fresh default |
| `init=True/False` | Include in `__init__` parameters |
| `repr=True/False` | Include in `__repr__` |
| `compare=True/False` | Include in `__eq__`, `__lt__`, etc. |
| `hash=None/True/False` | Include in `__hash__` (None = follow `compare`) |
| `metadata={...}` | Arbitrary metadata dict for third-party tools |
| `kw_only=True/False` | Make this field keyword-only (3.10+) |

### 3.1 The Mutable Default Trap

```python
@dataclass
class Bad:
    items: list = []      # ValueError at class creation!
```

Python refuses this — mutable defaults shared across all instances is a classic bug (cf. default arguments in functions). Use `default_factory`:

```python
@dataclass
class Good:
    items: list = field(default_factory=list)
```

Each new instance gets a *fresh* empty list. Same rule applies to `dict`, `set`, and any other mutable container.

> [!warning] Common Student Misconception
> "I'll just use `None` as a default and create the list inside `__init__`." That works, but defeats much of the point of dataclasses — your `__init__` is now hand-written, and you've lost `frozen` semantics. Use `default_factory` instead; it's the idiomatic, type-safe way.

---

## 4. `__post_init__` — The Post-Construction Hook

For derived fields, validation, or any setup that needs the values already assigned, define `__post_init__`:

```python
from dataclasses import dataclass, field
import re

@dataclass
class Email:
    value: str

    def __post_init__(self):
        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", self.value):
            raise ValueError(f"Invalid email: {self.value!r}")

@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("dimensions must be positive")
        self.area = self.width * self.height

r = Rectangle(3, 4)
print(r.area)    # 12.0
```

```mermaid
sequenceDiagram
    participant User
    participant DC as @dataclass-generated __init__
    participant PI as __post_init__
    User->>DC: Rectangle(3, 4)
    DC->>DC: self.width = 3
    DC->>DC: self.height = 4
    DC->>PI: __post_init__()
    PI->>PI: validate width, height
    PI->>PI: compute self.area = 12
    PI-->>DC: returns
    DC-->>User: Rectangle(width=3, height=4, area=12.0)
```

### 4.1 `InitVar` — Pass-Through Arguments

Sometimes you want to pass an argument to `__init__` that *is not* stored as a field. Use `InitVar`:

```python
from dataclasses import dataclass, field, InitVar

@dataclass
class DatabaseConfig:
    host: str
    port: int
    password: InitVar[str] = ""        # passed to __init__, NOT stored
    dsn: str = field(init=False)

    def __post_init__(self, password: str):
        self.dsn = f"postgres://user:{password}@{self.host}:{self.port}/db"

c = DatabaseConfig("localhost", 5432, password="secret")
print(c.dsn)        # postgres://user:secret@localhost:5432/db
# c.password        # AttributeError — not stored
```

---

## 5. Inheritance with Dataclasses

Dataclasses compose through inheritance, but the rules around field ordering and defaults are strict:

```python
@dataclass
class Base:
    x: int = 0

@dataclass
class Derived(Base):
    y: int = 0

d = Derived(x=1, y=2)
print(d)   # Derived(x=1, y=0) ... wait, no: Derived(x=1, y=2)
```

Fields are merged in MRO order: base fields first, then derived. If a base field has no default and a derived field does, the resulting `__init__` will have a non-default argument *after* a default one — which Python forbids:

```python
@dataclass
class Base:
    x: int                              # no default

@dataclass
class Derived(Base):
    y: int = 10                         # has default
# TypeError: non-default argument 'y' follows default argument
```

The fix: give `x` a default too, or use `kw_only=True`:

```python
@dataclass(kw_only=True)
class Base:
    x: int

@dataclass(kw_only=True)
class Derived(Base):
    y: int = 10
# OK: Derived(x=1, y=2) — all kwargs, no positional ordering issue
```

```mermaid
classDiagram
    class Base {
        +int x
        +__init__(x)
    }
    class Derived {
        +int y
        +__init__(x, y=10)
    }
    Base <|-- Derived
    note for Base "Fields without defaults must come first"
    note for Derived "Cannot add a defaulted field\nif base has non-defaulted field\nunless kw_only=True"
```

### 5.1 Overriding Fields

A subclass can override a field's type, default, or `field()` config:

```python
@dataclass
class Animal:
    name: str
    sound: str = "?"

@dataclass
class Dog(Animal):
    sound: str = "Woof"     # override default

d = Dog(name="Rex")
print(d)    # Dog(name='Rex', sound='Woof')
```

### 5.2 A Concrete Inheritance Example

Imagine a hierarchy of `Employee` types:

```python
from dataclasses import dataclass, field
from datetime import date

@dataclass
class Employee:
    id: int
    name: str
    hired: date = field(default_factory=date.today)

@dataclass
class SalariedEmployee(Employee):
    annual_salary: float = 0.0

@dataclass
class HourlyEmployee(Employee):
    hourly_rate: float = 0.0
    hours_worked: float = 0.0

@dataclass
class Contractor(HourlyEmployee):
    agency: str = ""           # contractors bill through an agency

# Contractor has fields: id, name, hired, hourly_rate, hours_worked, agency
c = Contractor(id=1, name="Bob", hourly_rate=80, hours_worked=40, agency="Acme")
print(c)
```

Notice that each subclass *adds* fields; the order is `id, name, hired, hourly_rate, hours_worked, agency`. All fields have defaults (or inherit defaults), so positional construction works.

### 5.3 Diamond Inheritance

```python
@dataclass
class A:
    a: int = 1

@dataclass
class B(A):
    b: int = 2

@dataclass
class C(A):
    c: int = 3

@dataclass
class D(B, C):
    d: int = 4

# D's fields, in MRO order: a (from A), b (from B), c (from C), d (from D)
print(D())    # D(a=1, b=2, c=3, d=4)
```

The MRO determines field order — `a` appears once, not twice, despite being inherited through both `B` and `C`.

---

## 6. Dataclasses vs Alternatives

```mermaid
flowchart LR
    Q["Need a data container?"]
    Q --> Q1["Mutable, lots of methods,<br/>inheritance?"]
    Q1 -->|Yes| DC["@dataclass"]
    Q --> Q2["Immutable, tuple-like,<br/>very lightweight?"]
    Q2 -->|Yes| NT["NamedTuple"]
    Q --> Q3["Just a typed dict shape,<br/>no methods needed?"]
    Q3 -->|Yes| TD["TypedDict"]
    Q --> Q4["Runtime validation,<br/>JSON parsing,<br/>serialization?"]
    Q4 -->|Yes| PYD["Pydantic BaseModel"]
    Q --> Q5["Heavy defaults,<br/>slots, validators,<br/>pre-3.7 support?"]
    Q5 -->|Yes| ATTR["attrs"]
    style DC fill:#dfd
```

| Feature | `@dataclass` | `NamedTuple` | `TypedDict` | `attrs` | `pydantic.BaseModel` |
|---|---|---|---|---|---|
| **Mutable?** | Yes (default) | No (tuples) | Yes (it's a dict) | Yes | Yes |
| **Immutable option?** | `frozen=True` | Always | No | `frozen=True` | `frozen=True` (config) |
| **Slots?** | `slots=True` (3.10+) | Always | N/A | `slots=True` | Yes |
| **Type validation at runtime?** | No (just hints) | No | No | Opt-in | **Yes** |
| **JSON (de)serialization?** | Manual | Manual | Manual (it's a dict) | Helpers | **Built-in** |
| **Inheritance?** | Yes | Awkward | Yes (totally) | Yes | Yes |
| **Methods?** | Yes | Yes (clunky) | No | Yes | Yes |
| **Default factories?** | `default_factory` | `field(default_factory=)` | N/A | `factory=` | Yes |
| **Python version** | 3.7+ | 3.6+ (typing) | 3.8+ | 3.6+ (external) | 3.7+ (external) |

### 6.1 When to Use Each

- **`@dataclass`** — default choice for data-holding classes in modern Python.
- **`NamedTuple`** — when you want tuple semantics (unpacking, indexing) *and* immutability.
- **`TypedDict`** — when you're describing the shape of a dict (e.g., JSON payloads, kwargs), not building a class.
- **`attrs`** — if you need features dataclasses lack (validators, converters, advanced slots) or pre-3.7 support.
- **Pydantic** — for HTTP/JSON models with strict runtime validation and serialization.

### 6.2 Example: Three Equivalents

```python
# Dataclass
from dataclasses import dataclass
@dataclass(frozen=True)
class Point1:
    x: float; y: float

# NamedTuple
from typing import NamedTuple
class Point2(NamedTuple):
    x: float; y: float

# TypedDict (not a class — just a dict shape!)
from typing import TypedDict
class Point3(TypedDict):
    x: float; y: float
```

The first two produce actual class instances; the third is purely for static type checkers — at runtime, `Point3(x=1, y=2)` is just `{"x": 1, "y": 2}`.

---

## 7. Practical Examples

### 7.1 Configuration Object

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 4
    debug: bool = False
    cors_origins: tuple[str, ...] = ("http://localhost:3000",)

# Frozen → safe to share, hash, use as dict key
config = ServerConfig()
print(config)   # ServerConfig(host='0.0.0.0', port=8080, ...)
```

### 7.2 Order with Validation

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass(order=True)
class Order:
    # `priority` is the sort key — others excluded from ordering
    priority: int
    created_at: datetime = field(default_factory=datetime.now, compare=False)
    id: str = field(compare=False)
    items: list = field(default_factory=list, compare=False)
    customer_email: Optional[str] = field(default=None, compare=False)

    def __post_init__(self):
        if not 0 <= self.priority <= 10:
            raise ValueError("priority must be 0..10")
        if not self.items:
            raise ValueError("order must have items")

orders = [
    Order(5, id="A", items=["x"]),
    Order(1, id="B", items=["y"]),
    Order(8, id="C", items=["z"]),
]
orders.sort()    # by priority ascending
```

### 7.3 Validation in `__post_init__`

```python
from dataclasses import dataclass

@dataclass
class Temperature:
    celsius: float

    def __post_init__(self):
        if self.celsius < -273.15:
            raise ValueError("below absolute zero")

    @property
    def fahrenheit(self):
        return self.celsius * 9/5 + 32

t = Temperature(25.0)
print(t.fahrenheit)   # 77.0
# Temperature(-300)   # ValueError
```

### 7.4 Frozen Dataclass as Dict Key

```python
@dataclass(frozen=True)
class GridCell:
    row: int
    col: int

board = {GridCell(0, 0): "A", GridCell(0, 1): "B"}
print(board[GridCell(0, 0)])   # "A" — same value, same hash
```

---

## 8. Converting Dataclasses

| Operation | Function |
|---|---|
| Instance → dict | `dataclasses.asdict(obj)` (deeply) |
| Instance → tuple | `dataclasses.astuple(obj)` (deeply) |
| Dict → instance | `MyClass(**d)` (manual; Pydantic automates this) |
| Replace a field | `dataclasses.replace(obj, field=new_value)` |
| Get fields metadata | `dataclasses.fields(obj)` / `dataclasses.fields(MyClass)` |

```python
from dataclasses import dataclass, asdict, astuple, replace, fields

@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str

u = User(1, "Alice", "alice@example.com")
asdict(u)         # {'id': 1, 'name': 'Alice', 'email': '...'}
astuple(u)        # (1, 'Alice', 'alice@example.com')
u2 = replace(u, name="Alicia")   # new frozen instance with one field changed
fields(User)      # tuple of Field objects
```

> [!warning] `asdict` is Deep
> `asdict` recursively converts nested dataclasses, lists, and dicts. That's usually what you want, but if your dataclass contains a non-serializable object (e.g., a DB connection), `asdict` will include it as-is. For JSON, serialize explicitly with `json.dumps(..., default=str)` or use Pydantic.

---

## 9. Pitfalls

### 9.1 Equality Compares All Fields by Default

If you have a `created_at` field, two "equal" objects created at different times will be `!=`. Use `field(compare=False)` to exclude fields from equality.

### 9.2 Mutable Default Field State

```python
@dataclass
class Bad:
    items: list = field(default_factory=list)

a, b = Bad(), Bad()
a.items.append(1)
print(b.items)    # [] — good! default_factory creates fresh lists
```

But:

```python
@dataclass
class Sneaky:
    config: dict = field(default_factory=lambda: {"debug": False})

a = Sneaky()
a.config["debug"] = True
b = Sneaky()
print(b.config)   # {'debug': False} — good, but easy to mess up
```

`default_factory` runs *once per instance*, so this is safe — but if you assign a shared object to a field after construction, you reintroduce the bug.

### 9.3 Type Hints Are Not Validated

```python
@dataclass
class Mismatch:
    x: int

Mismatch(x="hello")    # works! Just sets x = "hello"
```

Dataclasses honor *only* the field definitions — the type annotation is a hint, not a runtime check. Use Pydantic if you need runtime enforcement.

### 9.4 Inheritance Order Surprises

If a subclass adds a non-defaulted field but the base has defaulted fields, you'll get a `TypeError`. Plan field order carefully or use `kw_only=True`.

### 9.5 `unsafe_hash` Is a Footgun

`unsafe_hash=True` generates a `__hash__` based on `compare` fields even for mutable dataclasses. This means mutating an instance after using it as a dict key will silently break the dict's invariants. Use only when you really know what you're doing.

### 9.6 Equality via Tuples — Watch Out for Nested Mutables

Dataclass `__eq__` compares fields as a tuple: `(self.x, self.y) == (other.x, other.y)`. If a field is itself a mutable list, two instances are equal only if the lists happen to have the same current contents. This is usually what you want, but it can be surprising.

---

## 10. Best Practices

1. **Default to `@dataclass`** for any class whose primary job is holding data.
2. **Use `frozen=True`** for value objects (money, coordinates, IDs, configs).
3. **Use `default_factory`** for any mutable default — never `[]`, `{}`, or `set()`.
4. **Use `field(compare=False)`** for computed / timestamp / cache fields.
5. **Use `__post_init__`** for validation and derived fields, not for replacing `__init__`.
6. **Use `kw_only=True`** when a class has many fields or is likely to grow.
7. **Use `slots=True`** (3.10+) for high-cardinality classes to save memory.
8. **Don't fight the type system** — if you need runtime validation, switch to Pydantic.
9. **Prefer `dataclasses.replace`** over manual `copy` + mutate for frozen dataclasses.
10. **Document non-obvious field semantics** in `metadata={...}` for tooling.

> [!success] Final Teaching Tip
> Have students rewrite an existing verbose class as a dataclass. The dramatic line-count drop is the best "aha" moment — and once they see it, they'll reach for `@dataclass` first instead of writing `__init__` by hand.

---

## See Also

- [[Magic-Methods]] — `@dataclass` is a generator of `__init__`, `__repr__`, `__eq__`, `__hash__`, etc.
- [[Type-Hints-And-OOP]] — dataclasses depend on field annotations.
- [[Slots-And-Memory]] — the `slots=True` option ties in directly.
- [[Classes-And-Objects]] — when to use a dataclass vs a regular class.
- [[Constructors-And-Destructors]] — `__init__` and `__post_init__`.

## Appendix A: Worked Example — A Complete Data Class

Let's build a more realistic dataclass showing many features together. The example models a `BankAccount` with validation, computed fields, immutability for value types, and integration with `__post_init__`:

```python
from __future__ import annotations
from dataclasses import dataclass, field, InitVar
from datetime import datetime
from typing import Optional
import re

@dataclass(frozen=True)
class AccountId:
    """An immutable value object — frozen dataclass."""
    value: str
    def __post_init__(self):
        if not re.fullmatch(r"[A-Z]{2}\d{6}", self.value):
            raise ValueError(f"Invalid account ID: {self.value!r}")

@dataclass
class BankAccount:
    id: AccountId
    owner: str
    balance: float = 0.0
    opened_at: datetime = field(default_factory=datetime.now, compare=False)
    _initial_deposit: InitVar[Optional[float]] = None
    transactions: list[dict] = field(default_factory=list, repr=False, compare=False)

    def __post_init__(self, _initial_deposit: Optional[float]) -> None:
        if _initial_deposit is not None:
            if _initial_deposit < 0:
                raise ValueError("initial deposit cannot be negative")
            self.balance = _initial_deposit
            self.transactions.append({"type": "deposit", "amount": _initial_deposit})

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount
        self.transactions.append({"type": "deposit", "amount": amount})

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        self.transactions.append({"type": "withdrawal", "amount": amount})

# Two equivalent accounts are equal — same id, owner, balance
a1 = BankAccount(AccountId("AB123456"), "Alice", _initial_deposit=100)
a2 = BankAccount(AccountId("AB123456"), "Alice", balance=100)
print(a1 == a2)   # True — `opened_at` excluded from compare, transactions too

a1.deposit(50)
print(a1.balance)   # 150.0
print(len(a1.transactions))   # 2 (initial + deposit)
```

Notice the patterns:

- **`AccountId` is `frozen=True`** — value object, hashable, immutable.
- **`opened_at` uses `default_factory`** and `compare=False` — fresh timestamp per instance, excluded from equality.
- **`_initial_deposit` is `InitVar`** — passed to `__init__` but not stored as a field.
- **`transactions` is hidden from `repr` and `compare`** — internal bookkeeping.

This is what idiomatic, production-grade dataclasses look like.

## Appendix B: Common Pitfalls — Expanded

| Pitfall | Symptom | Fix |
|---|---|---|
| Mutable default `[]` | `ValueError` at class definition | Use `field(default_factory=list)` |
| Comparing all fields including timestamps | Two "equal" objects are unequal | Use `field(compare=False)` |
| `__post_init__` mutating a frozen dataclass | `FrozenInstanceError` | Use `object.__setattr__` to bypass frozen check |
| Subclass adds non-default field after defaulted base field | `TypeError: non-default follows default` | Make all fields `kw_only=True`, or restructure |
| Forgot `__hash__` on mutable dataclass with `eq=True` | Object unhashable (dataclass sets `__hash__ = None`) | Use `frozen=True` (auto-adds hash) or `unsafe_hash=True` |
| Stored lambda in `default_factory` | Pickle fails | Use a module-level function |
| `asdict` on dataclass with non-serializable field | Pickle / JSON errors | Exclude field from `asdict` or use Pydantic |
| `field(default=...)` with mutable value | Mutable shared across instances — but Python refuses this at class definition | Use `default_factory` |

### B.1 Bypassing Frozen in `__post_init__`

Sometimes you need to compute and set a field in `__post_init__` but the dataclass is `frozen=True`. Direct assignment fails:

```python
@dataclass(frozen=True)
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)
    def __post_init__(self):
        self.area = self.width * self.height    # FrozenInstanceError!
```

Fix: use `object.__setattr__` to bypass the frozen check:

```python
@dataclass(frozen=True)
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)
    def __post_init__(self):
        object.__setattr__(self, "area", self.width * self.height)
```

This is the officially-blessed workaround for frozen dataclasses with computed fields.

## Appendix C: Dataclasses and Pattern Matching (3.10+)

Python 3.10 added structural pattern matching (`match`/`case`). Dataclasses integrate beautifully — the `__match_args__` attribute (auto-generated by `@dataclass`) lets `match` match positional arguments:

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    # __match_args__ = ("x", "y") auto-generated

def describe(p):
    match p:
        case Point(0, 0):       return "origin"
        case Point(0, y):       return f"on y-axis at {y}"
        case Point(x, 0):       return f"on x-axis at {x}"
        case Point(x, y):       return f"point at ({x}, {y})"
        case _:                 return "not a point"
```

If you set `match_args=False` on the decorator, positional matching is disabled and you must use keyword patterns: `case Point(x=0, y=0)`.

## Appendix D: Decision Tree — When to Use Dataclasses

```mermaid
flowchart TD
    Q1["Need a class to hold data?"]
    Q1 -- no --> ND["Use a regular class"]
    Q1 -- yes --> Q2["Need validation at construction?"]
    Q2 -- yes --> Q3["Strict runtime validation<br/>(types, regex, ranges)?"]
    Q3 -- yes --> PYD["Use Pydantic BaseModel"]
    Q3 -- no --> DC1["Use @dataclass with __post_init__"]
    Q2 -- no --> Q4["Need immutability?"]
    Q4 -- yes --> Q5["Tuple semantics needed<br/>(unpacking, indexing)?"]
    Q5 -- yes --> NT["Use NamedTuple"]
    Q5 -- no --> FROZ["Use @dataclass(frozen=True)"]
    Q4 -- no --> Q6["Need slots for memory?"]
    Q6 -- yes --> SLOTS["@dataclass(slots=True)"]
    Q6 -- no --> Q7["Need ordering?"]
    Q7 -- yes --> ORD["@dataclass(order=True)"]
    Q7 -- no --> BASIC["@dataclass (basic)"]
    style PYD fill:#fdd
    style DC1 fill:#dfd
    style FROZ fill:#dfd
    style NT fill:#dfd
    style SLOTS fill:#dfd
    style ORD fill:#dfd
    style BASIC fill:#dfd
    style ND fill:#fdd
```

## Appendix E: Quick Reference — Field Options Table

| Option | Default | Effect |
|---|---|---|
| `default` | `_MISSING` | Static default value (must be immutable) |
| `default_factory` | `_MISSING` | Callable producing a fresh default |
| `init` | `True` | Include in `__init__` parameters |
| `repr` | `True` | Include in `__repr__` |
| `hash` | `None` | `None` follows `compare`; `True`/`False` overrides |
| `compare` | `True` | Include in `__eq__`, `__lt__`, etc. |
| `metadata` | `None` | Arbitrary dict for tooling |
| `kw_only` | `False` | Make this field keyword-only (3.10+) |

## Appendix F: Performance Notes

- Dataclasses are **zero runtime cost** beyond what an equivalent hand-written class would have. The decorator runs at class creation; instances are plain Python objects.
- `frozen=True` adds a small overhead on every `__setattr__` and `__delattr__` call (they raise `FrozenInstanceError`).
- `slots=True` (3.10+) gives the memory/speed benefits described in [[Slots-And-Memory]].
- For very hot paths, a hand-written `__init__` can be slightly faster than the dataclass-generated one — but the difference is usually negligible compared to the maintenance savings.
- `asdict` and `astuple` are O(n) where n is the number of fields (plus the cost of recursive descent for nested dataclasses). For high-throughput code paths, avoid them in inner loops.
- Pattern matching on dataclasses (3.10+) uses `__match_args__`, which is a tuple lookup — extremely fast.
- `dataclasses.replace()` constructs a new instance by calling `__init__` again — same cost as the original construction.

### F.1 When to Avoid Dataclasses

- **Heavy inheritance with mixed defaulted/non-defaulted fields**: the positional ordering rules become painful. Switch to `kw_only=True` or use a regular class.
- **Need full custom `__init__` with non-trivial logic**: dataclass `__init__` is generated; if you need conditional logic, side effects, or argument transformation, write `__init__` yourself.
- **Need class-level state that's not field-related**: dataclasses are about fields. If your class has lots of classmethods and few fields, a plain class is clearer.
- **Cross-version compatibility**: dataclasses require Python 3.7+. If you must support 3.6, use `attrs` instead.

> [!success] Final Teaching Tip
> Have students rewrite an existing verbose class as a dataclass. The dramatic line-count drop is the best "aha" moment — and once they see it, they'll reach for `@dataclass` first instead of writing `__init__` by hand.

## References

- PEP 557 — Data Classes
- `dataclasses` module documentation
- "Fluent Python" (Ramalho), Chapter 5 — "Data Class Builders"
- attrs library: https://www.attrs.org
- Pydantic: https://docs.pydantic.dev

## Dataclasses Deep Dive: `kw_only=True`, `slots=True`, vs Pydantic V2

### `kw_only=True` (Python 3.10+)

Forces attributes to be specified by keyword.

```python
from dataclasses import dataclass

@dataclass(kw_only=True)
class Config:
    timeout: int = 10
    url: str

# c = Config(10, 'http://...') # TypeError!
c = Config(url='http://...', timeout=20)
```

### `slots=True` (Python 3.10+)

Automatically generates `__slots__` to save memory and prevent dynamic attribute creation.

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
# p.z = 3 # AttributeError!
```

### Dataclasses vs Pydantic V2

- **Dataclasses**: Standard library, lightweight, primarily for boilerplate reduction. No built-in validation (except type hints which aren't enforced at runtime).
- **Pydantic V2**: Third-party (Rust backend), powerful runtime validation, parsing, serialization.

```mermaid
graph TD
    A[Dataclass] -->|slots=True| B(Memory Efficient)
    A -->|kw_only=True| C(Strict Init)
    D[Pydantic V2] -->|Rust Core| E(Fast Validation)
    D -->|Type Coercion| F(Safe Data Parsing)
```

### Practice Exercises
1. Create a `slots=True` dataclass and verify its memory footprint vs a normal class using `sys.getsizeof()`.
2. Compare instantiating a dataclass vs a Pydantic model with invalid types.
