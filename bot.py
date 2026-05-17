import os
import asyncio
import logging
import requests

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

CHAT_ID = -1003817168180

TIMEZONE = ZoneInfo("Europe/Chisinau")


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


def get_weather():
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q=Chisinau&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    )

    response = requests.get(url)
    data = response.json()

    temp = round(data["main"]["temp"])
    description = data["weather"][0]["description"]

    return (
        f"🌦 Доброе утро, Кишинёв!\n\n"
        f"Сейчас: {temp}°C\n"
        f"Погода: {description}\n\n"
        f"Хорошего дня 🙌"
    )


async def morning_post_loop(application):
    while True:
        now = datetime.now(TIMEZONE)

        target = datetime.combine(
            now.date(),
            time(8, 30),
            tzinfo=TIMEZONE
        )

        if now >= target:
            target += timedelta(days=1)

        seconds_until_post = (target - now).total_seconds()

        logging.info(f"Next weather post in {seconds_until_post} seconds")

        await asyncio.sleep(seconds_until_post)

        weather_text = get_weather()

        await application.bot.send_message(
            chat_id=CHAT_ID,
            text=weather_text
        )


async def on_startup(application):
    application.create_task(
        morning_post_loop(application)
    )


app = (
    ApplicationBuilder()
    .token(TOKEN)
    .post_init(on_startup)
    .build()
)

app.add_handler(
    MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
)

app.run_polling()