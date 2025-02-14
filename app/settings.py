import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from functools import lru_cache

from dotenv import load_dotenv

from utils import get_environment

load_dotenv()


@dataclass
class BaseSettings:

    def to_dict(self):
        return asdict(self)


@dataclass
class LogSettings(BaseSettings):
    log_level: int = logging.INFO if get_environment(
    ) == 'DEV' else logging.ERROR
    log_path: str = f'logs/{datetime.now().strftime("%Y/%m/%d")}'


@dataclass
class FlaskAPISettings(BaseSettings):
    host: str = os.getenv("FLASK_HOST", "0.0.0.0")
    port: int = int(os.getenv("FLASK_PORT", 8080))
    debug: bool = get_environment() == 'DEV'


@dataclass
class StractSettings(BaseSettings):
    token: str = os.getenv("STRACT_TOKEN", "")
    base_url: str = os.getenv("STRACT_BASE_URL", "")


@dataclass
class InfoSettings(BaseSettings):
    name: str = os.getenv("INFO_NAME", "")
    email: str = os.getenv("INFO_EMAIL", "")
    linkedin_url: str = os.getenv("INFO_LINKEDIN_URL", "")


class Settings:
    log_settings: LogSettings = LogSettings()
    flaskapi_settings: FlaskAPISettings = FlaskAPISettings()
    stract_settings: StractSettings = StractSettings()
    info_settings: InfoSettings = InfoSettings()


@lru_cache
def get_settings():
    return Settings()
