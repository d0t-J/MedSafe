from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "MedSafe API"
    app_description: str = (
        "Medicine side-effect and interaction checker powered by FDA data and Claude AI"
    )
    app_version: str = "1.0.0"


def get_settings() -> Settings:
    return Settings()
