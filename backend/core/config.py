"""Application settings loaded from environment / .env file."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Nugen API
    nugen_api_key: str = ""
    nugen_base_url: str = "https://api.nugen.in/inference"
    nugen_aligned_model_id: str = ""
    nugen_embed_model: str = "nugen-flash-embed"
    # Fallback flag: when the aligned model is not ready, force the generic
    # model instead of matching on a stale/blank aligned id.
    nugen_use_aligned: bool = True

    # Google Earth Engine
    gee_service_account: str = ""
    gee_key_file: str = "backend/gee-key.json"
    gee_key_json: str = ""  # production: full service-account JSON as a string

    # NASA FIRMS
    firms_map_key: str = ""

    # Supabase (all environments — no SQLite)
    database_url: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # App
    frontend_url: str = "http://localhost:3000"
    allowed_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()