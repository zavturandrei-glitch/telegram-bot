import os
import requests
import asyncio
import logging

from datetime import time

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


async def morning_weather(context: ContextTypes.DEFAULT_TYPE):

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q=Chisinau&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    )

    response = requests.get(url)
    data = response.json()

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]

    message = (
        f"🌤 Доброе утро!\n\n"
        f"Сейчас в Кишинёве:\n"
        f"🌡 Температура: {temp}°C\n"
        f"☁️ Погода: {description}"
    )

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):

    for user in update.message.new_chat_members:

        name = user.full_name

        await update.message.reply_text(
            f"👋 Добро пожаловать, {name}!\n\n"
            f"Рады видеть вас в группе 🙌\n"
            f"Здесь можно спокойно задавать вопросы по Кишинёву:\n"
            f"🏠 жильё\n"
            f"💼 работа\n"
            f"📄 документы\n"
            f"🚌 транспорт"
        )

        await asyncio.sleep(10)

        await update.message.reply_text(
            "🙏 Если вам сейчас нужна помощь или совет — "
            "можете написать прямо в группу."
        )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        welcome
    )
)

job_queue = app.job_queue

job_queue.run_daily(
    morning_weather,
    time=time(20, 13)
)

app.run_polling()