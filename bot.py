import os
import asyncio
import logging
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
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


async def morning_post_loop(application):
    while True:
        now = datetime.now(TIMEZONE)
        target = datetime.combine(now.date(), time(8, 30), tzinfo=TIMEZONE)

        if now >= target:
            target = target + timedelta(days=1)

        seconds_until_post = (target - now).total_seconds()

        logging.info(f"Next morning post in {seconds_until_post} seconds")

        await asyncio.sleep(seconds_until_post)

        await application.bot.send_message(
            chat_id=CHAT_ID,
            text=(
                "☀️ Доброе утро!\n\n"
                "Кто сегодня ищет жильё, работу или помощь с документами — "
                "пишите в группу. Возможно, кто-то уже сталкивался с таким вопросом и подскажет."
            )
        )


async def on_startup(application):
    application.create_task(morning_post_loop(application))


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