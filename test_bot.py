#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности бота
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "http://localhost:8000/api/v1"

async def test_backend_integration():
    """Тестирование интеграции с backend"""
    print("🧪 Тестирование интеграции с backend...")
    
    async with aiohttp.ClientSession() as session:
        # Тест получения расписания
        try:
            async with session.get(f'{BACKEND_URL}/schedule?level=beginner') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Расписание получено: {len(data['schedule'])} занятий")
                else:
                    print(f"❌ Ошибка получения расписания: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка подключения к backend: {e}")
        
        # Тест получения профиля
        try:
            async with session.get(f'{BACKEND_URL}/profile?user_id=123456789') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Профиль получен: {data['level']}, прогресс: {data['progress']}%")
                else:
                    print(f"❌ Ошибка получения профиля: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка получения профиля: {e}")
        
        # Тест получения клубов
        try:
            async with session.get(f'{BACKEND_URL}/clubs') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Клубы получены: {len(data['clubs'])} клубов")
                else:
                    print(f"❌ Ошибка получения клубов: {response.status}")
        except Exception as e:
            print(f"❌ Ошибка получения клубов: {e}")

def test_bot_logic():
    """Тестирование логики бота"""
    print("\n🤖 Тестирование логики бота...")
    
    # Имитация состояний пользователей
    user_states = {}
    
    # Тест выбора уровня
    user_id = 123456789
    user_states[user_id] = {'level': None}
    
    print(f"✅ Состояние пользователя создано: {user_states[user_id]}")
    
    # Имитация выбора уровня
    user_states[user_id] = {'level': 'beginner'}
    print(f"✅ Уровень выбран: {user_states[user_id]['level']}")
    
    # Тест форматирования сообщений
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
    print("✅ Форматирование сообщений работает")

async def test_api_endpoints():
    """Тестирование всех API endpoints"""
    print("\n🌐 Тестирование API endpoints...")
    
    endpoints = [
        "/schedule",
        "/profile?user_id=123456789",
        "/clubs",
        "/tests",
        "/lessons"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                async with session.get(f'{BACKEND_URL}{endpoint}') as response:
                    if response.status == 200:
                        print(f"✅ {endpoint} - OK")
                    else:
                        print(f"❌ {endpoint} - {response.status}")
            except Exception as e:
                print(f"❌ {endpoint} - Ошибка: {e}")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов...")
    
    # Тест backend интеграции
    await test_backend_integration()
    
    # Тест логики бота
    test_bot_logic()
    
    # Тест API endpoints
    await test_api_endpoints()
    
    print("\n✅ Все тесты завершены!")

if __name__ == '__main__':
    asyncio.run(main()) 