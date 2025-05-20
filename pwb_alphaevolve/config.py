"""Centralised runtime configuration using Pydantic BaseSettings.

Environment variables (defaults in brackets):

OPENAI_API_KEY    – Required for evolution step (no default)
OPENAI_MODEL      – Chat model name ["o3-mini"]
MAX_TOKENS        – Token cap for LLM replies [4096]

SQLITE_DB         – Path to SQLite file ["~/.pwb_alphaevolve/programs.db"]
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration pulled from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)
    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("o3-mini", env="OPENAI_MODEL")
    max_tokens: int = Field(4096, env="MAX_TOKENS")

    # Storage
    sqlite_db: str = Field("~/.pwb_alphaevolve/programs.db", env="SQLITE_DB")

    # Data
    default_symbols_raw: str = Field("SPY,EFA,IEF,VNQ,GSG", env="DEFAULT_SYMBOLS")
    start_date: str = Field("1990-01-01", env="START_DATE")

    hof_metric: str = Field("calmar", env="HOF_METRIC")

    @property
    def default_symbols(self) -> tuple[str, ...]:
        """Always returns a tuple of upper-case tickers."""
        return tuple(s.strip().upper() for s in self.default_symbols_raw.split(",") if s.strip())


settings = Settings()
