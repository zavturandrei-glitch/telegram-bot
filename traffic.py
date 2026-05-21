import os
import requests

from telegram.ext import ContextTypes


TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

CHAT_ID = -1003817168180


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
        status = "🔴 Сильные пробки"
    elif current_speed < free_flow_speed * 0.8:
        status = "🟠 Движение замедлено"
    else:
        status = "🟢 Движение свободное"

    return (
        "🚗 Пробки в Кишинёве\n\n"
        f"Центр города: {status}\n"
        f"Средняя скорость: {current_speed} км/ч\n\n"
        "Берегите время и планируйте маршрут заранее 🙌"
    )


async def morning_traffic(context: ContextTypes.DEFAULT_TYPE):
    text = get_traffic_text()

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=text
    )