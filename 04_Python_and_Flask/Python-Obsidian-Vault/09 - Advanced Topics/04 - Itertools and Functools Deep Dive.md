# Itertools and Functools Deep Dive

## Itertools
The `itertools` module implements a number of iterator building blocks inspired by constructs from APL, Haskell, and SML. They are highly memory efficient and fast.

### 1. `chain`
Combine multiple iterables into one continuous stream.

```python
import itertools
from collections.abc import Iterable

def combine_and_print[T, U](iter1: Iterable[T], iter2: Iterable[U]) -> None:
    """
    Combines two iterables and prints them sequentially.
    Demonstrates Python 3.12+ generic type syntax.
    """
    for item in itertools.chain(iter1, iter2):
        print(item, end=" ")
    print()

if __name__ == "__main__":
    combine_and_print([1, 2, 3], ['a', 'b', 'c'])
```

### 2. `batched` (New in Python 3.12)
Batch data into tuples of a specific length.

```python
import itertools
from collections.abc import Iterable

def process_in_batches[T](data: Iterable[T], batch_size: int) -> None:
    """
    Processes an iterable in batches using itertools.batched (Python 3.12+).
    """
    for batch in itertools.batched(data, batch_size):
        print(f"Processing batch: {batch}")

if __name__ == "__main__":
    process_in_batches(range(10), 3)
```

### 3. `combinations` and `permutations`

```python
import itertools
from collections.abc import Sequence

def get_combinations[T](items: Sequence[T], length: int) -> list[tuple[T, ...]]:
    """Returns all combinations of a specific length."""
    return list(itertools.combinations(items, length))

if __name__ == "__main__":
    print(get_combinations(['A', 'B', 'C'], 2))
```

## Functools
The `functools` module is for higher-order functions: functions that act on or return other functions.

### 1. `cache` and `lru_cache`
Decorator to wrap a function with a memoizing callable. `cache` is simpler and faster if you don't need a size limit.

```python
import functools

@functools.cache
def fibonacci(n: int) -> int:
    """
    Calculates the n-th Fibonacci number efficiently using memoization.
    """
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

if __name__ == "__main__":
    print(fibonacci(100)) # Computes instantly
```

### 2. `partial`
Used for partial function application which "freezes" some portion of a function's arguments.

```python
import functools
from collections.abc import Callable

def power(base: int | float, exponent: int | float) -> int | float:
    """Returns base raised to the power of exponent."""
    return base ** exponent

# Create a new function that always squares its input
square: Callable[[int | float], int | float] = functools.partial(power, exponent=2)

if __name__ == "__main__":
    print(square(5)) # Output: 25
```

### 3. Custom Context Manager with `contextmanager`
Using `functools` and `contextlib` to create robust context managers.

```python
import contextlib
from collections.abc import Iterator

@contextlib.contextmanager
def temporary_state(state_dict: dict[str, str], key: str, temp_value: str) -> Iterator[None]:
    """
    A custom context manager to temporarily change a state dictionary.
    """
    original_value = state_dict.get(key)
    state_dict[key] = temp_value
    try:
        yield
    finally:
        if original_value is None:
            del state_dict[key]
        else:
            state_dict[key] = original_value

if __name__ == "__main__":
    my_state = {"theme": "light"}
    with temporary_state(my_state, "theme", "dark"):
        print(f"Inside context: {my_state['theme']}")
    print(f"Outside context: {my_state['theme']}")
```
