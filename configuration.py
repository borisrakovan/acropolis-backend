import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path.cwd()
load_dotenv(BASE_DIR / ".env")


def path_to(*parts: str) -> Path:
    all_parts = [*parts]
    path = Path(BASE_DIR.parent).joinpath(*all_parts)
    path.mkdir(parents=True, exist_ok=True)
    return path


class Configuration:
    WEATHER_CACHE_DIR = path_to("data", "weather_cache")
