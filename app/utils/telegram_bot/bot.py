from dotenv import load_dotenv
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from app import Config
from app.utils.telegram_bot.handlers import (
    start, show_menu, process_login, process_add_article, process_add_photosession,
    process_add_service, process_category_selection, handle_message
)


telegram_token = Config.TELEGRAM_BOT_TOKEN

def main() -> None:
    """
    Основная функция для запуска бота.
    """
    application = ApplicationBuilder().token(telegram_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^Меню$"), show_menu))
    application.add_handler(CallbackQueryHandler(process_login, pattern='login'))
    application.add_handler(CallbackQueryHandler(process_add_article, pattern='add_article'))
    application.add_handler(CallbackQueryHandler(process_add_photosession, pattern='add_photosession'))
    application.add_handler(CallbackQueryHandler(process_add_service, pattern='add_service'))
    application.add_handler(CallbackQueryHandler(process_category_selection, pattern='^category_'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()

