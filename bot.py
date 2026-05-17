import os
import requests
import asyncio
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

CHAT_ID = -1003817168180


async def send_weather(bot):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q=Chisinau&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    )

    response = requests.get(url)
    data = response.json()

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]

    text = (
        f"🌤 Погода в Кишинёве\n\n"
        f"🌡 Температура: {temp}°C\n"
        f"☁️ Сейчас: {description}"
    )

    await bot.send_message(chat_id=CHAT_ID, text=text)


async def startup_test(app):
    await asyncio.sleep(20)
    await send_weather(app.bot)


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        name = user.full_name

        await update.message.reply_text(
            f"👋 Добро пожаловать, {name}!\n\n"
            "Рады видеть вас в группе 🙌"
        )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
)

app.post_init = startup_test

app.run_polling()