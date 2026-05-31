from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite:///./penny_hunt.db"
    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    FRONTEND_URL: str = ""
    BACKEND_URL: str = ""
    TARGET_ZIP: str = "78542"
    RADIUS_MILES: float = 30.0
    SCRAPE_INTERVAL_SECONDS: int = 120
    SCORE_BROADCAST_THRESHOLD: float = 80.0

    DG_SCRAPE_BASE: str = ""
    HD_SCRAPE_BASE: str = ""
    WALMART_SCRAPE_BASE: str = ""
    HEB_SCRAPE_BASE: str = ""
    SCRAPE_MAX_PAGES: int = 3
    SCRAPE_CONCURRENCY: int = 4

    ENABLE_LLM_SCORING: bool = False
    ANTHROPIC_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    VISION_DAILY_COST_LIMIT_USD: float = 1.00

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalize_db_url(cls, v):
        if not v:  # blank env on Railway/local -> safe dev default
            return "sqlite:///./penny_hunt.db"
        if v.startswith("postgres://"):  # Railway sometimes uses the legacy scheme
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @property
    def origins(self) -> list[str]:
        o = [x.strip() for x in self.ALLOWED_ORIGINS.split(",") if x.strip()]
        if self.FRONTEND_URL:
            o.append(self.FRONTEND_URL.rstrip("/"))
        return o


settings = Settings()
