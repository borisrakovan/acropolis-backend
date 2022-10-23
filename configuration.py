import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path.cwd()
load_dotenv(BASE_DIR / ".env")

print(BASE_DIR)


def path_to(*parts: str) -> Path:
    all_parts = [*parts]
    path = Path(BASE_DIR.parent).joinpath(*all_parts)
    path.mkdir(parents=True, exist_ok=True)
    return path


class Configuration:
    WEATHER_CACHE_DIR = path_to("data", "weather_cache")

    SERVICE_EMAIL_SERVER = "mail.hostmaster.sk"
    SERVICE_EMAIL_PORT_TLS = "587"
    SERVICE_EMAIL_ADDRESS = "acropolis@pergamon.sk"
    SERVICE_EMAIL_PASSWORD = "12345678"
