import asyncio
import aiohttp
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000/api/v1')

class NotificationService:
    def __init__(self, bot):
        self.bot = bot
        self.running = False
    
    async def start(self):
        """Запуск сервиса уведомлений"""
        self.running = True
        await self._notification_loop()
    
    async def stop(self):
        """Остановка сервиса уведомлений"""
        self.running = False
    
    async def _notification_loop(self):
        """Основной цикл отправки уведомлений"""
        while self.running:
            try:
                await self._check_and_send_notifications()
                # Проверяем каждые 5 минут
                await asyncio.sleep(300)
            except Exception as e:
                print(f"Ошибка в цикле уведомлений: {e}")
                await asyncio.sleep(60)
    
    async def _check_and_send_notifications(self):
        """Проверка и отправка уведомлений"""
        try:
            async with aiohttp.ClientSession() as session:
                # Получаем всех пользователей с активными уведомлениями
                # В реальном проекте здесь будет запрос к БД
                test_users = ["123456789", "987654321"]
                
                for user_id in test_users:
                    await self._send_scheduled_notifications(session, user_id)
                    await self._send_daily_motivation(session, user_id)
                    
        except Exception as e:
            print(f"Ошибка при проверке уведомлений: {e}")
    
    async def _send_scheduled_notifications(self, session: aiohttp.ClientSession, user_id: str):
        """Отправка запланированных уведомлений"""
        try:
            # Получаем настройки пользователя
            async with session.get(f'{BACKEND_URL}/notifications/settings?user_id={user_id}') as response:
                if response.status != 200:
                    return
                
                settings = await response.json()
                
                # Проверяем, нужно ли отправлять уведомления
                if not settings.get('lesson_reminders', True):
                    return
                
                # Получаем расписание пользователя
                async with session.get(f'{BACKEND_URL}/schedule?user_id={user_id}') as response:
                    if response.status != 200:
                        return
                    
                    schedule_data = await response.json()
                    lessons = schedule_data.get('schedule', [])
                    
                    # Проверяем ближайшие занятия
                    now = datetime.now()
                    for lesson in lessons:
                        # Парсим время занятия (упрощенная логика)
                        lesson_time = self._parse_lesson_time(lesson.get('time', ''))
                        if lesson_time:
                            time_diff = lesson_time - now
                            
                            # Отправляем уведомление за 1 час до занятия
                            if timedelta(hours=0, minutes=55) <= time_diff <= timedelta(hours=1, minutes=5):
                                await self._send_lesson_reminder(user_id, lesson)
                            
                            # Отправляем уведомление за 24 часа до занятия
                            elif timedelta(hours=23, minutes=55) <= time_diff <= timedelta(hours=24, minutes=5):
                                await self._send_lesson_reminder(user_id, lesson, is_advance=True)
                                
        except Exception as e:
            print(f"Ошибка при отправке запланированных уведомлений: {e}")
    
    async def _send_daily_motivation(self, session: aiohttp.ClientSession, user_id: str):
        """Отправка ежедневной мотивации"""
        try:
            # Получаем настройки пользователя
            async with session.get(f'{BACKEND_URL}/notifications/settings?user_id={user_id}') as response:
                if response.status != 200:
                    return
                
                settings = await response.json()
                
                if not settings.get('daily_motivation', True):
                    return
                
                # Проверяем время для отправки мотивации
                reminder_time = settings.get('reminder_time', '09:00')
                current_time = datetime.now().strftime('%H:%M')
                
                if current_time == reminder_time:
                    await self._send_motivation_message(user_id)
                    
        except Exception as e:
            print(f"Ошибка при отправке мотивации: {e}")
    
    def _parse_lesson_time(self, time_str: str) -> Optional[datetime]:
        """Парсинг времени занятия"""
        try:
            # Упрощенный парсинг для демонстрации
            # В реальном проекте здесь будет более сложная логика
            if "Понедельник" in time_str and "18:00" in time_str:
                # Вычисляем следующий понедельник
                now = datetime.now()
                days_ahead = 0 - now.weekday()  # 0 = понедельник
                if days_ahead <= 0:  # Понедельник уже прошел на этой неделе
                    days_ahead += 7
                next_monday = now + timedelta(days=days_ahead)
                return next_monday.replace(hour=18, minute=0, second=0, microsecond=0)
            
            elif "Вторник" in time_str and "19:00" in time_str:
                now = datetime.now()
                days_ahead = 1 - now.weekday()  # 1 = вторник
                if days_ahead <= 0:
                    days_ahead += 7
                next_tuesday = now + timedelta(days=days_ahead)
                return next_tuesday.replace(hour=19, minute=0, second=0, microsecond=0)
            
            elif "Среда" in time_str and "17:30" in time_str:
                now = datetime.now()
                days_ahead = 2 - now.weekday()  # 2 = среда
                if days_ahead <= 0:
                    days_ahead += 7
                next_wednesday = now + timedelta(days=days_ahead)
                return next_wednesday.replace(hour=17, minute=30, second=0, microsecond=0)
            
            return None
        except:
            return None
    
    async def _send_lesson_reminder(self, user_id: str, lesson: Dict, is_advance: bool = False):
        """Отправка напоминания о занятии"""
        try:
            title = "Напоминание о занятии"
            if is_advance:
                message = f"Завтра в {lesson.get('time', '').split(', ')[1]} у вас занятие '{lesson.get('title', '')}'"
            else:
                message = f"Через час у вас занятие '{lesson.get('title', '')}' в {lesson.get('location', '')}"
            
            # Отправляем уведомление через API
            async with aiohttp.ClientSession() as session:
                await session.post(f'{BACKEND_URL}/notifications/send', json={
                    'user_id': user_id,
                    'notification_type': 'lesson_reminder',
                    'title': title,
                    'message': message
                })
            
            # Отправляем сообщение в Telegram
            await self.bot.send_message(
                chat_id=user_id,
                text=f"🔔 {title}\n\n{message}"
            )
            
        except Exception as e:
            print(f"Ошибка при отправке напоминания о занятии: {e}")
    
    async def _send_motivation_message(self, user_id: str):
        """Отправка мотивационного сообщения"""
        try:
            motivation_messages = [
                "💪 Доброе утро! Готовы к новому дню изучения английского?",
                "🌟 Сегодня отличный день для изучения новых слов!",
                "📚 Не забывайте про ежедневную практику английского языка",
                "🎯 Маленькие шаги каждый день приводят к большим результатам!",
                "🔥 Ваш английский становится лучше с каждым днем!"
            ]
            
            import random
            message = random.choice(motivation_messages)
            
            # Отправляем уведомление через API
            async with aiohttp.ClientSession() as session:
                await session.post(f'{BACKEND_URL}/notifications/send', json={
                    'user_id': user_id,
                    'notification_type': 'daily_motivation',
                    'title': 'Ежедневная мотивация',
                    'message': message
                })
            
            # Отправляем сообщение в Telegram
            await self.bot.send_message(
                chat_id=user_id,
                text=f"💪 {message}"
            )
            
        except Exception as e:
            print(f"Ошибка при отправке мотивации: {e}")
    
    async def send_test_notification(self, user_id: str, test_name: str):
        """Отправка уведомления о новом тесте"""
        try:
            title = "Доступен новый тест"
            message = f"Пройдите тест '{test_name}' для получения баллов и проверки знаний"
            
            # Отправляем уведомление через API
            async with aiohttp.ClientSession() as session:
                await session.post(f'{BACKEND_URL}/notifications/send', json={
                    'user_id': user_id,
                    'notification_type': 'test_notification',
                    'title': title,
                    'message': message
                })
            
            # Отправляем сообщение в Telegram
            await self.bot.send_message(
                chat_id=user_id,
                text=f"📝 {title}\n\n{message}"
            )
            
        except Exception as e:
            print(f"Ошибка при отправке уведомления о тесте: {e}")
    
    async def send_club_reminder(self, user_id: str, club_name: str, club_time: str):
        """Отправка напоминания о клубе"""
        try:
            title = "Напоминание о клубе"
            message = f"Сегодня в {club_time} состоится встреча клуба '{club_name}'"
            
            # Отправляем уведомление через API
            async with aiohttp.ClientSession() as session:
                await session.post(f'{BACKEND_URL}/notifications/send', json={
                    'user_id': user_id,
                    'notification_type': 'club_reminder',
                    'title': title,
                    'message': message
                })
            
            # Отправляем сообщение в Telegram
            await self.bot.send_message(
                chat_id=user_id,
                text=f"👥 {title}\n\n{message}"
            )
            
        except Exception as e:
            print(f"Ошибка при отправке напоминания о клубе: {e}") 