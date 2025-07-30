from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command
import asyncio
import os
import aiohttp
import json

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000/api/v1')

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Состояния пользователей (в реальном проекте используйте БД)
user_states = {}

def get_level_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Начальный уровень')],
            [KeyboardButton(text='Продвинутый уровень')]
        ],
        resize_keyboard=True
    )

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Открыть мини-приложение', web_app=WebAppInfo(url='https://your-webapp-url.com'))],
            [KeyboardButton(text='Связаться с куратором / преподавателем')],
            [KeyboardButton(text='Информация о курсах и школе')],
            [KeyboardButton(text='Изменить уровень обучения')]
        ],
        resize_keyboard=True
    )

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = {'level': None}
    
    await message.answer(
        'Добро пожаловать в школу английского языка! 🎓\n\n'
        'Выберите ваш уровень обучения:',
        reply_markup=get_level_keyboard()
    )

@dp.message(Command('help'))
async def cmd_help(message: types.Message):
    help_text = """
📚 Доступные команды:

/start — Начать работу с ботом
/help — Показать эту справку
/profile — Ваш профиль и прогресс
/schedule — Расписание занятий

🎯 Основные функции:
• Запись на занятия
• Просмотр расписания
• Мини-уроки и тесты
• Связь с преподавателем
• Участие в клубах
    """
    await message.answer(help_text)

@dp.message(Command('profile'))
async def cmd_profile(message: types.Message):
    user_id = message.from_user.id
    
    # Получаем профиль из backend
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{BACKEND_URL}/profile?user_id={user_id}') as response:
                if response.status == 200:
                    profile = await response.json()
                    profile_text = f"""
👤 Ваш профиль:

📊 Уровень: {profile.get('level', 'Не выбран')}
📈 Прогресс: {profile.get('progress', 0)}%
📚 Завершено уроков: {profile.get('lessons_completed', 0)}
🏆 Баллы: {profile.get('points', 0)}
    """
                else:
                    profile_text = "❌ Не удалось загрузить профиль"
    except:
        profile_text = "❌ Ошибка соединения с сервером"
    
    await message.answer(profile_text)

@dp.message(Command('schedule'))
async def cmd_schedule(message: types.Message):
    user_id = message.from_user.id
    user_state = user_states.get(user_id, {})
    level = user_state.get('level', 'all')
    
    # Получаем расписание из backend
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{BACKEND_URL}/schedule?level={level}&user_id={user_id}') as response:
                if response.status == 200:
                    schedule_data = await response.json()
                    schedule = schedule_data.get('schedule', [])
                    
                    if schedule:
                        schedule_text = "📅 Расписание занятий:\n\n"
                        for lesson in schedule:
                            schedule_text += f"🕐 {lesson.get('time', 'N/A')}\n"
                            schedule_text += f"📚 {lesson.get('title', 'N/A')}\n"
                            schedule_text += f"👨‍🏫 {lesson.get('teacher', 'N/A')}\n"
                            schedule_text += f"📍 {lesson.get('location', 'N/A')}\n\n"
                    else:
                        schedule_text = "📅 Расписание пока пусто"
                else:
                    schedule_text = "❌ Не удалось загрузить расписание"
    except:
        schedule_text = "❌ Ошибка соединения с сервером"
    
    await message.answer(schedule_text)

@dp.message(lambda message: message.text == 'Начальный уровень')
async def handle_beginner_level(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = {'level': 'beginner'}
    
    await message.answer(
        '✅ Выбран начальный уровень обучения!\n\n'
        'Теперь вы можете:\n'
        '• Записываться на занятия\n'
        '• Проходить мини-уроки\n'
        '• Участвовать в клубах\n'
        '• Отслеживать прогресс',
        reply_markup=get_main_keyboard()
    )

@dp.message(lambda message: message.text == 'Продвинутый уровень')
async def handle_advanced_level(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = {'level': 'advanced'}
    
    await message.answer(
        '✅ Выбран продвинутый уровень обучения!\n\n'
        'Теперь вы можете:\n'
        '• Записываться на занятия\n'
        '• Проходить мини-уроки\n'
        '• Участвовать в клубах\n'
        '• Отслеживать прогресс',
        reply_markup=get_main_keyboard()
    )

@dp.message(lambda message: message.text == 'Открыть мини-приложение')
async def handle_open_webapp(message: types.Message):
    await message.answer(
        '🌐 Открываю мини-приложение...\n\n'
        'В мини-приложении вы сможете:\n'
        '• Просматривать расписание\n'
        '• Бронировать уроки\n'
        '• Проходить тесты\n'
        '• Участвовать в клубах\n'
        '• Отслеживать прогресс'
    )

@dp.message(lambda message: message.text == 'Связаться с куратором / преподавателем')
async def handle_contact_teacher(message: types.Message):
    await message.answer(
        '👨‍🏫 Связь с преподавателем:\n\n'
        '📧 Email: teacher@englishschool.com\n'
        '📱 Telegram: @english_teacher\n'
        '📞 Телефон: +7 (999) 123-45-67\n\n'
        '⏰ Время работы: Пн-Пт 9:00-18:00'
    )

@dp.message(lambda message: message.text == 'Информация о курсах и школе')
async def handle_course_info(message: types.Message):
    info_text = """
🏫 О нашей школе английского языка:

📚 Наши курсы:
• Начальный уровень (A1-A2)
• Продвинутый уровень (B1-C1)
• Разговорные клубы
• Подготовка к экзаменам

🎯 Преимущества:
• Опытные преподаватели
• Индивидуальный подход
• Современные методики
• Удобное расписание

💰 Стоимость:
• Групповые занятия: от 2000₽/мес
• Индивидуальные: от 1500₽/занятие
• Клубы: от 500₽/месяц

📍 Адрес: ул. Примерная, 123
    """
    await message.answer(info_text)

@dp.message(lambda message: message.text == 'Изменить уровень обучения')
async def handle_change_level(message: types.Message):
    await message.answer(
        'Выберите новый уровень обучения:',
        reply_markup=get_level_keyboard()
    )

@dp.message()
async def handle_unknown(message: types.Message):
    await message.answer(
        '❓ Не понимаю эту команду.\n'
        'Используйте /help для просмотра доступных команд.'
    )

async def main():
    print("🤖 Telegram bot starting...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
