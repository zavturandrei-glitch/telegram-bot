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
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

CHAT_ID = -1003817168180
TIMEZONE = ZoneInfo("Europe/Chisinau")


def get_weather_text():
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q=Chisinau&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    )

    response = requests.get(url, timeout=10)
    data = response.json()

    temp = round(data["main"]["temp"], 1)
    description = data["weather"][0]["description"]

    return (
        "🌤 Доброе утро, Кишинёв!\n\n"
        f"🌡 Температура: {temp}°C\n"
        f"☁️ Сейчас: {description}\n\n"
        "Хорошего дня 🙌"
    )


def get_traffic_text():
    lat = 47.0228
    lon = 28.8353

    url = (
        "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
        f"?point={lat},{lon}&key={TOMTOM_API_KEY}"
    )

    response = requests.get(url, timeout=10)
    data = response.json()

    print("TOMTOM STATUS:", response.status_code)
    print("TOMTOM DATA:", data)

    if "flowSegmentData" not in data:
        return (
            "🚗 Пробки в Кишинёве\n\n"
            "Сейчас не получилось получить данные TomTom.\n"
            "Проверяем настройку API 🙏"
        )

    flow = data["flowSegmentData"]

    current_speed = flow["currentSpeed"]
    free_flow_speed = flow["freeFlowSpeed"]

    if current_speed < free_flow_speed * 0.5:
        status = "🔴 Сильные пробки"
    elif current_speed < free_flow_speed * 0.8:
        status = "🟠 Движение замедлено"
    else:
        status = "🟢 Движение свободное"

    return (
        "🚗 Пробки в Кишинёве\n\n"
        f"Центр города: {status}\n"
        f"Скорость сейчас: {current_speed} км/ч\n"
        f"Обычно без пробок: {free_flow_speed} км/ч\n\n"
        "Берегите время и планируйте маршрут заранее 🙌"
    )


async def morning_weather(context: ContextTypes.DEFAULT_TYPE):
    weather_text = get_weather_text()

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=weather_text
    )


async def morning_traffic(context: ContextTypes.DEFAULT_TYPE):
    traffic_text = get_traffic_text()

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=traffic_text
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

app.job_queue.run_daily(
    morning_weather,
    time=time(hour=8, minute=0, tzinfo=TIMEZONE)
)

app.job_queue.run_once(
    morning_traffic,
    when=10
)

app.run_polling()