import asyncio
import time
from pathlib import Path
from typing import AsyncGenerator, Generator, Text, Tuple, Union


PathText = Union[Path, Text]


def watch(
    filepath: PathText,
    period: float = 0.1,
    raise_timeout_errors: Tuple = (TimeoutError,),
) -> Generator[Path, None, None]:
    """Watch a file for changes.

    Parameters
    ----------
    filepath : PathText
        Path to file to watch.
    period : float, optional
        period to check for changes, by default 0.1

    Yields
    ------
    PathText
        Path to file that has changed.

    Examples
    --------
    >>> from pyassorted.io import watch
    >>> for filepath in watch('file.txt'):
    ...     print(filepath)
    """

    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Path '{filepath}' does not exist.")
    file_mtime = filepath.stat().st_mtime

    while True:
        try:
            file_mtime_now = filepath.stat().st_mtime
            if file_mtime_now != file_mtime:
                file_mtime = file_mtime_now
                yield filepath
            else:
                time.sleep(period)
        except raise_timeout_errors as e:
            raise e


async def async_watch(
    filepath: PathText,
    period: float = 0.1,
    raise_timeout_errors: Tuple = (
        TimeoutError,
        asyncio.exceptions.TimeoutError,
    ),
) -> AsyncGenerator[Path, None]:
    """Watch a file for changes.

    Parameters
    ----------
    filepath : PathText
        Path to file to watch.
    period : float, optional
        period to check for changes, by default 0.1

    Examples
    --------
    >>> import asyncio
    >>> from pyassorted.io import watch
    >>> async def main():
    ...     async for filepath in async_watch("test.txt"):
    ...         print(filepath)
    >>> asyncio.run(main())
    """

    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Path '{filepath}' does not exist.")
    file_mtime = filepath.stat().st_mtime

    while True:
        try:
            file_mtime_now = filepath.stat().st_mtime
            if file_mtime_now != file_mtime:
                file_mtime = file_mtime_now
                yield filepath
            else:
                await asyncio.sleep(period)
        except raise_timeout_errors as e:
            raise e
