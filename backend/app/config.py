import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@lru_cache
def get_settings():
    return Settings()


class Settings:
    def __init__(self):
        self.port = int(os.getenv("PORT", "8090"))
        self.agri_bundle_secret = os.getenv("AGRI_BUNDLE_SECRET", "dev-change-me-bundle-secret")
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        self.expose_accuracy_report = os.getenv("AGRI_EXPOSE_ACCURACY_REPORT", "true").lower() in (
            "1",
            "true",
            "yes",
        )
