from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import asyncio
import os

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
bot = Bot(token=TOKEN)
dp = Dispatcher()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Открыть мини-приложение')],
        [KeyboardButton(text='Связаться с куратором / преподавателем')],
        [KeyboardButton(text='Информация о курсах и школе')]
    ],
    resize_keyboard=True
)

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(
        'Добро пожаловать в школу английского языка!\nВыберите уровень обучения:',
        reply_markup=main_kb
    )

@dp.message(Command('help'))
async def cmd_help(message: types.Message):
    await message.answer('Доступные команды:\n/start — начать\n/help — помощь\n/profile — профиль\n/schedule — расписание')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
