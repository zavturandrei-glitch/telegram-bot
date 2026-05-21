import os
import asyncio
import logging
import requests

from datetime import time
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

from traffic import traffic_command

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

CHAT_ID = -1003817168180
TIMEZONE = ZoneInfo("Europe/Chisinau")


def get_weather_text():
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q=Chisinau&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    )

    response = requests.get(url)
    data = response.json()

    temp = round(data["main"]["temp"], 1)
    description = data["weather"][0]["description"]

    return (
        "🌤 Доброе утро, Кишинёв!\n\n"
        f"🌡 Температура: {temp}°C\n"
        f"☁️ Сейчас: {description}\n\n"
        "Хорошего дня 🙌"
    )


async def morning_weather(context: ContextTypes.DEFAULT_TYPE):
    weather_text = get_weather_text()

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=weather_text
    )


async def send_second_message(bot, chat_id):
    await asyncio.sleep(10)

    await bot.send_message(
        chat_id=chat_id,
        text="🙏 Если вам сейчас нужна помощь или совет — можете написать прямо в группу."
    )


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        name = user.full_name
        chat_id = update.effective_chat.id

        await update.message.reply_text(
            f"👋 Добро пожаловать, {name}!\n\n"
            "Рады видеть вас в группе 🙌\n"
            "Здесь можно спокойно задавать вопросы по Кишинёву:\n"
            "🏠 жильё\n"
            "💼 работа\n"
            "📄 документы\n"
            "🚌 транспорт"
        )

        context.application.create_task(
            send_second_message(context.bot, chat_id)
        )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
)

app.add_handler(
    CommandHandler("traffic", traffic_command)
)

app.job_queue.run_daily(
    morning_weather,
    time=time(hour=8, minute=0, tzinfo=TIMEZONE)
)

app.run_polling()