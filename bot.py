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
GOOGLE_ROUTES_API_KEY = os.getenv("GOOGLE_ROUTES_API_KEY")

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
        "🌤 Погода в Кишинёве\n\n"
        f"🌡 Температура: {temp}°C\n"
        f"☁️ Сейчас: {description}"
    )


def get_route_duration(origin_lat, origin_lon, dest_lat, dest_lon):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_ROUTES_API_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.staticDuration",
    }

    body = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": origin_lat,
                    "longitude": origin_lon,
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": dest_lat,
                    "longitude": dest_lon,
                }
            }
        },
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
    }

    response = requests.post(url, headers=headers, json=body, timeout=15)

    print("GOOGLE ROUTES STATUS:", response.status_code)
    print("GOOGLE ROUTES TEXT:", response.text)

    data = response.json()

    if "routes" not in data or not data["routes"]:
        return None

    route = data["routes"][0]

    duration_text = route.get("duration", "0s")
    static_duration_text = route.get("staticDuration", "0s")

    duration_seconds = int(duration_text.replace("s", ""))
    static_duration_seconds = int(static_duration_text.replace("s", ""))

    return duration_seconds, static_duration_seconds


def seconds_to_minutes(seconds):
    return round(seconds / 60)


def get_traffic_text():
    routes = [
        {
            "name": "Ботаника → Центр",
            "origin": (46.9885, 28.8572),
            "destination": (47.0245, 28.8323),
        },
        {
            "name": "Рышкановка → Центр",
            "origin": (47.0604, 28.8721),
            "destination": (47.0245, 28.8323),
        },
        {
            "name": "Буюканы → Центр",
            "origin": (47.0386, 28.7803),
            "destination": (47.0245, 28.8323),
        },
    ]

    lines = []

    for route in routes:
        result = get_route_duration(
            route["origin"][0],
            route["origin"][1],
            route["destination"][0],
            route["destination"][1],
        )

        if result is None:
            lines.append(f"⚠️ {route['name']}: данных пока нет")
            continue

        duration_seconds, static_duration_seconds = result

        delay_seconds = duration_seconds - static_duration_seconds

        duration_min = seconds_to_minutes(duration_seconds)
        delay_min = seconds_to_minutes(delay_seconds)

        if delay_min >= 15:
            status = "🔴 сильная пробка"
        elif delay_min >= 7:
            status = "🟠 движение замедлено"
        else:
            status = "🟢 нормально"

        lines.append(
            f"{status}\n"
            f"{route['name']}: примерно {duration_min} мин"
        )

        if delay_min > 0:
            lines.append(f"Задержка из-за трафика: +{delay_min} мин")

        lines.append("")

    return (
        "🚗 Пробки в Кишинёве\n\n"
        + "\n".join(lines)
        + "Планируйте маршрут заранее 🙌"
    )


async def weather_and_traffic_post(context: ContextTypes.DEFAULT_TYPE):
    weather_text = get_weather_text()
    traffic_text = get_traffic_text()

    full_text = (
        f"{weather_text}\n\n"
        "────────────\n\n"
        f"{traffic_text}"
    )

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=full_text
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
    weather_and_traffic_post,
    time=time(hour=8, minute=0, tzinfo=TIMEZONE)
)

app.job_queue.run_daily(
    weather_and_traffic_post,
    time=time(hour=12, minute=0, tzinfo=TIMEZONE)
)

app.job_queue.run_daily(
    weather_and_traffic_post,
    time=time(hour=17, minute=0, tzinfo=TIMEZONE)
)

app.run_polling()