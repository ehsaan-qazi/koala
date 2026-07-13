"""
Koala backend configuration.
Loads settings from environment variables / .env file.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Supabase ──────────────────────────────────────────────
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_jwt_secret: str = ""  # For local JWT verification

    # ── Database ──────────────────────────────────────────────
    database_url: str = "postgresql+psycopg://koala:koala@localhost:5432/koala"

    # ── App ───────────────────────────────────────────────────
    app_secret_key: str = "koala-dev-secret-change-in-prod"
    debug: bool = True

    # ── LemonSqueezy (Billing) ────────────────────────────────
    lemonsqueezy_api_key: str = ""
    lemonsqueezy_webhook_secret: str = ""
    lemonsqueezy_store_id: str = ""
    lemonsqueezy_variant_id: str = ""

    # ── AI (Phase 2+) ────────────────────────────────────────
    llm_api_key: str = ""
    llm_provider: str = "gemini"

    # ── Tier Limits ──────────────────────────────────────────
    free_upload_limit: int = 3
    pro_upload_limit: int = 20
    free_max_file_size_mb: int = 10
    pro_max_file_size_mb: int = 25

    # ── CORS ─────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    model_config = {
        "env_file": "../.env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
