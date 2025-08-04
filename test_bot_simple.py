#!/usr/bin/env python3
"""
Простой тест бота
"""

import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Загружаем переменные из .env файла
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Это тестовый бот. Работает! ✅")

@dp.message(Command('test'))
async def cmd_test(message: types.Message):
    await message.answer("Тест прошел успешно! 🎉")

async def main():
    print(f"🤖 Запуск тестового бота...")
    print(f"📝 Токен: {TOKEN[:10]}...")
    
    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    asyncio.run(main()) 