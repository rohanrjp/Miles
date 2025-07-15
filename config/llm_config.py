from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from .config import settings

gemini_model = GeminiModel(
    'gemini-2.5-flash', provider=GoogleGLAProvider(api_key=settings.GEMINI_API_KEY)
)
