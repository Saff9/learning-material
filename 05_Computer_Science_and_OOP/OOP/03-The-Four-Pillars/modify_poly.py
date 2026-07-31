import os
import re

file_path = "c:/Users/owais/OneDrive/Desktop/study material/learning-material/05_Computer_Science_and_OOP/OOP/03-The-Four-Pillars/polymorphism.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Edit 1: Generic typing (PEP 695)
content = re.sub(
    r'from typing import TypeVar, Generic\n\nT = TypeVar\("T"\)\n\nclass Stack\(Generic\[T\]\):',
    r'class Stack[T]:',
    content
)
content = re.sub(
    r'def first\(items: list\[T\]\) -> T:',
    r'def first[T](items: list[T]) -> T:',
    content
)

# Edit 2: Overrides in Subtype Polymorphism
content = content.replace(
'''class Animal:
    def speak(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    def speak(self) -> str: return "Woof"

class Cat(Animal):
    def speak(self) -> str: return "Meow"''',
'''from typing import override

class Animal:
    def speak(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    @override
    def speak(self) -> str: return "Woof"

class Cat(Animal):
    @override
    def speak(self) -> str: return "Meow"'''
)

# Add code execution trace to Subtype polymorphism
content = content.replace(
'''chorus([Dog(), Cat(), Dog()])      # Woof / Meow / Woof
```

This is the polymorphism you get for free from inheritance + method overriding.''',
'''chorus([Dog(), Cat(), Dog()])      # Woof / Meow / Woof
```

#### Code Execution Trace

1. **`chorus([Dog(), Cat(), Dog()])`**: The `chorus` function is called with a list of three instances.
2. **First iteration (`a` is `Dog`)**: Python calls `a.speak()`. At runtime, it checks the object's class (`Dog`), finds `Dog.speak()`, executes it, and returns `"Woof"`.
3. **Second iteration (`a` is `Cat`)**: The loop calls `a.speak()`. The runtime resolves the type as `Cat`, calls `Cat.speak()`, returning `"Meow"`.
4. **Third iteration (`a` is `Dog`)**: Similar to the first, resolving to `Dog.speak()`.

This is the polymorphism you get for free from inheritance + method overriding.'''
)

# Edit 3: typing.Self
content = content.replace(
'''class Vector:
    def __init__(self, x: float, y: float):''',
'''from typing import Self

class Vector:
    def __init__(self, x: float, y: float):'''
)
content = content.replace(
'''def __add__(self, other: "Vector") -> "Vector":''',
'''def __add__(self, other: Self) -> Self:'''
)
content = content.replace(
'''def __sub__(self, other: "Vector") -> "Vector":''',
'''def __sub__(self, other: Self) -> Self:'''
)
content = content.replace(
'''def __lt__(self, other: "Vector") -> bool:''',
'''def __lt__(self, other: Self) -> bool:'''
)

# Add memory diagram to Vector example
content = content.replace(
'''print(v[0], v[1])    # 1 2
```''',
'''print(v[0], v[1])    # 1 2
```

#### Memory Allocation Diagram (Operator Overloading)

When executing `v = Vector(1, 2)`, `w = Vector(3, 4)`, and `res = v + w`, the objects are allocated as follows:

```mermaid
block-beta
    columns 3
    block:v["v (Vector)"]
        x1["x: 1.0"] y1["y: 2.0"]
    end
    space
    block:w["w (Vector)"]
        x2["x: 3.0"] y2["y: 4.0"]
    end
    space space space
    block:res["res (Vector) - from v.__add__(w)"]
        x3["x: 4.0"] y3["y: 6.0"]
    end
    v --> res
    w --> res
```'''
)

# Edit 4: Replace Practice Exercises
old_exercises_re = r"## 14\. Practice Exercises.*"
new_exercises = """## 14. Practice Exercises

Here are some practice exercises with starter templates. Try to solve them utilizing Python 3.12+ syntax where appropriate.

### Exercise 1: Replace Conditional with Polymorphism
**Problem Statement:**
Refactor the following `NotificationSystem` to use subtype polymorphism instead of `isinstance` checks. Extend it by adding an `SMSNotification`.

```python
# Starter Template
class Email:
    def __init__(self, addr): self.addr = addr
class Push:
    def __init__(self, token): self.token = token

def send_notification(notification, msg):
    if isinstance(notification, Email):
        print(f"Sending Email to {notification.addr}: {msg}")
    elif isinstance(notification, Push):
        print(f"Sending Push to {notification.token}: {msg}")
    else:
        raise TypeError("Unknown notification type")

# TODO: Refactor using a common Notification ABC or Protocol.
```

### Exercise 2: Operator Overloading with `typing.Self`
**Problem Statement:**
Implement a `Point` class that supports addition and subtraction. Use `typing.Self` for the type hints.

```python
# Starter Template
from typing import Self

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        
    # TODO: Implement __add__ and __sub__ returning Self.
    
    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"
```

### Exercise 3: Structural Subtyping (Duck Typing) with Protocols
**Problem Statement:**
Define a `Renderable` protocol that requires a `render() -> str` method. Write a generic function `display[T: Renderable](item: T)` that calls `render()` on the item.

```python
# Starter Template
from typing import Protocol

# TODO: Define the Renderable protocol

# TODO: Implement a Widget class and a Text class that satisfy Renderable

# TODO: Implement the display function using the new PEP 695 generic syntax
```

### Exercise 4: Dynamic Dispatch (singledispatch)
**Problem Statement:**
Create a polymorphic `format_data` function using `@singledispatch` that formats `int`, `list`, and `dict` differently.

```python
# Starter Template
from functools import singledispatch

@singledispatch
def format_data(data) -> str:
    raise NotImplementedError("Unsupported type")

# TODO: Register handlers for int, list, and dict.
```
"""

content = re.sub(old_exercises_re, new_exercises, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Modification complete.")
