import errno
import functools
import json
import logging
from pathlib import Path
from time import time
from typing import Any, Callable, TypeVar

from configuration import Configuration

_DecoratedFunction = TypeVar("_DecoratedFunction", bound=Callable[..., Any])

logger = logging.getLogger(__name__)


def safe_open(filename: Path, **kwargs):
    dirname = filename.parent.resolve()
    if not dirname.exists():
        try:
            dirname.mkdir(parents=True, exist_ok=True)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    return open(filename, **kwargs)


def file_cache(resource_name: str, key: str) -> Callable[[_DecoratedFunction], _DecoratedFunction]:

    directory = Configuration.WEATHER_CACHE_DIR / resource_name

    def read(filename: Path) -> str:
        with filename.open("r", encoding="utf-8") as f:
            content = json.load(f)
        logger.info(f"{resource_name} loaded from cache")
        return content

    def write(filename: Path, content: str):
        with safe_open(filename, mode="w", encoding="utf-8") as f:
            json.dump(content, f)

        logger.info(f"{resource_name} saved to cache")

    def decorator(func: _DecoratedFunction) -> _DecoratedFunction:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # key = '_'.join(str(arg) for arg in args) + '_' + '_'.join(f"{k}={v}" for k, v in kwargs.items())
            filename = directory / (key + ".txt")
            if filename.exists():
                content = read(filename)

            else:
                content = func(*args, **kwargs)
                try:
                    write(filename, content)
                except Exception as exc:
                    filename.unlink(missing_ok=True)
                    logger.error(f"Failed to write to cache: {str(exc)}")
            return content

        return wrapper

    return decorator


def timed(action_name: str) -> Callable[[_DecoratedFunction], _DecoratedFunction]:
    from functools import wraps

    def decorator(func: _DecoratedFunction) -> _DecoratedFunction:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"{action_name} started")
            start = time()
            result = func(*args, **kwargs)
            end = time()
            logger.info(f"{action_name} took {end - start:.2f} seconds")
            return result

        return wrapper

    return decorator
