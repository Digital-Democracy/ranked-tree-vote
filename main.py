from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

from handlers import start, logout, create, delete, menu

import os
from dotenv_vault import load_dotenv

from utils import i18n

load_dotenv()


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()

    if query.data == "create":
        await create(update, context)
    elif query.data == "delete":
        await delete(update, context)
    elif query.data == "logout":
        await logout(update, context)
    elif query.data == "info":
        await info(update, context)


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    formatted_text = i18n(update.effective_user.language_code)("info")
    await update.effective_message.reply_chat_action("upload_video")
    await update.effective_user.send_video(
        video="media/info.mp4",
        width=1920,
        height=1080,
        caption=formatted_text,
        parse_mode="Markdown"
    )


def main() -> None:
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(callback))

    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("logout", logout))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
