import re

with open("c:/Users/owais/OneDrive/Desktop/study material/learning-material/05_Computer_Science_and_OOP/OOP/06-Design-Patterns/Behavioral-Patterns.md", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Chain of Responsibility
text = text.replace(
    "from dataclasses import dataclass\n",
    "from dataclasses import dataclass\nfrom typing import Self, override\n"
)
text = text.replace(
    '    def set_next(self, middleware: "Middleware") -> "Middleware":',
    '    def set_next(self, middleware: Self) -> Self:'
)
text = text.replace(
    '    def handle(self, request: Request) -> Response | None:\n        token = request.headers.get("Authorization", "")',
    '    @override\n    def handle(self, request: Request) -> Response | None:\n        token = request.headers.get("Authorization", "")'
)
text = text.replace(
    '    def handle(self, request: Request) -> Response | None:\n        if request.method == "OPTIONS":',
    '    @override\n    def handle(self, request: Request) -> Response | None:\n        if request.method == "OPTIONS":'
)
text = text.replace(
    '    def handle(self, request: Request) -> Response | None:\n        self._count += 1',
    '    @override\n    def handle(self, request: Request) -> Response | None:\n        self._count += 1'
)
text = text.replace(
    '    def handle(self, request: Request) -> Response | None:\n        return Response(200, f"Hello! You requested {request.path}")',
    '    @override\n    def handle(self, request: Request) -> Response | None:\n        return Response(200, f"Hello! You requested {request.path}")'
)

# 2. Command
text = text.replace(
    'from abc import ABC, abstractmethod\n\n\nclass TextEditor',
    'from abc import ABC, abstractmethod\nfrom typing import override\n\n\nclass TextEditor'
)
text = text.replace('    def execute(self) -> None:\n        self._editor.insert(self._text, self._position)', '    @override\n    def execute(self) -> None:\n        self._editor.insert(self._text, self._position)')
text = text.replace('    def undo(self) -> None:\n        if not self._executed:', '    @override\n    def undo(self) -> None:\n        if not self._executed:')
text = text.replace('    def execute(self) -> None:\n        self._deleted_text = self._editor.delete', '    @override\n    def execute(self) -> None:\n        self._deleted_text = self._editor.delete')
text = text.replace('    def undo(self) -> None:\n        self._editor.insert(self._deleted_text', '    @override\n    def undo(self) -> None:\n        self._editor.insert(self._deleted_text')
text = text.replace('    def execute(self) -> None:\n        for cmd in self._commands:', '    @override\n    def execute(self) -> None:\n        for cmd in self._commands:')
text = text.replace('    def undo(self) -> None:\n        # Undo in reverse order!', '    @override\n    def undo(self) -> None:\n        # Undo in reverse order!')

# 3. Interpreter
text = text.replace(
    'from typing import Any\n\n\nclass Expression',
    'from typing import Any, override\n\n\nclass Expression'
)
for c in ['Equals', 'GreaterThan', 'And', 'Or', 'Not']:
    text = re.sub(rf'class {c}\(Expression\):(.*?)\n    def interpret', rf'class {c}(Expression):\g<1>\n    @override\n    def interpret', text, flags=re.DOTALL)

# 4. Mediator
text = text.replace(
    'from abc import ABC, abstractmethod\nfrom datetime import datetime\n\n\nclass ChatRoom',
    'from abc import ABC, abstractmethod\nfrom datetime import datetime\nfrom typing import override\n\n\nclass ChatRoom'
)
text = text.replace('    def receive(self, message: str) -> None:\n        self.inbox.append(message)', '    @override\n    def receive(self, message: str) -> None:\n        self.inbox.append(message)')

# 6. Observer
text = text.replace(
    'from abc import ABC, abstractmethod\nfrom dataclasses import dataclass\n\n\n@dataclass',
    'from abc import ABC, abstractmethod\nfrom dataclasses import dataclass\nfrom typing import override\n\n\n@dataclass'
)
text = text.replace(
    '    def update(self, subject, payload: PriceUpdate) -> None:\n        print(f"[{self.name}]',
    '    @override\n    def update(self, subject, payload: PriceUpdate) -> None:\n        print(f"[{self.name}]'
)
text = text.replace(
    '    def update(self, subject, payload: PriceUpdate) -> None:\n        if payload.symbol',
    '    @override\n    def update(self, subject, payload: PriceUpdate) -> None:\n        if payload.symbol'
)

# 7. State
text = text.replace(
    'from abc import ABC, abstractmethod\n\n\nclass VendingMachine',
    'from abc import ABC, abstractmethod\nfrom typing import override\n\n\nclass VendingMachine'
)
for method in ['insert_coin', 'select']:
    for state_cls in ['IdleState', 'HasCoinState', 'DispensingState']:
        text = re.sub(rf'class {state_cls}\(State\):(.*?)\n    def {method}', rf'class {state_cls}(State):\g<1>\n    @override\n    def {method}', text, flags=re.DOTALL)

# 8. Strategy
text = text.replace(
    'from abc import ABC, abstractmethod\nimport gzip',
    'from abc import ABC, abstractmethod\nfrom typing import override\nimport gzip'
)
for method in ['compress', 'decompress']:
    for strategy_cls in ['GzipStrategy', 'Bzip2Strategy', 'LzmaStrategy']:
        text = re.sub(rf'class {strategy_cls}\(CompressionStrategy\):(.*?)\n    def {method}', rf'class {strategy_cls}(CompressionStrategy):\g<1>\n    @override\n    def {method}', text, flags=re.DOTALL)
for strategy_cls in ['GzipStrategy', 'Bzip2Strategy', 'LzmaStrategy']:
    text = re.sub(rf'class {strategy_cls}\(CompressionStrategy\):(.*?)\n    @property\n    def name', rf'class {strategy_cls}(CompressionStrategy):\g<1>\n    @property\n    @override\n    def name', text, flags=re.DOTALL)

for cls_name in ['StripeStrategy', 'PayPalStrategy', 'CryptoStrategy']:
    text = re.sub(rf'class {cls_name}\(PaymentStrategy\):(.*?)\n    def pay', rf'class {cls_name}(PaymentStrategy):\g<1>\n    @override\n    def pay', text, flags=re.DOTALL)

# 9. Template Method
text = text.replace(
    'from abc import ABC, abstractmethod\nfrom typing import Any, Iterable\n\n\nclass DataPipeline',
    'from abc import ABC, abstractmethod\nfrom typing import Any, Iterable, override\n\n\nclass DataPipeline'
)
for method in ['extract', 'transform', 'load', 'after_load']:
    text = re.sub(rf'class CSVToDatabasePipeline\(DataPipeline\):(.*?)\n    def {method}', rf'class CSVToDatabasePipeline(DataPipeline):\g<1>\n    @override\n    def {method}', text, flags=re.DOTALL)
for method in ['extract', 'transform', 'load']:
    text = re.sub(rf'class APIToJSONPipeline\(DataPipeline\):(.*?)\n    def {method}', rf'class APIToJSONPipeline(DataPipeline):\g<1>\n    @override\n    def {method}', text, flags=re.DOTALL)

# 10. Visitor
visitor_old = """```python
from abc import ABC, abstractmethod


class Node(ABC):
    @abstractmethod
    def accept(self, visitor: "Visitor") -> Any: ...


class Number(Node):
    def __init__(self, value: float):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_number(self)


class Add(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visit_add(self)


class Multiply(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visit_multiply(self)


from typing import Any


class Visitor(ABC):
    @abstractmethod
    def visit_number(self, n: Number) -> Any: ...

    @abstractmethod
    def visit_add(self, a: Add) -> Any: ...

    @abstractmethod
    def visit_multiply(self, m: Multiply) -> Any: ...


class Evaluator(Visitor):
    def visit_number(self, n: Number) -> float:
        return n.value

    def visit_add(self, a: Add) -> float:
        return a.left.accept(self) + a.right.accept(self)

    def visit_multiply(self, m: Multiply) -> float:
        return m.left.accept(self) * m.right.accept(self)


class Printer(Visitor):
    def visit_number(self, n: Number) -> str:
        return str(n.value)

    def visit_add(self, a: Add) -> str:
        return f"({a.left.accept(self)} + {a.right.accept(self)})"

    def visit_multiply(self, m: Multiply) -> str:
        return f"({m.left.accept(self)} * {m.right.accept(self)})"


# Build: (3 + 4) * (2 + 5)
expr = Multiply(Add(Number(3), Number(4)), Add(Number(2), Number(5)))

print(Evaluator().visit_multiply(expr))   # 49.0  -- but better to use accept:
print(expr.accept(Evaluator()))           # 49.0
print(expr.accept(Printer()))             # ((3 + 4) * (2 + 5))
```

The `accept` method does **double dispatch**: the visitor's `visit_*` method is chosen based on both (a) the visitor type and (b) the element type. Adding a new visitor (e.g., `TypeChecker`) requires no changes to the `Node` classes."""

visitor_new = """```python
from dataclasses import dataclass
from typing import Any


@dataclass
class Node:
    pass


@dataclass
class Number(Node):
    value: float


@dataclass
class Add(Node):
    left: Node
    right: Node


@dataclass
class Multiply(Node):
    left: Node
    right: Node


class Evaluator:
    def visit(self, node: Node) -> float:
        match node:
            case Number(value):
                return value
            case Add(left, right):
                return self.visit(left) + self.visit(right)
            case Multiply(left, right):
                return self.visit(left) * self.visit(right)
            case _:
                raise ValueError("Unknown node")


class Printer:
    def visit(self, node: Node) -> str:
        match node:
            case Number(value):
                return str(value)
            case Add(left, right):
                return f"({self.visit(left)} + {self.visit(right)})"
            case Multiply(left, right):
                return f"({self.visit(left)} * {self.visit(right)})"
            case _:
                raise ValueError("Unknown node")


# Build: (3 + 4) * (2 + 5)
expr = Multiply(Add(Number(3), Number(4)), Add(Number(2), Number(5)))

print(Evaluator().visit(expr))           # 49.0
print(Printer().visit(expr))             # ((3 + 4) * (2 + 5))
```

Modern Python 3.10+ uses `match`/`case` structural pattern matching to replace the traditional **double dispatch** `accept` method. The visitor matches on the element types, which is far more concise. Adding a new visitor (e.g., `TypeChecker`) requires no changes to the `Node` classes."""

text = text.replace(visitor_old, visitor_new)

with open("c:/Users/owais/OneDrive/Desktop/study material/learning-material/05_Computer_Science_and_OOP/OOP/06-Design-Patterns/Behavioral-Patterns.md", "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
