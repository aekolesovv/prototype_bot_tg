from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command
import asyncio
import os
import aiohttp
import json
from dotenv import load_dotenv
from .notification_service import NotificationService
from db.repositories import UserRepository

# Загружаем переменные из .env файла
load_dotenv()

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
            [KeyboardButton(text='Открыть мини-приложение', web_app=WebAppInfo(url='http://localhost:3000'))],
            [KeyboardButton(text='Связаться с куратором / преподавателем')],
            [KeyboardButton(text='Информация о курсах и школе')],
            [KeyboardButton(text='Изменить уровень обучения')],
            [KeyboardButton(text='🔔 Уведомления')]
        ],
        resize_keyboard=True
    )

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = {'level': None}
    
    # Создаем или получаем пользователя из БД
    user = UserRepository.get_by_telegram_id(str(user_id))
    if not user:
        user = UserRepository.create_user(
            str(user_id),
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )
    
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

@dp.message(Command('notifications'))
async def cmd_notifications(message: types.Message):
    user_id = message.from_user.id
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{BACKEND_URL}/notifications?user_id={user_id}') as response:
                if response.status == 200:
                    data = await response.json()
                    notifications = data.get('notifications', [])
                    unread_count = data.get('unread_count', 0)
                    
                    if not notifications:
                        await message.answer("🔔 У вас пока нет уведомлений")
                        return
                    
                    # Показываем последние 5 уведомлений
                    recent_notifications = notifications[:5]
                    notification_text = f"🔔 Ваши уведомления ({unread_count} непрочитанных):\n\n"
                    
                    for notification in recent_notifications:
                        status = "🔴" if not notification["is_read"] else "⚪"
                        notification_text += f"{status} {notification['title']}\n"
                        notification_text += f"   {notification['message']}\n\n"
                    
                    if len(notifications) > 5:
                        notification_text += f"... и еще {len(notifications) - 5} уведомлений"
                    
                    # Создаем inline кнопки для управления уведомлениями
                    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                        [types.InlineKeyboardButton(text="📋 Все уведомления", callback_data="all_notifications")],
                        [types.InlineKeyboardButton(text="✅ Отметить все прочитанными", callback_data="mark_all_read")],
                        [types.InlineKeyboardButton(text="⚙️ Настройки уведомлений", callback_data="notification_settings")]
                    ])
                    
                    await message.answer(notification_text, reply_markup=keyboard)
                else:
                    await message.answer("❌ Не удалось загрузить уведомления")
    except:
        await message.answer("❌ Ошибка соединения с сервером")

@dp.message(lambda message: message.text == 'Начальный уровень')
async def handle_beginner_level(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = {'level': 'beginner'}
    
    # Обновляем уровень в БД
    user = UserRepository.get_by_telegram_id(str(user_id))
    if user:
        UserRepository.update_user_level(user.id, 'beginner')
    
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
    
    # Обновляем уровень в БД
    user = UserRepository.get_by_telegram_id(str(user_id))
    if user:
        UserRepository.update_user_level(user.id, 'advanced')
    
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

@dp.message(lambda message: message.text == '🔔 Уведомления')
async def handle_notifications_button(message: types.Message):
    await cmd_notifications(message)

@dp.callback_query(lambda c: c.data == "all_notifications")
async def show_all_notifications(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{BACKEND_URL}/notifications?user_id={user_id}') as response:
                if response.status == 200:
                    data = await response.json()
                    notifications = data.get('notifications', [])
                    
                    if not notifications:
                        await callback_query.message.edit_text("🔔 У вас пока нет уведомлений")
                        return
                    
                    notification_text = "🔔 Все ваши уведомления:\n\n"
                    
                    for i, notification in enumerate(notifications, 1):
                        status = "🔴" if not notification["is_read"] else "⚪"
                        date = notification["created_at"][:10] if notification["created_at"] else ""
                        notification_text += f"{i}. {status} {notification['title']}\n"
                        notification_text += f"   {notification['message']}\n"
                        notification_text += f"   📅 {date}\n\n"
                    
                    await callback_query.message.edit_text(notification_text)
                else:
                    await callback_query.answer("❌ Не удалось загрузить уведомления")
    except:
        await callback_query.answer("❌ Ошибка соединения с сервером")

@dp.callback_query(lambda c: c.data == "mark_all_read")
async def mark_all_notifications_read(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{BACKEND_URL}/notifications/read-all?user_id={user_id}') as response:
                if response.status == 200:
                    await callback_query.answer("✅ Все уведомления отмечены как прочитанные")
                    await callback_query.message.edit_text("✅ Все уведомления отмечены как прочитанные")
                else:
                    await callback_query.answer("❌ Не удалось обновить уведомления")
    except:
        await callback_query.answer("❌ Ошибка соединения с сервером")

@dp.callback_query(lambda c: c.data == "notification_settings")
async def show_notification_settings(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{BACKEND_URL}/notifications/settings?user_id={user_id}') as response:
                if response.status == 200:
                    settings = await response.json()
                    
                    settings_text = "⚙️ Настройки уведомлений:\n\n"
                    settings_text += f"📚 Напоминания о занятиях: {'✅' if settings['lesson_reminders'] else '❌'}\n"
                    settings_text += f"📝 Уведомления о тестах: {'✅' if settings['test_notifications'] else '❌'}\n"
                    settings_text += f"👥 Напоминания о клубах: {'✅' if settings['club_reminders'] else '❌'}\n"
                    settings_text += f"💪 Ежедневная мотивация: {'✅' if settings['daily_motivation'] else '❌'}\n"
                    settings_text += f"⏰ Время напоминаний: {settings['reminder_time']}\n"
                    
                    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                        [types.InlineKeyboardButton(text="🔧 Изменить настройки", callback_data="edit_notification_settings")]
                    ])
                    
                    await callback_query.message.edit_text(settings_text, reply_markup=keyboard)
                else:
                    await callback_query.answer("❌ Не удалось загрузить настройки")
    except:
        await callback_query.answer("❌ Ошибка соединения с сервером")

@dp.callback_query(lambda c: c.data == "edit_notification_settings")
async def edit_notification_settings(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    
    # Создаем inline кнопки для переключения настроек
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📚 Напоминания о занятиях", callback_data="toggle_lesson_reminders")],
        [types.InlineKeyboardButton(text="📝 Уведомления о тестах", callback_data="toggle_test_notifications")],
        [types.InlineKeyboardButton(text="👥 Напоминания о клубах", callback_data="toggle_club_reminders")],
        [types.InlineKeyboardButton(text="💪 Ежедневная мотивация", callback_data="toggle_daily_motivation")],
        [types.InlineKeyboardButton(text="⏰ Изменить время", callback_data="change_reminder_time")]
    ])
    
    await callback_query.message.edit_text(
        "🔧 Выберите настройку для изменения:",
        reply_markup=keyboard
    )

@dp.message()
async def handle_unknown(message: types.Message):
    await message.answer(
        '❓ Не понимаю эту команду.\n'
        'Используйте /help для просмотра доступных команд.'
    )

async def main():
    # Запускаем сервис уведомлений
    notification_service = NotificationService(bot)
    
    try:
        # Запускаем сервис уведомлений в фоне
        notification_task = asyncio.create_task(notification_service.start())
        
        # Запускаем бота с явным указанием параметров
        print("🤖 Бот запущен и готов к работе!")
        await dp.start_polling(bot, skip_updates=True)
    except KeyboardInterrupt:
        print("Остановка бота...")
    finally:
        # Останавливаем сервис уведомлений
        await notification_service.stop()
        if 'notification_task' in locals():
            notification_task.cancel()

if __name__ == '__main__':
    asyncio.run(main())
