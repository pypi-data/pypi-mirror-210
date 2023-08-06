# pyassorted #

A library has assorted utils in Pure-Python. There are 3 principles:

1. Light-weight
2. No dependencies
3. Pythonic usage.


* Documentation: https://dockhardman.github.io/pyassorted/
* PYPI: https://pypi.org/project/pyassorted/

## Installation ##
```shell
pip install pyassorted
```

## Modules ##
- pyassorted.asyncio.executor
- pyassorted.asyncio.io
- pyassorted.asyncio.utils
- pyassorted.cache.cache
- pyassorted.collections.sqlitedict
- pyassorted.datetime
- pyassorted.io.watch
- pyassorted.lock.filelock


## Modules Description and Usages ##

### pyassorted.asyncio ###

This Python module, `pyassorted.asyncio`, provides utility functions to facilitate easier and more effective asynchronous programming using Python's built-in `asyncio` library.

It provides a level of abstraction over some of the complexities of the `asyncio` and `concurrent.futures` library.

```python
import asyncio
from pyassorted.asyncio import run_func

def normal_func() -> bool:
    return True

async def async_func() -> bool:
    await asyncio.sleep(0.0)
    return True

async main():
    assert await run_func(normal_func) is True
    assert await run_func(async_func) is True

asyncio.run(main())
```

### pyassorted.asyncio.io ###

The `aio_open` function serves as a replacement for Python's built-in open function, creating an instance of the `AsyncIOWrapper` when invoked. It is designed to work in an async with block and follows a similar interface to the standard `open` function.

```python
import asyncio
from pyassorted.io import aio_open

async def main():
    # Write to a file
    async with aio_open("file.txt", "w") as f:
        await f.write("Hello")
    # Read file content
    async with aio_open("file.txt") as f:
        assert (await f.read()) == "Hello"

asyncio.run(main())
```

### pyassorted.cache ###

`pyassorted.cache` is a Python module that provides an interface for caching data to enhance performance by reducing expensive or time-consuming function calls and computations.

It includes the implementation of the Least Recently Used (LRU) cache policy and a `cached` decorator for easy application of caching to any function or coroutine function.

```python
import asyncio
from pyassorted.cache import LRU, cached

lru_cache = LRU()

# Cache function
@cached(lru_cache)
def add(a: int, b: int) -> int:
    return a + b

assert add(1, 2) == 3
assert lru_cache.hits == 0
assert lru_cache.misses == 1

assert add(1, 2) == 3
assert lru_cache.hits == 1
assert lru_cache.misses == 1

# Cache coroutine
@cached(lru_cache)
async def async_add(a: int, b: int) -> int:
    await asyncio.sleep(0)
    return a + b

assert add(1, 2) == 3
assert lru_cache.hits == 2
assert lru_cache.misses == 1
```

### pyassorted.collections.sqlitedict ###

The `pyassorted.collections.sqlitedict` module provides a dictionary-like interface to SQLite databases. This can be used as a persistent dictionary for Python objects, where keys are restricted to primitive types such as strings and numbers.

The SqliteDict class supports common dictionary operations like getting, setting, and determining the length, with the added feature of enabling these operations asynchronously.

The `async_set` and `async_get` methods use an asynchronous execution pattern, which can be very useful in applications with high IO operations, like web or network servers.

```python
import asyncio
from pyassorted.collections.sqlitedict import SqliteDict

sql_dict = SqliteDict(":memory:")
sql_dict["key"] = "value"
assert sql_dict["key"] == "value"

# Asynchronous usage
async def main():
    await sql_dict.async_set("key", "value")
    assert (await sql_dict.async_get("key")) == "value"
asyncio.run(main())
```

### pyassorted.datetime ###


The `pyassorted.datetime` module offers various utilities for managing and interacting with date and time in Python.

This module comprises two primary functions: `aware_datetime_now` and `iso_datetime_now`. The `aware_datetime_now` function provides the current datetime in a specified timezone, using pytz's timezone conversions for enhanced accuracy.

If no timezone is specified, it defaults to UTC. `iso_datetime_now` builds on `aware_datetime_now` and delivers the current datetime in ISO 8601 string format.

The module also features a `Timer` class, a versatile tool to measure elapsed time. It provides simple methods like `click` to start or mark time, `read` to read the elapsed time, and `reset` to start anew. The `Timer` class is also designed as a context manager, which allows it to be used efficiently within with statements.

These utilities make the `pyassorted.datetime` module a versatile tool for managing and measuring time in your Python applications.

- aware_datetime_now
```python
from pyassorted.datetime import aware_datetime_now, iso_datetime_now

print(aware_datetime_now())  # datetime.datetime
print(iso_datetime_now())  # Datetime ISO String
```

- Timer
```python
import time
from pyassorted.datetime import Timer

timer = Timer()
timer.click()
time.sleep(1)
timer.click()
print(round(timer.read()))  # 1

with timer:
    time.sleep(1)
print(round(timer.read()))  # 1
```

### pyassorted.io.watch ###

The `pyassorted.io.watch` module provides functionality to monitor files for changes. It includes two main functions: `watch` and `async_watch`. The `watch` function is a synchronous generator that continuously checks for modifications in a specified file and yields the file path whenever changes are detected.

The `async_watch` function, on the other hand, is an asynchronous generator doing the same but built for asynchronous programming.

```python
import asyncio
from pyassorted.io import async_watch, watch

def watch_file(filepath):
    for file in watch(filepath):
        print("File changed!")

async def async_watch_file(filepath):
    async for file in async_watch(filepath):
        print("File changed!")

filepath = "modifying_file.txt"
watch_file(filepath)
async_watch_file(filepath)
```

### pyassorted.lock ###

The `pyassorted.lock` module provides a soft file locking mechanism, ensuring that only one process can access a shared resource at a time.

Utilizing a lock file for status tracking, it facilitates both synchronous and asynchronous resource protection in multi-threaded and multi-process environments. Key features include adjustable timeouts, lock expiration, and custom lock file naming.

This module, compatible with standard and async context managers, can be seamlessly integrated into your project to maintain data consistency in concurrent operations.

```python
from concurrent.futures import ThreadPoolExecutor
from pyassorted.lock import FileLock

number = 0
tasks_num = 100
lock = FileLock()

def add_one():
    global number
    with lock:
        number += 1

with ThreadPoolExecutor(max_workers=40) as executor:
    futures = [executor.submit(add_one) for _ in range(tasks_num)]
    for future in futures:
        future.result()

assert number == tasks_num
```
