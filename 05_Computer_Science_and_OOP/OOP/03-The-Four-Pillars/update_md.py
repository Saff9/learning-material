import re

with open(r'c:/Users/owais/OneDrive/Desktop/study material/learning-material/05_Computer_Science_and_OOP/OOP/03-The-Four-Pillars/encapsulation.md', 'r', encoding='utf-8') as f:
    content = f.read()

old_circle = '''class Circle(Shape):
    def describe(self):
        return f"A {self._color} circle"   # acceptable: subclass touching protected'''
new_circle = '''from typing import override

class Circle(Shape):
    @override
    def describe(self) -> str:
        return f"A {self._color} circle"   # acceptable: subclass touching protected'''
content = content.replace(old_circle, new_circle)

old_stack = '''# Better: separate, when you can afford it
class Stack:
    def peek(self):             # query — no mutation
        return self._items[-1]
    def pop(self) -> None:      # command — no return value
        self._items.pop()'''
new_stack = '''# Better: separate, when you can afford it
# Using Python 3.12+ Generic Syntax (PEP 695)
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def peek(self) -> T:        # query — no mutation
        return self._items[-1]

    def pop(self) -> None:      # command — no return value
        self._items.pop()

# --- Code Execution Trace ---
# 1. s = Stack[int]() -> Stack instance created. `self._items` initialized to `[]`.
# 2. s.push(42) -> `42` is appended to `self._items`. `self._items` is now `[42]`.
# 3. val = s.peek() -> returns `42` without modifying `self._items`.
# 4. s.pop() -> removes `42` from `self._items`. Returns `None`.'''
content = content.replace(old_stack, new_stack)

old_bank_account = '''    def withdraw(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError("withdraw must be positive")
        if amount > self.__balance + self._overdraft_limit:
            raise InsufficientFunds(self.__balance, amount)
        self.__balance -= amount
        self.__transactions.append(("withdraw", amount))
        return amount'''

new_bank_account = '''    def withdraw(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError("withdraw must be positive")
        if amount > self.__balance + self._overdraft_limit:
            raise InsufficientFunds(self.__balance, amount)
        self.__balance -= amount
        self.__transactions.append(("withdraw", amount))
        return amount

    def freeze(self) -> "Self":
        self._frozen = True
        return self'''
content = content.replace(old_bank_account, new_bank_account)

old_bank_acct_start = '''class BankAccount:
    """Encapsulated: state is private, mutation goes through methods."""'''
new_bank_acct_start = '''from typing import Self

class BankAccount:
    """Encapsulated: state is private, mutation goes through methods."""'''
content = content.replace(old_bank_acct_start, new_bank_acct_start)

mem_diagram = '''
### 2.3 Memory Allocation Diagram

Here is how the `BankAccount` object and its private attributes are laid out in memory, illustrating how Python's name mangling works under the hood.

```mermaid
block-beta
    columns 1
    Space["Heap Memory"]
    block:Obj["acct: BankAccount"]
        columns 2
        owner["owner"] owner_val["'Ada'"]
        limit["_overdraft_limit"] limit_val["100"]
        balance["_BankAccount__balance"] balance_val["-50"]
        trans["_BankAccount__transactions"] trans_val["[('deposit', 500), ('withdraw', 550)]"]
    end
    style Obj fill:#d4f1d4,stroke:#333,stroke-width:2px
```
'''
content = content.replace('## 3. Access Control in Python', mem_diagram + '\n## 3. Access Control in Python')

old_practice = '''## 14. Practice Exercises

1. **Encapsulate a `Password` class.** Store the password hashed (use `hashlib.sha256`). Expose only `password` as a write-only property (getter raises `PermissionError`). Add a `verify(plain) -> bool` method.
2. **Fix the leaky `Team.members()`.** Return an immutable view. Test that `team.members().append("x")` raises `AttributeError` (or returns a new list, your choice — justify the trade-off).
3. **Build a `Rectangle` with invariant `width >= 0 and height >= 0`** using `@property`. Add a computed `area` and a `resize(factor)` method that preserves the aspect ratio.
4. **Refactor for Demeter.** Given `order.customer.account.balance`, design a new interface where `Order` asks `Customer` for `billing_balance()` and `Customer` asks its own `Account`. Write both versions.
5. **Build a `TransactionLog`** that exposes a read-only `entries` property returning a tuple, and a `add(entry)` method that validates `entry.amount != 0`. Demonstrate that external code cannot append to the log.'''

new_practice = '''## 14. Practice Exercises

Below are problem statements along with starter templates to help you practice encapsulation, validation, and modern Python type hints.

### Exercise 1: The `Password` Class
**Problem Statement:** Encapsulate a password. Store the password hashed (use `hashlib.sha256`). Expose only `password` as a write-only property (getter raises `PermissionError`). Add a `verify(plain) -> bool` method.

**Solution Template:**
```python
import hashlib

class Password:
    def __init__(self, initial_password: str):
        # TODO: Route this through the setter
        pass

    @property
    def password(self) -> str:
        # TODO: Raise PermissionError
        pass

    @password.setter
    def password(self, plain: str) -> None:
        # TODO: Hash the plain password and store it in a private variable
        pass

    def verify(self, plain: str) -> bool:
        # TODO: Hash 'plain' and compare with the stored hash
        pass
```

### Exercise 2: Fixing Leaky State
**Problem Statement:** Fix the leaky `Team.members()`. Return an immutable view or copy so callers can't modify the internal team list.

**Solution Template:**
```python
class Team:
    def __init__(self):
        self.__members: list[str] = []

    def add(self, member: str) -> None:
        self.__members.append(member)

    def members(self) -> tuple[str, ...]:
        # TODO: Return a safe representation instead of self.__members directly
        pass
```

### Exercise 3: Maintaining Invariants
**Problem Statement:** Build a `Rectangle` with invariants `width >= 0` and `height >= 0` using `@property`. Add a computed `area` and a `resize(factor)` method that preserves the aspect ratio. Return `Self` from `resize` for a fluent API.

**Solution Template:**
```python
from typing import Self

class Rectangle:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    # TODO: Create @property and @setter for width and height

    @property
    def area(self) -> float:
        # TODO: Return area
        pass

    def resize(self, factor: float) -> Self:
        # TODO: Apply factor and return self
        pass
```
'''

content = content.replace(old_practice, new_practice)

with open(r'c:/Users/owais/OneDrive/Desktop/study material/learning-material/05_Computer_Science_and_OOP/OOP/03-The-Four-Pillars/encapsulation.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
