import os
import asyncio
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")


async def send_second_message(bot, chat_id):
    logging.info("SECOND TASK STARTED")

    await asyncio.sleep(10)

    try:
        await bot.send_message(
            chat_id=chat_id,
            text="🙏 Если вам сейчас нужна помощь или совет — можете написать прямо в группу."
        )
        logging.info("SECOND MESSAGE SENT")

    except Exception as e:
        logging.error(f"SECOND MESSAGE ERROR: {e}")


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

        logging.info("SECOND TASK CREATED")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
)

app.run_polling()