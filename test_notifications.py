#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы уведомлений
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Конфигурация
BACKEND_URL = "http://localhost:8000/api/v1"
TEST_USER_ID = "123456789"

async def test_notifications():
    """Тестирование системы уведомлений"""
    print("🧪 Тестирование системы уведомлений...")
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Тест получения уведомлений
        print("\n1. Получение уведомлений пользователя...")
        try:
            async with session.get(f"{BACKEND_URL}/notifications?user_id={TEST_USER_ID}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Уведомления загружены: {len(data.get('notifications', []))} шт.")
                    print(f"   Непрочитанных: {data.get('unread_count', 0)}")
                else:
                    print(f"❌ Ошибка получения уведомлений: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        # 2. Тест получения настроек уведомлений
        print("\n2. Получение настроек уведомлений...")
        try:
            async with session.get(f"{BACKEND_URL}/notifications/settings?user_id={TEST_USER_ID}") as response:
                if response.status == 200:
                    settings = await response.json()
                    print("✅ Настройки загружены:")
                    for key, value in settings.items():
                        print(f"   {key}: {value}")
                else:
                    print(f"❌ Ошибка получения настроек: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        # 3. Тест отправки нового уведомления
        print("\n3. Отправка тестового уведомления...")
        try:
            notification_data = {
                "user_id": TEST_USER_ID,
                "notification_type": "test_notification",
                "title": "Тестовое уведомление",
                "message": "Это тестовое уведомление для проверки системы",
                "scheduled_time": None
            }
            
            async with session.post(f"{BACKEND_URL}/notifications/send", json=notification_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Тестовое уведомление отправлено")
                    print(f"   ID: {result.get('notification', {}).get('id')}")
                else:
                    print(f"❌ Ошибка отправки уведомления: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        # 4. Тест обновления настроек
        print("\n4. Обновление настроек уведомлений...")
        try:
            new_settings = {
                "user_id": TEST_USER_ID,
                "lesson_reminders": True,
                "test_notifications": False,
                "club_reminders": True,
                "daily_motivation": True,
                "reminder_time": "10:00",
                "timezone": "Europe/Moscow"
            }
            
            async with session.post(f"{BACKEND_URL}/notifications/settings", json=new_settings) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Настройки обновлены")
                    print(f"   Новое время напоминаний: {result.get('settings', {}).get('reminder_time')}")
                else:
                    print(f"❌ Ошибка обновления настроек: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        # 5. Тест отметки уведомления как прочитанного
        print("\n5. Отметка уведомления как прочитанного...")
        try:
            async with session.post(f"{BACKEND_URL}/notifications/1/read?user_id={TEST_USER_ID}") as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Уведомление отмечено как прочитанное")
                else:
                    print(f"❌ Ошибка отметки уведомления: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        # 6. Проверка финального состояния
        print("\n6. Финальная проверка уведомлений...")
        try:
            async with session.get(f"{BACKEND_URL}/notifications?user_id={TEST_USER_ID}") as response:
                if response.status == 200:
                    data = await response.json()
                    notifications = data.get('notifications', [])
                    unread_count = data.get('unread_count', 0)
                    
                    print(f"✅ Финальное состояние:")
                    print(f"   Всего уведомлений: {len(notifications)}")
                    print(f"   Непрочитанных: {unread_count}")
                    
                    if notifications:
                        print("   Последние уведомления:")
                        for i, notification in enumerate(notifications[-3:], 1):
                            status = "🔴" if not notification["is_read"] else "⚪"
                            print(f"   {i}. {status} {notification['title']}")
                else:
                    print(f"❌ Ошибка финальной проверки: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

async def test_telegram_bot_notifications():
    """Тестирование уведомлений через Telegram бота"""
    print("\n🤖 Тестирование уведомлений через Telegram бота...")
    
    # Здесь можно добавить тесты для проверки отправки уведомлений через бота
    # Для этого нужно будет запустить бота и проверить отправку сообщений
    
    print("⚠️  Для полного тестирования Telegram бота:")
    print("   1. Запустите backend: uvicorn backend.main:app --reload")
    print("   2. Запустите бота: python run_bot.py")
    print("   3. Отправьте команду /notifications в боте")

def main():
    """Основная функция"""
    print("🚀 Запуск тестов системы уведомлений")
    print("=" * 50)
    
    # Проверяем доступность backend
    async def check_backend():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BACKEND_URL}/ping") as response:
                    if response.status == 200:
                        print("✅ Backend доступен")
                        return True
                    else:
                        print("❌ Backend недоступен")
                        return False
        except Exception as e:
            print(f"❌ Ошибка подключения к backend: {e}")
            return False
    
    async def run_tests():
        if await check_backend():
            await test_notifications()
            await test_telegram_bot_notifications()
        else:
            print("\n💡 Для запуска тестов:")
            print("   1. Запустите backend: uvicorn backend.main:app --reload")
            print("   2. Запустите этот скрипт снова")
    
    asyncio.run(run_tests())
    
    print("\n" + "=" * 50)
    print("🏁 Тестирование завершено")

if __name__ == "__main__":
    main() 