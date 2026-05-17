import os
import asyncio
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

CHAT_ID = -1003817168180


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


async def test_autopost(bot):
    await asyncio.sleep(60)

    await bot.send_message(
        chat_id=CHAT_ID,
        text="✅ Тест автопостинга работает. Бот сам написал сообщение в группу."
    )


async def post_init(application):
    application.create_task(
        test_autopost(application.bot)
    )


app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

app.add_handler(
    MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
)

app.run_polling()