from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/image_relevance"

    gemini_api_key: str = ""
    vision_model: str = "gemini-3.6-flash"
    embedding_model: str = "gemini-embedding-001"

    vision_confidence_threshold: float = 0.70
    similarity_threshold: float = 0.70
    ai_budget_usd: float = 0.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
