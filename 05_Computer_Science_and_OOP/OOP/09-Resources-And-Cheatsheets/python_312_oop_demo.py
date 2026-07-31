import math
from typing import override, Self
from dataclasses import dataclass
from pydantic import BaseModel, Field

# 1. Dataclasses with kw_only=True and slots=True
@dataclass(kw_only=True, slots=True)
class Point:
    x: float
    y: float

# 2. Pydantic V2 Model
class User(BaseModel):
    id: int
    name: str = Field(min_length=1)
    email: str

# 3. PEP 695 Generics
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

# 4. typing.Self for fluent builder
class QueryBuilder:
    def __init__(self) -> None:
        self.query = ""

    def select(self, fields: str) -> Self:
        self.query += f"SELECT {fields} "
        return self

    def from_table(self, table: str) -> Self:
        self.query += f"FROM {table} "
        return self

# 5. PEP 698 @override decorator
class Animal:
    def speak(self) -> str:
        return "..."

class Dog(Animal):
    @override
    def speak(self) -> str:
        return "Woof!"

# 6. match/case for design pattern dispatch (Command Pattern)
@dataclass(kw_only=True, slots=True)
class MoveCommand:
    dx: int
    dy: int

@dataclass(kw_only=True, slots=True)
class AttackCommand:
    target: str

def execute_command(command: object) -> None:
    match command:
        case MoveCommand(dx, dy):
            print(f"Moving by {dx}, {dy}")
        case AttackCommand(target):
            print(f"Attacking {target}")
        case _:
            print("Unknown command")

def main() -> None:
    print("--- Modern Python OOP Demo ---")
    
    # Dataclass demo
    p = Point(x=10.0, y=20.0)
    print(f"Point: {p}")

    # Pydantic V2 demo
    u = User(id=1, name="Alice", email="alice@example.com")
    print(f"User: {u}")

    # Generics demo
    s = Stack[int]()
    s.push(1)
    s.push(2)
    print(f"Stack pop: {s.pop()}")

    # Fluent builder demo
    qb = QueryBuilder().select("*").from_table("users")
    print(f"Query: {qb.query}")

    # Override demo
    d = Dog()
    print(f"Dog says: {d.speak()}")

    # Match/case demo
    execute_command(MoveCommand(dx=5, dy=-2))
    execute_command(AttackCommand(target="Dragon"))

if __name__ == "__main__":
    main()
