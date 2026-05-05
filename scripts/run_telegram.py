import os
import sys

# إضافة المجلد الرئيسي للمسار عشان بايثون يشوف المجلدات
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.telegram.bot import build_telegram_app

if __name__ == "__main__":
    app = build_telegram_app()
    print("Telegram bot is running with polling...")
    app.run_polling()
