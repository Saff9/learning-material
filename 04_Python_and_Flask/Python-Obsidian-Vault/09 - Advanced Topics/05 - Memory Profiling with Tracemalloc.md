# Memory Profiling with Tracemalloc

Memory management in Python is usually handled automatically by the garbage collector, but understanding where memory is allocated can be critical for optimizing large applications.

The `tracemalloc` module is a debug tool to trace memory blocks allocated by Python. It provides detailed information on where memory is being allocated.

## Custom Context Manager for Tracing

Using a custom context manager is a Pythonic way to ensure `tracemalloc` is always safely started and stopped, even if an exception occurs.

```python
import tracemalloc
import contextlib
from collections.abc import Iterator

@contextlib.contextmanager
def trace_memory(frames: int = 1) -> Iterator[None]:
    """
    A custom context manager to safely start and stop tracemalloc.
    Yields control back to the block where memory allocations are traced.
    """
    tracemalloc.start(frames)
    try:
        yield
    finally:
        snapshot: tracemalloc.Snapshot = tracemalloc.take_snapshot()
        top_stats: list[tracemalloc.Statistic] = snapshot.statistics('lineno')
        
        print("\n[ Top 3 memory allocations in block ]")
        for stat in top_stats[:3]:
            print(stat)
            
        tracemalloc.stop()

def memory_intensive_task() -> list[dict[str, int]]:
    """
    Creates a large list of dictionaries to simulate memory allocation.
    """
    return [{"key": i} for i in range(100000)]

if __name__ == "__main__":
    with trace_memory(frames=10):
        _ = memory_intensive_task()
```

## Comparing Snapshots
You can take multiple snapshots and compare them to find memory leaks over time.

```python
import tracemalloc
import gc

def track_memory_leak() -> None:
    """
    Demonstrates how to compare snapshots to identify a leak.
    """
    tracemalloc.start()
    
    # Snapshot 1: Baseline
    snapshot1: tracemalloc.Snapshot = tracemalloc.take_snapshot()
    
    # Simulate an operation that leaks memory
    leaked_list: list[int] = [i for i in range(50000)]
    
    # Snapshot 2: After potential leak
    snapshot2: tracemalloc.Snapshot = tracemalloc.take_snapshot()
    
    # Compare snapshots
    top_stats: list[tracemalloc.StatisticDiff] = snapshot2.compare_to(snapshot1, 'lineno')
    
    print("[ Top 3 memory differences ]")
    for stat in top_stats[:3]:
        print(stat)
        
    tracemalloc.stop()

if __name__ == "__main__":
    track_memory_leak()
```

## Deep Dive: Object Allocation Traceback

Python 3.12+ provides enhanced error messages and deeper inspection. With `tracemalloc`, you can pinpoint the exact line of code that allocated a specific object.

```python
import tracemalloc

def create_objects() -> list[str]:
    return ["hello" * 100 for _ in range(1000)]

if __name__ == "__main__":
    tracemalloc.start(10) # Store 10 frames of traceback
    
    obj_list = create_objects()
    
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('traceback')
    
    stat = top_stats[0]
    print(f"Largest memory block: {stat.size / 1024:.1f} KiB")
    print("Traceback:")
    for line in stat.traceback.format():
        print(line)
        
    tracemalloc.stop()
```
