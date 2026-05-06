import os
import asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")


async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):

    for user in update.message.new_chat_members:

        name = user.full_name
        chat_id = update.effective_chat.id

        # Первое сообщение
        await update.message.reply_text(
            f"👋 Добро пожаловать, {name}!\n\n"
            "Рады видеть вас в группе 🙌\n"
            "Здесь можно спокойно задавать вопросы по Кишинёву:\n"
            "🏠 жильё\n"
            "💼 работа\n"
            "📄 документы\n"
            "🚌 транспорт"
        )

        # Ждём 2 минуты
        await asyncio.sleep(120)

        # Второе сообщение
        await context.bot.send_message(
            chat_id=chat_id,
            text="🙏 Если вам сейчас нужна помощь или совет — можете написать прямо в группу."
        )


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome)
)

app.run_polling()