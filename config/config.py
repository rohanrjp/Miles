from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    BOT_TOKEN:str
    TELEGRAM_CHAT_ID:str
    GEMINI_API_KEY:str
    STRAVA_CLIENT_ID:str
    STRAVA_CLIENT_SECRET:str
    STRAVA_ACESS_TOKEN:str
    STRAVA_REFRESH_TOKEN:str
    NEON_DB_STRING:str
    GOOGLE_CLIENT_ID:str
    GOOGLE_CLIENT_SECRET:str
    
    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
settings=Settings()    