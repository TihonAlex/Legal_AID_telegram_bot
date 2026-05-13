import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")
ADMIN_IDS = [379327403,7659324331]  # сюда вставь свой Telegram user_id

NAME, PHONE, REQUEST = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💼 Вас приветствует Консультант бот.\n\n"
        "Как вас зовут?"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    keyboard = [[KeyboardButton("Отправить мой номер", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "✍️ Опишите вашу ситуацию:",
        reply_markup=reply_markup
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text

    context.user_data["phone"] = phone

    await update.message.reply_text(
        "👩‍💻 Я посоветуюсь со старшими товарищами и обязательно вам отвечу в течение дня на ваш ТГ аккаунт. Держитесь!"
    )
    return REQUEST


async def get_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["request"] = update.message.text

    name = context.user_data["name"]
    phone = context.user_data["phone"]
    request = context.user_data["request"]

    username = update.effective_user.username
    user_id = update.effective_user.id

    admin_text = (
        "📩 Новая заявка\n\n"
        f"🙋 Имя: {name}\n"
        f"🙇 Описание ситуации: {phone}\n"
        f"📝 Последний комментарий: {request}\n\n"
        f"Telegram: @{username if username else 'нет username'}\n"
        f"User ID: {user_id}"
    )

    for admin_id in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=admin_id,
            text=admin_text
        )
        

    await update.message.reply_text(
        "Спасибо, вам 🤝"
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Заявка отменена.")
    return ConversationHandler.END

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ваш ID: {update.effective_user.id}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()


    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [
                MessageHandler(filters.CONTACT | filters.TEXT, get_phone)
            ],
            REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_request)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conversation)
    
    app.add_handler(CommandHandler("myid", myid))

    app.run_polling()


if __name__ == "__main__":
    main()