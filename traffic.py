import os
import requests

from telegram import Update
from telegram.ext import ContextTypes


TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")


def get_traffic_text():
    lat = 47.0105
    lon = 28.8638

    url = (
        "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
        f"?point={lat},{lon}&key={TOMTOM_API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    flow = data["flowSegmentData"]

    current_speed = flow["currentSpeed"]
    free_flow_speed = flow["freeFlowSpeed"]

    if current_speed < free_flow_speed * 0.5:
        status = "🔴 сильная загруженность"
    elif current_speed < free_flow_speed * 0.8:
        status = "🟠 движение замедлено"
    else:
        status = "🟢 движение свободное"

    return (
        "🚗 Трафик в Кишинёве\n\n"
        f"Центр города: {status}\n"
        f"Скорость сейчас: {current_speed} км/ч\n"
        f"Обычно без пробок: {free_flow_speed} км/ч\n\n"
        "Тестируем новую функцию 🙏"
    )


async def traffic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_traffic_text()
    await update.message.reply_text(text)