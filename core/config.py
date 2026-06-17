from dataclasses import dataclass
from dotenv import load_dotenv

import os

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "MedSafe API")
    app_description: str = os.getenv(
        "APP_DESCRIPTION",
        "Medicine side-effect and interaction checker powered by FDA data and Claude AI",
    )
    app_version: str = os.getenv("APP_VERSION", "1.0.0")


def get_settings() -> Settings:
    return Settings()
