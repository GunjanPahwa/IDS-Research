"""Application configuration management via pydantic-settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """NIDS Backend Settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DEFAULT_DATASET: str = "unsw_nb15"
    MAX_BATCH_SIZE: int = 1000
    ARTIFACTS_DIR: str = "."
    MODELS_DIR: str = "models"
    PREPROCESSORS_DIR: str = "data/preprocessors"
    LOG_LEVEL: str = "INFO"

    @property
    def root_path(self) -> Path:
        return Path(self.ARTIFACTS_DIR).resolve()

    @property
    def models_path(self) -> Path:
        p = Path(self.MODELS_DIR)
        return p if p.is_absolute() else self.root_path / p

    @property
    def preprocessors_path(self) -> Path:
        p = Path(self.PREPROCESSORS_DIR)
        return p if p.is_absolute() else self.root_path / p


settings = Settings()
