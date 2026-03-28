from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Corporate Finance App"
    TARGET_TICKER: str = "MSFT"
    
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()