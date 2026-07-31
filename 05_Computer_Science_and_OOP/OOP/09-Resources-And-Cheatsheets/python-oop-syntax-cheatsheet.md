---
title: "Python OOP Syntax Cheat Sheet"
tags:
  - oop
  - cheatsheet
  - python
  - syntax
  - reference-card
aliases:
  - Python OOP Syntax
  - Python Class Syntax Card
  - Python OOP Cheatsheet
created: 2025-01-20
---

# 🐍 Python OOP Syntax Cheat Sheet

> [!tip] Pure syntax. Every snippet is copy-pasteable and minimal.
> For the *why* behind each feature, follow the wikilinks to the deep-dive notes.

---

## 1. Class Declaration — All Variants

```python
# 1. Simplest
class Empty: ...

# 2. With docstring + attributes
class Point:
    """A 2D point."""
    z: int = 0                       # class attribute / annotation

# 3. Inheriting (single)
class Dog(Animal): ...

# 4. Multiple inheritance
class FlyingFish(Fish, Bird): ...

# 5. With metaclass
class Logged(metaclass=LogMeta): ...

# 6. With kwargs to metaclass / __init_subclass__
class Plugin(Base, key="auth"): ...

# 7. Generic class (PEP 585 / 695)
class Stack(list[T]): ...            # 3.12+
# or older:
from typing import Generic, TypeVar
T = TypeVar("T")
class Stack(Generic[T]): ...
```

See [[classes-and-objects]] · [[metaclasses-and-class-creation]].

---

## 2. Construction Trio — `__new__`, `__init__`, `__del__`

```python
class Traced:
    def __new__(cls, *args, **kwargs):
        print(f"__new__({cls}, {args})")
        instance = super().__new__(cls)             # default object creation
        return instance

    def __init__(self, x: int) -> None:
        print(f"__init__({x})")
        self.x = x

    def __del__(self) -> None:
        print(f"__del__ of {self}")
```

| Hook | When called | Common use |
|---|---|---|
| `__new__` | Before `__init__`, returns the instance | Immutables, singletons, subclassing built-ins |
| `__init__` | After `__new__`, mutates the instance | Default initialization |
| `__del__` | When refcount hits 0 (no guarantees on timing!) | Cleanup — prefer `__exit__`/context managers |

> [!danger] Don't rely on `__del__`
> It may never run during interpreter shutdown. Use `with` + `__enter__`/`__exit__` for resource cleanup.

---

## 3. Attributes — Instance, Class, Static

```python
class Counter:
    total: int = 0          # class attribute — shared across instances

    def __init__(self) -> None:
        self.count: int = 0 # instance attribute — per object

Counter.total               # 0 (read via class)
Counter.total = 5           # set class attribute
c = Counter()
c.count                     # 0
c.count = 3                 # set instance attribute (shadows class attr if same name)
```

| Attribute type | Defined in | Lives on | Example |
|---|---|---|---|
| Instance | `__init__` / methods via `self.x =` | instance `__dict__` | `self.name` |
| Class | Class body | class `__dict__` (and inherited) | `Counter.total` |
| Static (annotation only) | Class body, no value | Just an annotation | `name: str` (no `=`) |

> [!warning] Mutable default class attributes are shared!
> ```python
> class Bad:
>     items: list = []           # ❌ shared across ALL instances
> class Good:
>     def __init__(self) -> None:
>         self.items: list = []  # ✅ fresh per instance
> ```

---

## 4. Methods — Instance / Class / Static

```python
class Sugar:
    _g_per_tsp: float = 4.2
    def __init__(self, brand: str) -> None:
        self.brand = brand

    def describe(self) -> str:                              # instance
        return f"{self.brand} sugar"

    @classmethod
    def from_default(cls) -> "Sugar":                       # class
        return cls("C&H")

    @staticmethod
    def density() -> float:                                 # static
        return 1.587
```

| Decorator | First param | Receives | Use case |
|---|---|---|---|
| (none) | `self` | instance | Default — uses/changes instance state |
| `@classmethod` | `cls` | class | Alternate constructors, class-level ops |
| `@staticmethod` | (none) | nothing | Utility functions logically grouped with class |

See [[methods]].

---

## 5. Properties — getter, setter, deleter, cached

```python
from functools import cached_property

class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius                  # routes through setter

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @celsius.deleter
    def celsius(self) -> None:
        raise AttributeError("cannot delete temperature")

    @property
    def fahrenheit(self) -> float:               # read-only
        return self._celsius * 9 / 5 + 32

    @cached_property                             # computed once, cached on instance
    def is_freezing(self) -> bool:
        return self._celsius <= 0
```

> [!warning] `cached_property` + `__slots__`
> `cached_property` needs to write to `self.__dict__`. If you use `__slots__` without a `__dict__` slot, it'll fail. Either add `__dict__` to slots or use `@property` with a manual cache.

See [[properties]].

---

## 6. Inheritance — Single, Multiple, MRO, super()

```python
class A:
    def hello(self) -> str:
        return "A"

class B(A):
    def hello(self) -> str:
        return f"B({super().hello()})"        # cooperative super

class C(A):
    def hello(self) -> str:
        return f"C({super().hello()})"

class D(B, C):                                # diamond!
    def hello(self) -> str:
        return f"D({super().hello()})"

print(D().hello())                            # D(B(C(A)))
print(D.__mro__)                              # method resolution order
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

### `super()` — All Forms

```python
super().method()                              # zero-arg (in instance/class methods)
super(__class__, self).method()               # explicit two-arg form
super(__class__, cls).method()                # in classmethods
super()                                       # in __new__: super().__new__(cls)
```

### MRO & C3 Linearization

- `Cls.__mro__` — tuple showing lookup order.
- C3 algorithm — *monotonic*, *extends*, *no surprises*; raises `TypeError` if it can't linearize.
- Common pitfall: two base classes with conflicting MROs.

See [[inheritance]] · [[methods]].

---

## 7. Abstract Base Classes (ABC) & `@abstractmethod`

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "Shape": ...   # can combine with classmethod

class Circle(Shape):
    def __init__(self, r: float) -> None: self.r = r
    def area(self) -> float: return 3.14159 * self.r ** 2
    def perimeter(self) -> float: return 2 * 3.14159 * self.r
    @classmethod
    def from_dict(cls, data: dict) -> "Circle": return cls(data["r"])

# Shape()              # ❌ TypeError — can't instantiate abstract class
# Circle(2)            # ✅ all abstractmethods implemented
```

| Helper | Purpose |
|---|---|
| `ABC` | Base class providing `__init_subclass__` checks |
| `@abstractmethod` | Must be overridden |
| `@abstractproperty` | Deprecated — use `@property` + `@abstractmethod` |
| `ABCMeta` | Metaclass alternative to inheriting `ABC` |
| `register()` | `Shape.register(Triangle)` — virtual subclass (no inheritance) |

See [[abstraction]].

---

## 8. Protocols — `typing.Protocol` (structural typing)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Walker(Protocol):
    def walk(self, distance: float) -> None: ...

class Dog:                                     # NOTE: does NOT inherit Walker
    def walk(self, distance: float) -> None:
        print(f"Dog walked {distance}m")

def go(w: Walker) -> None: w.walk(5)
go(Dog())                                      # ✅ structurally compatible
isinstance(Dog(), Walker)                      # ✅ True (runtime_checkable)
```

| Feature | ABC | Protocol |
|---|:---:|:---:|
| Nominal (must inherit) | ✓ | ✗ |
| Structural (duck-typed) | ✗ | ✓ |
| `isinstance` works | ✓ | ✓ (if `@runtime_checkable`) |
| Static type checker support | ✓ | ✓ |
| Can share code | ✓ | ✗ |

See [[protocols-and-type-hints]].

---

## 9. Dataclasses — All Field Options

```python
from dataclasses import dataclass, field, InitVar
from typing import ClassVar

@dataclass(
    init=True,              # auto __init__
    repr=True,              # auto __repr__
    eq=True,                # auto __eq__
    order=False,            # auto __lt__, __le__, __gt__, __ge__
    unsafe_hash=False,      # auto __hash__
    frozen=False,           # immutable (also makes hashable)
    match_args=True,        # __match_args__ for pattern matching (3.10+)
    kw_only=False,          # all fields keyword-only (3.10+)
    slots=False,            # __slots__ (3.10+)
    weakref=False,          # support weakrefs
)
class Article:
    title: str                                  # required, positional
    author: str = "Anonymous"                   # default
    tags: list[str] = field(default_factory=list, repr=False, compare=False)
    views: int = field(init=False, default=0)   # set in __post_init__
    SECRET: ClassVar[str] = "n/a"               # class var, NOT a field
    debug: InitVar[bool] = False                # init-only, not stored

    def __post_init__(self, debug: bool) -> None:
        if debug: print(f"Created: {self.title}")
        # self.views = 0  # could also initialize here instead of field default
```

### `field()` options

| Option | Effect |
|---|---|
| `default=x` | Default value (must be immutable) |
| `default_factory=f` | Called for default (use for mutables) |
| `init=False` | Not in `__init__` |
| `repr=False` | Hide from `__repr__` |
| `compare=False` | Exclude from `__eq__` / `__lt__` |
| `hash=False` | Exclude from `__hash__` (only if `unsafe_hash` or `frozen`) |
| `metadata={}` | Arbitrary metadata for downstream tools |
| `kw_only=True` | Force keyword-only (3.10+) |

### Frozen gotchas

```python
@dataclass(frozen=True)
class Money:
    amount: int
    items: list  # ❌ list is mutable — frozen doesn't make this deep!
```

See [[dataclasses-and-attrs]].

---

## 10. NamedTuple

```python
from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float = 0.0           # default allowed
    label: str = "origin"

p = Point(1.0, 2.0, "A")
p.x                          # 1.0      — attribute access
p[0]                         # 1.0      — index access
p._replace(x=5.0)            # new Point(5.0, 2.0, "A")   — immutable update
tuple(p)                     # (1.0, 2.0, "A")
```

| | `@dataclass` | `NamedTuple` |
|---|---|---|
| Mutable by default | ✓ | ✗ (immutable) |
| Inheritance | ✓ | Limited |
| Methods | Full | Limited |
| Memory | Larger | Smaller (subclass of `tuple`) |
| Indexable | ✗ | ✓ |
| Hashable | If `frozen=True` | ✓ always |

---

## 11. The Complete Dunder Method Catalog

### Construction & Lifecycle
| Dunder | Triggers |
|---|---|
| `__new__(cls, ...)` | `Cls(...)` — creates instance |
| `__init__(self, ...)` | `Cls(...)` — initializes |
| `__del__(self)` | GC / interpreter exit |
| `__post_init__(self)` | `@dataclass` post-init hook |

### Representation
| Dunder | Triggers |
|---|---|
| `__repr__(self)` | `repr(x)` / interactive |
| `__str__(self)` | `str(x)` / `print(x)` |
| `__format__(self, spec)` | `f"{x:spec}"` / `format(x, spec)` |
| `__bytes__(self)` | `bytes(x)` |
| `__bool__(self)` | `bool(x)` / `if x:` |

### Comparison
| Dunder | Triggers |
|---|---|
| `__eq__`, `__ne__` | `==`, `!=` |
| `__lt__`, `__le__`, `__gt__`, `__ge__` | `<`, `<=`, `>`, `>=` |
| `__hash__(self)` | `hash(x)` / dict keys |
| `__bool__(self)` | `bool(x)` |

> [!warning] `__eq__` without `__hash__` makes the object unhashable. Pair them.

### Arithmetic
| Dunder | Op | Reflected | In-place |
|---|---|---|---|
| `__add__` | `+` | `__radd__` | `__iadd__` |
| `__sub__` | `-` | `__rsub__` | `__isub__` |
| `__mul__` | `*` | `__rmul__` | `__imul__` |
| `__truediv__` | `/` | `__rtruediv__` | `__itruediv__` |
| `__floordiv__` | `//` | `__rfloordiv__` | `__ifloordiv__` |
| `__mod__` | `%` | `__rmod__` | `__imod__` |
| `__pow__` | `**` | `__rpow__` | `__ipow__` |
| `__matmul__` | `@` | `__rmatmul__` | `__imatmul__` |
| `__neg__`, `__pos__`, `__abs__` | unary `-`, `+`, `abs()` | — | — |

### Containers
| Dunder | Triggers |
|---|---|
| `__len__(self)` | `len(x)` |
| `__getitem__(self, key)` | `x[key]` |
| `__setitem__(self, key, val)` | `x[key] = val` |
| `__delitem__(self, key)` | `del x[key]` |
| `__contains__(self, item)` | `item in x` |
| `__iter__(self)` | `iter(x)` / `for ... in x` |
| `__next__(self)` | next value from iterator |
| `__reversed__(self)` | `reversed(x)` |
| `__missing__(self, key)` | dict subclass fallback for missing key |

### Context Managers
| Dunder | Triggers |
|---|---|
| `__enter__(self)` | `with x as y:` (returns `y`) |
| `__exit__(self, exc_type, exc, tb)` | end of `with` block |

### Callable & Descriptors
| Dunder | Triggers |
|---|---|
| `__call__(self, ...)` | `x(...)` |
| `__get__(self, obj, owner)` | attribute access on descriptor |
| `__set__(self, obj, value)` | attribute set on descriptor |
| `__delete__(self, obj)` | `del obj.attr` on descriptor |
| `__set_name__(self, owner, name)` | called when class body finishes |

### Attribute Access
| Dunder | Triggers |
|---|---|
| `__getattr__(self, name)` | `x.foo` when normal lookup fails |
| `__getattribute__(self, name)` | every `x.foo` (handle with care!) |
| `__setattr__(self, name, value)` | `x.foo = v` |
| `__delattr__(self, name)` | `del x.foo` |
| `__dir__(self)` | `dir(x)` |

### Type Hints & Generics
| Dunder | Triggers |
|---|---|
| `__class_getitem__(cls, item)` | `Cls[int]` |
| `__init_subclass__(cls, **kw)` | subclass creation hook |

### Pickle & Copy
| Dunder | Triggers |
|---|---|
| `__getstate__`, `__setstate__`, `__reduce__` | pickle |
| `__copy__`, `__deepcopy__` | `copy.copy` / `copy.deepcopy` |

See [[magic-methods]] for the full deep dive.

---

## 12. Magic Method Recipes (Minimal)

### String/Repr

```python
class Point:
    def __init__(self, x: int, y: int) -> None: self.x, self.y = x, y
    def __repr__(self) -> str: return f"Point({self.x}, {self.y})"
    def __str__(self) -> str:  return f"({self.x}, {self.y})"
    def __format__(self, spec: str) -> str:
        if spec == "p": return f"({self.x},{self.y})"
        return str(self)
```

### Comparison

```python
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, major: int, minor: int) -> None:
        self.major, self.minor = major, minor
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Version) and (self.major, self.minor) == (other.major, other.minor)
    def __lt__(self, other: "Version") -> bool:
        return (self.major, self.minor) < (other.major, other.minor)
    def __hash__(self) -> int: return hash((self.major, self.minor))
```

### Arithmetic (Vector)

```python
class V:
    def __init__(self, *coords: float) -> None: self.coords = coords
    def __add__(self, other: "V") -> "V": return V(*(a + b for a, b in zip(self.coords, other.coords)))
    def __radd__(self, other: "V") -> "V": return self + other
    def __mul__(self, k: float) -> "V":    return V(*(c * k for c in self.coords))
    def __rmul__(self, k: float) -> "V":   return self * k
    def __eq__(self, other: object) -> bool:
        return isinstance(other, V) and self.coords == other.coords
    def __hash__(self) -> int: return hash(self.coords)
```

### Container (Matrix)

```python
class Matrix:
    def __init__(self, data: list[list[float]]) -> None: self.data = data
    def __getitem__(self, key: tuple[int, int]) -> float:
        i, j = key; return self.data[i][j]
    def __setitem__(self, key: tuple[int, int], v: float) -> None:
        i, j = key; self.data[i][j] = v
    def __len__(self) -> int: return len(self.data)
    def __contains__(self, v: float) -> bool: return any(v in row for row in self.data)
    def __iter__(self):  # yield rows
        yield from self.data
```

### Iterator / Iterable

```python
class Countdown:
    def __init__(self, n: int) -> None: self.n = n
    def __iter__(self) -> "Countdown": return self
    def __next__(self) -> int:
        if self.n <= 0: raise StopIteration
        self.n -= 1
        return self.n + 1

# Iterable only (returns a separate iterator):
class Range3:
    def __iter__(self): return iter([1, 2, 3])
```

### Context Manager

```python
class Timer:
    def __enter__(self) -> "Timer":
        import time; self.start = time.perf_counter(); return self
    def __exit__(self, exc_type, exc, tb) -> None:
        import time; print(f"{time.perf_counter() - self.start:.3f}s")

with Timer() as t:
    sum(range(1_000_000))
```

### Callable

```python
class Multiplier:
    def __init__(self, k: float) -> None: self.k = k
    def __call__(self, x: float) -> float: return x * self.k

double = Multiplier(2)
double(5)    # 10
```

### Descriptor

```python
class Validated:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = "_" + name
    def __get__(self, obj, owner): return getattr(obj, self.name) if obj else self
    def __set__(self, obj, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("must be non-negative int")
        setattr(obj, self.name, value)

class Product:
    quantity = Validated()
    def __init__(self, q: int) -> None: self.quantity = q
```

See [[magic-methods]] · [[properties]] (descriptors).

---

## 13. Type Hints for OOP

```python
from typing import ClassVar, Self, TypeVar, Generic, overload, Protocol, final

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None: self._items: list[T] = []
    def push(self, x: T) -> None: self._items.append(x)
    def pop(self) -> T: return self._items.pop()
    @classmethod
    def of(cls, items: list[T]) -> "Stack[T]": ...
    def __class_getitem__(cls, item): return cls   # for Stack[int] at runtime

class Animal:
    species: ClassVar[str] = "Animalia"             # ClassVar = on the class, not instance
    def reproduce(self) -> "Self":                  # Self (3.11+) = returns same subclass
        return type(self)()

@overload
def parse(s: str) -> dict: ...
@overload
def parse(s: bytes) -> dict: ...
def parse(s): ...                                   # implementation

@final
class FinalClass: ...                               # mypy: cannot subclass
```

| Hint | Meaning | When to use |
|---|---|---|
| `Self` | "an instance of the (sub)class" | Methods that return new instances of same class |
| `ClassVar[T]` | Attribute is on the class, not instance | Distinguish class attrs from instance attrs |
| `TypeVar("T")` | Generic type parameter | Container/algorithm generic |
| `TypeVar("T", bound=Foo)` | Constrained to Foo subtypes | Need Foo's API on T |
| `TypeVar("T", str, bytes)` | Constrained to str or bytes | Multiple concrete constraints |
| `Generic[T]` | Marks class as generic | `class Stack(Generic[T])` |
| `@overload` | Multiple signatures, one impl | Function with overloads |
| `Protocol` | Structural interface | Duck-typed contracts |
| `@final` | Cannot subclass / override | Lock down API |
| `"ForwardRef"` | String annotation | Forward references |

See [[protocols-and-type-hints]].

---

## 14. Metaclasses — Brief

```python
# Simplest: __init_subclass__ (covers 95% of cases)
class Plugin:
    registry: ClassVar[dict[str, type]] = {}
    def __init_subclass__(cls, key: str, **kw) -> None:
        super().__init_subclass__(**kw)
        Plugin.registry[key] = cls

class Auth(Plugin, key="auth"): ...
class Cache(Plugin, key="cache"): ...
print(Plugin.registry)         # {'auth': <class 'Auth'>, 'cache': <class 'Cache'>}
```

```python
# Real metaclass (use sparingly!)
class LogMeta(type):
    def __new__(mcs, name, bases, ns):
        cls = super().__new__(mcs, name, bases, ns)
        print(f"Created class: {name}")
        return cls

class Logged(metaclass=LogMeta): ...
```

| Tool | When to use |
|---|---|
| `__init_subclass__` | Hook into subclass creation (most cases) |
| `__class_getitem__` | Support `Cls[T]` syntax |
| Custom metaclass | When you must intercept class creation itself (rare) |
| `abc.ABCMeta` | Building abstract base classes |
| `enum.EnumMeta` | Building enum types (don't reinvent) |

> [!warning] "Metaclasses are deeper magic than 99% of users should ever worry about."
> — Tim Peters. See [[metaclasses-and-class-creation]].

---

## 15. "Which Feature for Which Job" Decision Table

| Job | Use | Not this |
|---|---|---|
| Validate an attribute on set | `@property` + setter | `set_x()` / `setX()` Java-style |
| Compute derived value | `@property` (cheap) or method (expensive/side-effects) | Public attribute |
| Cache computation | `@cached_property` | Manual `self._cache` dict |
| Alternate constructor | `@classmethod` (e.g. `from_string`) | Top-level function |
| Class-level constant | Class attribute (uppercase name) | Module constant inside class |
| Bundled utility fn | `@staticmethod` (or top-level fn) | Instance method that ignores `self` |
| Force override | `@abstractmethod` + `ABC` | Comment saying "must override" |
| Duck-typed interface | `typing.Protocol` | ABC inheritance |
| Data bag w/ equality | `@dataclass` | Hand-written `__init__` + `__eq__` |
| Immutable value object | `@dataclass(frozen=True)` | `NamedTuple` (if you want indexing) |
| Singleton | module-level instance or `__new__` (rare) | `global` |
| Polymorphic behavior | Inheritance, Protocol, or first-class fn | `if isinstance(...)` chains |
| Add behavior w/o subclassing | Decorator pattern (GoF) or Python `@decorator` | Deep subclass tree |
| Object lifecycle hooks | `__enter__`/`__exit__`, `__post_init__` | `__del__` |
| Customize class creation | `__init_subclass__` | Metaclass (until you've ruled out the simpler option) |
| Runtime "is X a Y?" | `isinstance` (with ABC/Protocol) | `type(x) == Y` |

---

## 16. Gotchas Cheat-List

> [!danger] Top 12 foot-guns
> 1. **Mutable default class attributes** — shared across all instances. Use `default_factory`.
> 2. **Mutable default arguments** in `__init__` (`def f(x=[])`). Same trap.
> 3. **Forgetting `self`** in method definitions → `TypeError` at call time.
> 4. **`__eq__` without `__hash__`** → object becomes unhashable (can't use as dict key).
> 5. **Setting a class attribute via `self.x =`** when you meant to mutate the class attr — creates instance attr shadowing class.
> 6. **`@cached_property` + `__slots__`** without `__dict__` slot → `AttributeError`.
> 7. **`super()` in `__new__`** — must pass `cls`: `super().__new__(cls)`.
> 8. **Calling `__init__` from `__new__`** — Python does this for you; don't double-init.
> 9. **Diamond inheritance + non-cooperative `super()`** — fix by making all bases cooperative.
> 10. **`__getattr__` vs `__getattribute__`** — the latter is called *every* time and is recursion-prone.
> 11. **Returning `NotImplemented` vs raising** — return `NotImplemented` from `__eq__` etc. for cooperative comparison.
> 12. **Subclassing built-ins** (`list`, `dict`) without overriding the right methods — C-level shortcuts bypass your overrides. Use `collections.UserList`/`UserDict`.

See [[common-mistakes-cheatsheet]] for full bad/good pairs.

---

## 🔑 Key Takeaways

- Python gives you **many ways to declare a class** — pick the simplest that works.
- The construction trio `__new__` / `__init__` / `__del__` is rarely all needed — `__init__` covers 99% of cases.
- **Class attributes are shared; instance attributes are not.** Mutable class attributes are a foot-gun.
- The three method kinds (instance / class / static) answer: *"what do I need access to?"*
- `@property` is the Pythonic getter/setter — but only add it when you need it.
- `super()` is cooperative — make sure every class in your hierarchy plays along.
- ABCs enforce at instantiation; Protocols check structurally — choose by philosophy.
- `@dataclass` removes 80% of class boilerplate; learn its full options menu.
- The dunder catalog is large but you'll only reach for ~15 regularly.
- Modern Python favors `typing.Self`, `ClassVar`, `Protocol`, `@overload`, `@final` for precise, checkable OOP.
- **Metaclasses are deep magic** — prefer `__init_subclass__` until you've exhausted it.
- When in doubt, link out: every snippet here has a deep-dive note behind it.

---

*See also: [[oop-quick-reference]] · [[classes-and-objects]] · [[methods]] · [[properties]] · [[magic-methods]] · [[dataclasses-and-attrs]] · [[metaclasses-and-class-creation]] · [[protocols-and-type-hints]] · [[common-mistakes-cheatsheet]]*
