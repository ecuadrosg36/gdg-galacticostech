from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str
    mode: str
    ollama_model: str
    ollama_api_base: str
    google_api_key: str
    gemini_gemma_model: str
    database_url: str



settings = Settings()
