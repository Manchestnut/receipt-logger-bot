from telegram.ext import ApplicationBuilder, MessageHandler, filters                               
import os
from fastapi import FastAPI, Request, Response
from telegram import Update
import asyncio
from contextlib import asynccontextmanager

import telegram_bot_api as tg

@asynccontextmanager
async def lifespan(app: FastAPI):
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    webhook_url = f"{render_url}/telegram-webhook"

    print(f"Setting up Telegram Webhook to target: {webhook_url}")
    await bot_app.bot.set_webhook(url=webhook_url, allowed_updates=Update.ALL_TYPES)

    async with bot_app:
        await bot_app.start()
        yield
        await bot_app.stop()

app = FastAPI(lifespan=lifespan)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot_app = ApplicationBuilder().token(TOKEN).build()

bot_app.add_handler(MessageHandler(filters.PHOTO, tg.handle_receipt_photo))

@app.post("/telegram-webhook")
async def process_telegram_update(request: Request):
    payload = await request.json()
    update = Update.de_json(payload, bot_app.bot)

    await bot_app.process_update(update)
    return Response(status_code=200)

@app.get("/")
def health_check():
    return {"status": "healthy", "pipeline": "Mendelluke Expense Bot is live! Lezzgoo!"}