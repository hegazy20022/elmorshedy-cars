from telegram.ext import Application, MessageHandler, CommandHandler, filters
from app.core.config import settings
from agents.telegram.handlers.message_handler import handle_message


def build_telegram_app() -> Application:
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).read_timeout(30).connect_timeout(30).build()
    app.add_handler(CommandHandler("start", handle_message))
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE, handle_message))
    return app
