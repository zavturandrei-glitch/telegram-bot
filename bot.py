async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        name = user.full_name
        chat_id = update.effective_chat.id

        await update.message.reply_text(
            f"👋 Добро пожаловать, {name}!\n\n"
            "Рады видеть вас в группе 🙌\n"
            "Здесь можно спокойно задавать вопросы по Кишинёву:\n"
            "🏠 жильё\n💼 работа\n📄 документы\n🚌 транспорт"
        )

        await asyncio.sleep(120)

        await context.bot.send_message(
            chat_id=chat_id,
            text="🙏 Если вам сейчас нужна помощь или совет — можете написать прямо в группу."
        )