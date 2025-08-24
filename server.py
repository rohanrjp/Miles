from fastapi import FastAPI
from pydantic import BaseModel
import httpx
from config.config import settings
from graph import run_graph
from models.domain import User

BOT_TOKEN = settings.BOT_TOKEN
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = FastAPI()

class TelegramUpdate(BaseModel):
    update_id: int
    message: dict

@app.post("/webhook")
async def telegram_webhook(update: TelegramUpdate):
    message = update.message
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    # TODO: Replace with a real user object
    user = User(name="Rohan Paul", email="rohan1007rjp@gmail.com", interests=["running", "coding"],home_city="Chennai")

    result = await run_graph(text, user)

    # Send result back to Telegram
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": result}
        )

    return {"ok": True}