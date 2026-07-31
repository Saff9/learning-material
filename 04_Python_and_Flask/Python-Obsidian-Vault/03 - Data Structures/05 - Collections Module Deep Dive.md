# Python 3.12+ Deep Dive: Collections, Itertools, Functools & Memory

This deep dive covers the modernization of Python datastructures using the `collections`, `itertools`, and `functools` modules. It also touches upon modern typing (Python 3.12+), memory profiling, custom context managers, asynchronous flows, and the upcoming GIL/free-threading evolution (PEP 703).

## 1. Context Managers & Resource Management
Before diving into collections, let's explore a custom context manager for memory profiling, which we'll use throughout our deep dive.

```python
import tracemalloc
from typing import Self
from types import TracebackType

class MemoryProfiler:
    """
    A custom context manager to measure memory usage of a block of code.
    Uses strict type annotations and supports PEP 673 `Self`.
    """
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.start_mem: int = 0

    def __enter__(self) -> Self:
        tracemalloc.start()
        self.start_mem, _ = tracemalloc.get_traced_memory()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None
    ) -> bool | None:
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        used_mem: int = current_mem - self.start_mem
        print(f"[{self.name}] Memory used: {used_mem / 10**6:.4f} MB (Peak: {peak_mem / 10**6:.4f} MB)")
        return False
```

## 2. Collections Module Deep Dive

### 2.1. `Counter`
A `Counter` is a `dict` subclass for counting hashable objects.

```python
from collections import Counter
from typing import TypeVar, Iterable

T = TypeVar('T')

def count_frequencies(items: Iterable[T]) -> Counter[T]:
    """
    Counts the occurrences of items in an iterable.
    
    Args:
        items: An iterable of hashable items.
        
    Returns:
        A Counter mapping each item to its frequency.
    """
    return Counter(items)

if __name__ == "__main__":
    with MemoryProfiler("Counter test"):
        sample_text: str = "apple banana apple strawberry banana apple"
        words: list[str] = sample_text.lower().split()
        result: Counter[str] = count_frequencies(words)
        print(f"Word counts: {result}")
```

### 2.2. `defaultdict`
`defaultdict` calls a factory function to supply missing values.

```python
from collections import defaultdict
from typing import Sequence

def group_by_first_letter(words: Sequence[str]) -> dict[str, list[str]]:
    """
    Groups words by their starting letter.
    """
    # dict[str, list[str]] type hint is compatible with defaultdict
    grouped: defaultdict[str, list[str]] = defaultdict(list)
    for word in words:
        if word:
            grouped[word[0]].append(word)
    return dict(grouped)

if __name__ == "__main__":
    with MemoryProfiler("defaultdict test"):
        words_list: list[str] = ["apple", "banana", "avocado", "blueberry"]
        print(group_by_first_letter(words_list))
```

### 2.3. `NamedTuple` vs `@dataclass`
In Python 3.12+, `typing.NamedTuple` and `dataclasses.dataclass` are the preferred ways to create structured types.

```python
from typing import NamedTuple
from dataclasses import dataclass

class PointNamed(NamedTuple):
    """Immutable point using NamedTuple."""
    x: float
    y: float

@dataclass(slots=True, frozen=True)
class PointDataClass:
    """
    Immutable point using dataclass with slots.
    Slots drastically reduce memory usage by avoiding per-instance __dict__.
    """
    x: float
    y: float

def distance_from_origin(p: PointNamed | PointDataClass) -> float:
    return (p.x**2 + p.y**2) ** 0.5
```

### 2.4. `deque` and Async Workloads
`deque` is a thread-safe, double-ended queue. With async workflows, it can be used for managing tasks.

```python
import asyncio
from collections import deque
from typing import Any

async def async_worker(task_queue: deque[str]) -> None:
    """
    An asynchronous worker that processes tasks from a deque.
    """
    while task_queue:
        task: str = task_queue.popleft()
        print(f"Processing {task}...")
        await asyncio.sleep(0.1)  # Simulate I/O bound work

async def main_async_workflow() -> None:
    tasks: deque[str] = deque([f"Task-{i}" for i in range(5)])
    print("Starting async workers...")
    await asyncio.gather(
        async_worker(tasks),
        async_worker(tasks)
    )

if __name__ == "__main__":
    asyncio.run(main_async_workflow())
```

## 3. Itertools & Functools

### 3.1. Itertools
`itertools` provides fast, memory-efficient tools for iterators.

```python
import itertools
from typing import Iterator

def generate_combinations(items: list[str], r: int) -> Iterator[tuple[str, ...]]:
    """Generates all combinations of length r from the items."""
    return itertools.combinations(items, r)

if __name__ == "__main__":
    with MemoryProfiler("Itertools combination"):
        perms = list(generate_combinations(["A", "B", "C", "D"], 2))
        print(f"Combinations: {perms}")
```

### 3.2. Functools and `@cache`
`functools.cache` (introduced in 3.9) and `@lru_cache` provide memoization.

```python
from functools import cache

@cache
def heavy_computation(n: int) -> int:
    """
    Computes nth Fibonacci number with caching.
    """
    if n < 2:
        return n
    return heavy_computation(n - 1) + heavy_computation(n - 2)

if __name__ == "__main__":
    with MemoryProfiler("Functools cache"):
        print(f"Fib(100): {heavy_computation(100)}")
```

## 4. PEP 703: Making the Global Interpreter Lock (GIL) Optional
Historically, CPython's GIL has prevented multiple native threads from executing Python bytecodes simultaneously. This has made multi-threading in Python effective only for I/O-bound tasks, not CPU-bound tasks.

**PEP 703 (Free-Threading CPython):**
- Python 3.13 introduces an experimental build without the GIL.
- **Impact on Collections:** Thread-safe collections like `deque` rely on atomic operations in CPython. In a free-threaded world, their internal implementations use biased reference counting and advanced locking mechanisms to ensure data integrity without the GIL.
- **Performance:** CPU-bound parallel processing using threading (instead of multiprocessing) becomes viable, opening doors for high-performance scientific computing and machine learning natively in Python threads.
