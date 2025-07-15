from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN:str
    TELEGRAM_CHAT_ID:str
    GEMINI_API_KEY:str
    
    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
settings=Settings()    