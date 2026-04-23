from functools import lru_cache
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "HMS API"
    database_url: str = "sqlite:///./hms.db"
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 60
    # Optional first-run admin
    admin_seed_email: str | None = None
    admin_seed_password: str | None = None
    # Comma list or * for all
    cors_origins: Union[str, List[str]] = "*"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: object) -> Union[str, List[str]]:
        if v is None or v == "":
            return "*"
        if isinstance(v, str) and v != "*":
            return [x.strip() for x in v.split(",") if x.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
