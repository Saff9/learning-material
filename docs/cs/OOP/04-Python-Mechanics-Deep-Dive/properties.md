---
title: Properties in Python — Managed Attributes
tags:
  - oop
  - python
  - properties
  - descriptors
  - encapsulation
aliases:
  - property decorator
  - getter
  - setter
  - cached_property
created: 2025-07-30
---

> [!tip] Prerequisite
> Read [[methods]] first — properties are built on the same **descriptor protocol** that makes methods work. Also useful: [[encapsulation]] for *why* we hide attributes.

## 1. Why Properties?

In languages like Java, the convention is to write getters and setters for every field — so you can later add validation or logging without changing the API:

```java
// Java-style — verbose but safe to evolve
public class Temperature {
    private double celsius;
    public double getCelsius() { return celsius; }
    public void setCelsius(double v) {
        if (v < -273.15) throw new IllegalArgumentException();
        celsius = v;
    }
}
```

In Python, **you don't preemptively write getters and setters**. You start with a plain attribute. If you later need to intercept access, you *upgrade it to a property* — and **callers don't have to change a single line**.

```python
# Day 1 — plain attribute, simplest possible API
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

t = Temperature(25.0)
print(t.celsius)        # 25.0  ← direct attribute access

# Day 100 — now we need validation. No API change!
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius    # goes through the property below

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("Below absolute zero")
        self._celsius = value

t = Temperature(25.0)   # works exactly the same
print(t.celsius)        # 25.0  ← still looks like an attribute
t.celsius = -300        # raises ValueError
```

> [!note] This is Python's encapsulation story
> [[encapsulation]] in Python is **convention-first, enforcement-second**. Attributes start public. Properties let you add behavior without breaking the API. See [[encapsulation]] for the `_` and `__` conventions.

## 2. The `@property` Decorator

A `property` is a **data descriptor** that intercepts get, set, and delete operations on an attribute. You usually create it with the `@property` decorator stack:

```python
class Person:
    def __init__(self, name: str) -> None:
        self.name = name        # uses the setter

    @property
    def name(self) -> str:
        """The person's full name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Name cannot be empty")
        self._name = value.strip()

    @name.deleter
    def name(self) -> None:
        print("Forgetting name...")
        del self._name
```

Three things to notice:

1. The getter is decorated with `@property` and creates the `name` property object.
2. The setter is decorated with `@name.setter` — same name, attribute on the property.
3. The deleter is `@name.deleter`.
4. The underlying value lives in `self._name` (convention: leading underscore = "internal").

### 2.1 What `@property` actually does

The following are equivalent:

```python
# Decorator form
class A:
    @property
    def x(self): return self._x

# Functional form
class A:
    def get_x(self): return self._x
    x = property(get_x)
```

A `property` is a descriptor with `fget`, `fset`, `fdel`, and `doc` slots:

```python
p = A.x
print(type(p))              # <class 'property'>
print(p.fget, p.fset)       # <function A.x ...> None
print(p.__doc__)            # The docstring of the getter
```

## 3. Read-Only Properties

If you only define a getter, the property is **read-only**:

```python
class Product:
    def __init__(self, sku: str, price: float) -> None:
        self._sku = sku
        self.price = price

    @property
    def sku(self) -> str:
        """The product's SKU — immutable after construction."""
        return self._sku

p = Product("WIDGET-42", 9.99)
print(p.sku)          # WIDGET-42
p.sku = "OTHER"       # AttributeError: can't set attribute 'sku'
```

> [!tip] Make immutability explicit
> Read-only properties signal intent: "this is set once at construction and never changes." Combined with `@dataclass(frozen=True)` (see [[dataclasses-and-attrs]]), you get real immutability.

### 3.1 Forcing read-only by raising in the setter

Sometimes you want a clearer error message:

```python
class Product:
    @property
    def sku(self) -> str:
        return self._sku

    @sku.setter
    def sku(self, _value: str) -> None:
        raise AttributeError("SKU is immutable; create a new Product instead")
```

## 4. Validation in Setters

The most common property use case is **validation without changing the API**. The `Temperature` class above is the canonical example. Here's a more thorough one:

```python
from __future__ import annotations


class Temperature:
    """A temperature value with Celsius as the canonical unit."""

    ABSOLUTE_ZERO_C = -273.15

    def __init__(self, celsius: float) -> None:
        self.celsius = celsius    # routes through the setter

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("Temperature must be numeric")
        if value < self.ABSOLUTE_ZERO_C:
            raise ValueError(f"{value}°C is below absolute zero")
        self._celsius = float(value)

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = (value - 32) * 5 / 9     # reuse the validation!

    @property
    def kelvin(self) -> float:
        return self._celsius + 273.15


t = Temperature(25.0)
print(t.fahrenheit)      # 77.0
t.fahrenheit = 32.0      # routes through fahrenheit.setter → celsius.setter
print(t.celsius)         # 0.0
print(t.kelvin)          # 273.15

try:
    t.celsius = -500
except ValueError as e:
    print(e)             # -500°C is below absolute zero
```

> [!tip] Chain validations through setters
> `fahrenheit.setter` calls `self.celsius = ...`, which reuses the celsius validation. Don't duplicate logic — let one setter delegate to another.

## 5. Computed Properties

A property's getter can compute its value on the fly:

```python
import math


class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    @property
    def area(self) -> float:
        return math.pi * self.radius ** 2

    @property
    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


c = Circle(3)
print(c.area)        # 28.274333882308138
print(c.perimeter)   # 18.84955592153876
c.radius = 5
print(c.area)        # 78.53981633974483   ← always reflects current radius
```

The downside: every access recomputes. For cheap math, that's fine. For expensive work, cache it (next section).

## 6. Caching with `functools.cached_property`

`functools.cached_property` (Python 3.8+) computes the value **once**, then stores it in the instance's `__dict__`. Subsequent reads return the cached value.

```python
import math
import time
from functools import cached_property


class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    @cached_property
    def area(self) -> float:
        print("  (computing area...)")
        time.sleep(0.5)                 # simulate expensive work
        return math.pi * self.radius ** 2


c = Circle(3)
print(c.area)   # (computing area...)   28.2743...
print(c.area)   # 28.2743...            ← no recomputation
print(c.area)   # 28.2743...            ← cached
```

> [!warning] `cached_property` requires a `__dict__`
> Classes using `__slots__` (see [[dataclasses-and-attrs]]) or built-in types without `__dict__` cannot use `cached_property`. Use a regular `@property` with manual caching instead.

> [!warning] `cached_property` and mutability
> If `radius` changes after the first read, `area` will *not* update — it's frozen at first-access time. If you need invalidation, write it explicitly:

```python
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius
        self._area_cache: float | None = None

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value <= 0:
            raise ValueError("Radius must be positive")
        self._radius = value
        self._area_cache = None        # invalidate

    @property
    def area(self) -> float:
        if self._area_cache is None:
            self._area_cache = math.pi * self._radius ** 2
        return self._area_cache
```

## 7. Migration Path: Public Attribute → Property

This is the killer feature. Here's the recipe:

### 7.1 Step 1 — Start simple

```python
class Order:
    def __init__(self, quantity: int, unit_price: float) -> None:
        self.quantity = quantity
        self.unit_price = unit_price
        # No validation — YAGNI for now

o = Order(3, 9.99)
print(o.quantity)         # 3
o.quantity = 5            # direct assignment
```

### 7.2 Step 2 — Demand emerges

Customers report bugs where `quantity` is negative or zero. We need validation.

### 7.3 Step 3 — Upgrade without breaking callers

```python
class Order:
    def __init__(self, quantity: int, unit_price: float) -> None:
        self.quantity = quantity       # ← unchanged call site, but now uses setter
        self.unit_price = unit_price

    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, value: int) -> None:
        if value < 1:
            raise ValueError("Quantity must be at least 1")
        if not isinstance(value, int):
            raise TypeError("Quantity must be an integer")
        self._quantity = value

    @property
    def unit_price(self) -> float:
        return self._unit_price

    @unit_price.setter
    def unit_price(self, value: float) -> None:
        if value < 0:
            raise ValueError("Unit price cannot be negative")
        self._unit_price = float(value)

    @property
    def total(self) -> float:
        return self._quantity * self._unit_price


# Existing code still works:
o = Order(3, 9.99)
print(o.total)             # 29.97

# New validation kicks in:
try:
    o.quantity = -1
except ValueError as e:
    print(e)               # Quantity must be at least 1
```

> [!tip] "Don't write getters and setters until you need them"
> This is Pythonic. Start with attributes. When you need behavior, convert to a property. The public API is preserved.

## 8. Properties Are Descriptors — Here's the Lookup

Recall from [[methods]] that Python's attribute lookup is:

1. **Data descriptors** on the class (and bases) — `property` is one.
2. **Instance `__dict__`**.
3. Non-data descriptors (functions, classmethods) on the class.
4. Class `__dict__` plain values.
5. `__getattr__` (last-resort hook).

Because `property` is a **data descriptor**, it always wins over an instance attribute of the same name. This is why you can't accidentally shadow a property by writing `instance.x = 5` if `x` is a property without a setter:

```python
class P:
    @property
    def x(self) -> int:
        return 42

p = P()
p.x = 99   # AttributeError: can't set attribute  (data descriptor wins)
```

### 8.1 Mermaid: Property Descriptor Lookup

```mermaid
flowchart TD
    Start["`obj.x` (read)"] --> Q1{"Is `x` a data descriptor<br/>in type(obj).__mro__?"}
    Q1 -- Yes --> D["Call `descriptor.__get__(obj, type)`"]
    D --> Result["Return descriptor result"]
    Q1 -- No --> Q2{"Is `x` in obj.__dict__?"}
    Q2 -- Yes --> Inst["Return instance attribute"]
    Q2 -- No --> Q3{"Is `x` a non-data descriptor<br/>or plain class attr?"}
    Q3 -- Yes --> Use["Use class-level value<br/>(bound if function)"]
    Q3 -- No --> Q4{"Does type(obj) define `__getattr__`?"}
    Q4 -- Yes --> GA["Call `__getattr__(obj, 'x')`"]
    Q4 -- No --> Err["Raise AttributeError"]
    Inst --> Result
    Use --> Result
    GA --> Result
    Err --> End["(error propagates)"]
    Result --> End
```

### 8.2 The same flow for `obj.x = v` (write)

```mermaid
flowchart TD
    Start["`obj.x = v` (write)"] --> Q1{"Is `x` a data descriptor<br/>in type(obj).__mro__?"}
    Q1 -- Yes --> D{"Has it a `__set__`?<br/>(property: is there a setter?)"}
    D -- Yes --> Call["Call `descriptor.__set__(obj, v)`"]
    D -- No --> Store["Store `v` in obj.__dict__"]
    Q1 -- No --> Q2{"Does type(obj) define `__setattr__`?"}
    Q2 -- Yes --> SA["Call `__setattr__(obj, 'x', v)`"]
    Q2 -- No --> Store
    Call --> End
    Store --> End
    SA --> End
```

## 9. Worked Example: A `BankAccount` with Properties

```python
from __future__ import annotations
from decimal import Decimal


class BankAccount:
    """A read-protected, validated bank account."""

    def __init__(self, owner: str, opening_balance: Decimal) -> None:
        self.owner = owner                  # via setter
        self.balance = opening_balance      # via setter

    @property
    def owner(self) -> str:
        return self._owner

    @owner.setter
    def owner(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Owner required")
        self._owner = value.strip()

    @property
    def balance(self) -> Decimal:
        return self._balance

    @balance.setter
    def balance(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError("Balance must be a Decimal")
        if value < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = value

    def deposit(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.balance = self._balance + amount     # re-uses setter

    def withdraw(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal must be positive")
        self.balance = self._balance - amount     # setter validates non-negativity


acc = BankAccount("Alice", Decimal("100"))
acc.deposit(Decimal("50"))
print(acc.balance)        # 150.00

try:
    acc.withdraw(Decimal("1000"))
except ValueError as e:
    print(e)              # Balance cannot be negative
```

## 10. Worked Example: A `Circle` with Cached Computed Properties

```python
import math
from functools import cached_property


class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    @cached_property
    def area(self) -> float:
        print("  (computing area)")
        return math.pi * self.radius ** 2

    @cached_property
    def circumference(self) -> float:
        print("  (computing circumference)")
        return 2 * math.pi * self.radius

    @cached_property
    def diameter(self) -> float:
        print("  (computing diameter)")
        return 2 * self.radius


c = Circle(5)
print("First access:")
print(f"  area = {c.area}")
print(f"  area = {c.area}")      # cached
print(f"  circ = {c.circumference}")
print(f"  circ = {c.circumference}")   # cached
```

Output:

```
First access:
  (computing area)
  area = 78.53981633974483
  area = 78.53981633974483
  (computing circumference)
  circ = 31.41592653589793
  circ = 31.41592653589793
```

## 11. Worked Example: Read-Only `Product.sku`

```python
from __future__ import annotations


class Product:
    """A product whose SKU is set once and cannot change."""

    __slots__ = ("_sku", "_name", "_price")

    def __init__(self, sku: str, name: str, price: float) -> None:
        self._sku = self._validate_sku(sku)
        self.name = name
        self.price = price

    @staticmethod
    def _validate_sku(sku: str) -> str:
        if not sku or not sku.isalnum():
            raise ValueError("SKU must be non-empty and alphanumeric")
        return sku

    @property
    def sku(self) -> str:
        """Immutable product SKU."""
        return self._sku

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value.strip():
            raise ValueError("Name required")
        self._name = value.strip()

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = float(value)


p = Product("WIDGET42", "Widget", 9.99)
print(p.sku)               # WIDGET42
try:
    p.sku = "OTHER"        # AttributeError: can't set attribute
except AttributeError as e:
    print(e)
```

> [!note] `__slots__` plus read-only property = real immutability for that field
> `__slots__` prevents new instance attributes; the read-only property prevents reassignment. (But it doesn't prevent *the underlying `_sku`* from being assigned to from inside the class — that's why immutability is "convention + enforcement" in Python.)

## 12. Pitfalls

> [!warning] Pitfall 1: Infinite recursion in a setter
> ```python
> class Bad:
>     @property
>     def x(self): return self.x     # ❌ should be self._x
>     @x.setter
>     def x(self, v): self.x = v     # ❌ infinite recursion!
> ```
> Always store the value under a *different* name (convention: leading underscore).

> [!warning] Pitfall 2: Hiding the constructor argument with a property
> If `__init__` does `self.x = x` *and* there's a property `x`, the property's setter runs during construction. That's usually what you want — but if the setter has side effects (logging, validation), be aware they run during `__init__`.

> [!warning] Pitfall 3: Subclassing and replacing a property
> If a subclass wants to "extend" a property's setter, it can't just call `super().x` because `x` is the property object, not the underlying value. Use `super(SubClass, SubClass).x.fget(self)` patterns or just call `self._x` directly. This is awkward — accept it.

> [!warning] Pitfall 4: `cached_property` doesn't update on mutation
> See §6. Either make the underlying value immutable, or invalidate the cache explicitly.

> [!warning] Pitfall 5: Overusing properties for expensive operations
> A property *looks like* a cheap attribute access. If `db.query_cache` actually hits the network, callers will be surprised. Reserve properties for cheap things (or at least, things whose cost is bounded and obvious). For expensive operations, use a method: `db.fetch_cache()`.

## 13. Key Takeaways

> [!tip] In five sentences
> 1. Use **plain attributes** by default; upgrade to **`@property`** when you need validation, computation, or lazy caching — without breaking callers.
> 2. A property is a **data descriptor** that wins over instance `__dict__` on lookup.
> 3. **Read-only** properties (getter only) communicate immutability; combine with `__slots__` for stronger enforcement.
> 4. Use **`functools.cached_property`** to memoize expensive computed properties, and invalidate manually when inputs change.
> 5. Properties are Python's answer to "encapsulation without boilerplate" — they let you evolve from simple to sophisticated without an API rewrite.

## 14. Practice Exercises

> [!example] Easy
> 1. Convert a `Temperature` class with a plain `celsius` attribute into one with a `celsius` property that rejects values below `-273.15`. Confirm existing `t.celsius = 25` calls still work.
> 2. Add a read-only `fahrenheit` computed property to `Temperature` (it derives from `celsius`).

> [!example] Medium
> 3. Build a `Password` class with a `value` property whose setter rejects passwords shorter than 8 characters or without a digit. Store only a hash (e.g. `hashlib.sha256`) internally — the getter returns the hash, not the plaintext.
> 4. Write a `Circle` with `area` and `circumference` as `cached_property`s. Demonstrate the second access is fast (no print output).
> 5. Add a `radius.setter` to your `Circle` that *invalidates* the `cached_property` caches (since they're now stale). Hint: `del obj.area` clears the cache.

> [!example] Hard
> 6. Implement a `Money` class with `amount` and `currency` properties. Both setters validate. Add a computed property `in_usd` that converts using a class-level exchange-rate dict. Demonstrate that updating the exchange rate is reflected in new reads of `in_usd`.
> 7. Write a `LazyLoader` class whose `data` property loads from a file on first access and caches the result. Add a `.reload()` method that forces a reload. Confirm with timing that the first call is slow and subsequent calls are instant.
> 8. Build a small framework: a `Validated` descriptor class (like `property` but reusable) that takes a validator function and stores the value under a private name. Use it to declare `name = Validated(str, min_len=1)` and `age = Validated(int, min=0, max=150)` on a `Person` class. (This is the same mechanism `attrs` and `pydantic` use internally — see [[dataclasses-and-attrs]].)

## 15. Related Notes

- [[classes-and-objects]] — attributes, `__dict__`, instance vs class attributes
- [[methods]] — descriptor protocol that powers both methods and properties
- [[magic-methods]] — `__get__`, `__set__` for custom descriptors
- [[encapsulation]] — the philosophical basis for hiding state
- [[dataclasses-and-attrs]] — `attrs` provides reusable validated fields
- [[inheritance]] — overriding properties in subclasses
