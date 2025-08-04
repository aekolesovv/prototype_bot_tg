#!/usr/bin/env python3
"""
Скрипт для запуска Telegram-бота
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from bot.bot import main

# Загружаем переменные из .env файла
load_dotenv()

def check_environment():
    """Проверка окружения"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token or token == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Ошибка: Не установлен TELEGRAM_BOT_TOKEN")
        print("Установите переменную окружения или замените в bot/bot.py")
        return False
    
    print("✅ TELEGRAM_BOT_TOKEN установлен")
    return True

def main_wrapper():
    """Обертка для запуска бота"""
    print("🤖 Запуск Telegram-бота для школы английского языка...")
    
    if not check_environment():
        sys.exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main_wrapper() 