# Asyncio and Await Deep Dive

Modern Python (3.12+) has robust support for asynchronous programming via the `asyncio` module. This is highly beneficial for I/O-bound and high-level structured network code.

## 1. Event Loop and Basic Syntax

An event loop runs asynchronous tasks and callbacks, performs network IO operations, and runs subprocesses.

```python
import asyncio

async def fetch_data(task_id: int) -> dict[str, int]:
    """
    Simulates an asynchronous data fetch.
    """
    print(f"Task {task_id}: Starting fetch...")
    await asyncio.sleep(1)  # Simulate I/O delay
    print(f"Task {task_id}: Finished fetch!")
    return {"id": task_id, "data": task_id * 10}

async def main() -> None:
    """Main entrypoint for asyncio program."""
    result: dict[str, int] = await fetch_data(1)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## 2. Structured Concurrency with `TaskGroup` (Python 3.11+)

`asyncio.TaskGroup` provides a cleaner, safer, and strictly typed way to spawn multiple tasks and ensure they all complete (or fail together), replacing `asyncio.gather` for most use cases.

```python
import asyncio

async def compute_heavy(n: int) -> int:
    """Simulates a heavy async computation."""
    await asyncio.sleep(0.5)
    return n * n

async def main() -> None:
    async with asyncio.TaskGroup() as tg:
        task1: asyncio.Task[int] = tg.create_task(compute_heavy(10))
        task2: asyncio.Task[int] = tg.create_task(compute_heavy(20))
        
    # The TaskGroup ensures both tasks are done before exiting the block
    print(f"Results: {task1.result()}, {task2.result()}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 3. Custom Async Context Managers

You can create custom async context managers to handle setup and teardown for async resources, such as database connections or network sessions.

```python
import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

@asynccontextmanager
async def mock_db_connection(dsn: str) -> AsyncIterator[str]:
    """
    A custom async context manager for a database connection.
    """
    print(f"Connecting to database at {dsn}...")
    await asyncio.sleep(0.2) # Simulate connection delay
    connection_obj: str = f"ConnectionObject({dsn})"
    try:
        yield connection_obj
    finally:
        print(f"Closing database connection {dsn}...")
        await asyncio.sleep(0.1) # Simulate teardown delay

async def db_operation() -> None:
    async with mock_db_connection("postgres://localhost") as conn:
        print(f"Performing operation using {conn}")
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(db_operation())
```

## 4. `asyncio.to_thread`

For operations that are inherently blocking (like synchronous file I/O or legacy CPU-bound code) but need to be run in an event loop without blocking it, use `asyncio.to_thread`.

```python
import asyncio
import time

def blocking_io() -> str:
    """Simulates a blocking I/O operation (e.g., synchronous file read)."""
    time.sleep(1)
    return "Blocking I/O result"

async def main() -> None:
    print("Starting background task...")
    
    # Run the blocking operation in a separate thread, freeing the event loop
    result: str = await asyncio.to_thread(blocking_io)
    
    print(f"Task completed: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```
