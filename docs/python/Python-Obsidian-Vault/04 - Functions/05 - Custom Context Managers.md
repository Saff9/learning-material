# Custom Context Managers

Context managers allow you to allocate and release resources precisely when you want to. The most widely used example is the `with` statement for deterministic cleanup.

## 1. Class-Based Context Managers

To implement a context manager using a class, you need to define the `__enter__` and `__exit__` magic methods. This provides explicit control over initialization and teardown logic.

```python
import types
from typing import Any
import os

class FileManager:
    """
    A custom context manager for handling file operations securely.
    """
    def __init__(self, filename: str, mode: str) -> None:
        self.filename: str = filename
        self.mode: str = mode
        self.file: Any = None

    def __enter__(self) -> Any:
        print(f"Opening file: {self.filename}")
        self.file = open(self.filename, self.mode, encoding="utf-8")
        return self.file

    def __exit__(
        self, 
        exc_type: type[BaseException] | None, 
        exc_value: BaseException | None, 
        traceback: types.TracebackType | None
    ) -> bool:
        print(f"Closing file: {self.filename}")
        if self.file:
            self.file.close()
        
        if exc_type is not None:
            print(f"An exception occurred: {exc_value}")
            return False # Re-raise the exception
        return True

if __name__ == "__main__":
    with FileManager("test.txt", "w") as f:
        f.write("Hello, World!")
    
    # Cleanup for demo
    if os.path.exists("test.txt"):
        os.remove("test.txt")
```

## 2. Generator-Based Context Managers using `@contextmanager`

The `contextlib` module provides a decorator `@contextmanager` which allows you to write a generator function to serve as a context manager. This often leads to shorter, more readable code than the class-based approach.

```python
from contextlib import contextmanager
from typing import Iterator
import time

@contextmanager
def timer(label: str) -> Iterator[None]:
    """
    A context manager that times the execution of a code block.
    
    Args:
        label: A string label to identify the block being timed.
    """
    start_time: float = time.perf_counter()
    try:
        yield
    finally:
        end_time: float = time.perf_counter()
        print(f"[{label}] Execution time: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    with timer("heavy_computation"):
        total: int = sum(i * i for i in range(1_000_000))
        print(f"Computation complete, result ends with {str(total)[-4:]}")
```

## 3. Asynchronous Context Managers (`@asynccontextmanager`)

When working with modern Python asynchronous libraries (e.g., `asyncio`, `aiohttp`, `asyncpg`), asynchronous context managers (`__aenter__` and `__aexit__`) are essential to ensure non-blocking cleanup of network sockets, file descriptors, or database connections.

```python
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

@asynccontextmanager
async def mock_db_connection(db_url: str) -> AsyncIterator[dict[str, str]]:
    """
    An asynchronous context manager mocking a database connection.
    """
    print(f"Connecting to database at {db_url}...")
    await asyncio.sleep(0.5)  # Simulate network IO
    connection = {"status": "connected", "url": db_url}
    
    try:
        yield connection
    finally:
        print(f"Closing connection to {db_url}...")
        await asyncio.sleep(0.5)  # Simulate network teardown IO
        connection["status"] = "closed"

async def main() -> None:
    async with mock_db_connection("postgresql://localhost:5432/db") as conn:
        print(f"Active Connection State: {conn}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Contextlib Tools
The `contextlib` module also contains powerful primitives like:
- **`ExitStack`** and **`AsyncExitStack`**: Dynamically manage a variable number of context managers (e.g., opening multiple files dynamically in a loop).
- **`suppress`**: A context manager explicitly used to suppress specific exceptions (e.g., `with suppress(FileNotFoundError): os.remove('somefile.tmp')`).
