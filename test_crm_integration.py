#!/usr/bin/env python3
"""
Тестирование CRM/LMS интеграции с админ-панелью
Проверяет все компоненты интеграции: backend, frontend, синхронизацию
"""

import asyncio
import aiohttp
import json
import time
import sys
import os
from typing import Dict, Any, List

# Добавляем путь к backend для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Импортируем модули с абсолютными путями
from backend.crm_integration import CRMFactory, DEFAULT_CRM_CONFIG
from backend.crm_sync_service import CRMSyncService

class CRMIntegrationTester:
    """Тестер для CRM/LMS интеграции"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8001/api/v1"
        self.webapp_url = "http://localhost:3000"
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Логирование результата теста"""
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        print()
    
    async def test_backend_health(self) -> bool:
        """Тест здоровья backend API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/health") as response:
                    if response.status == 200:
                        return True
                    else:
                        return False
        except Exception as e:
            return False
    
    async def test_crm_status_endpoint(self) -> bool:
        """Тест эндпоинта статуса CRM"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/crm/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("status") == "not_configured"
                    else:
                        return False
        except Exception as e:
            return False
    
    async def test_crm_configuration(self) -> bool:
        """Тест настройки CRM интеграции"""
        try:
            config_data = {
                "crm_type": "moodle",
                "base_url": "https://test-moodle.com",
                "api_token": "test_token_123",
                "course_id": "1"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/crm/configure",
                    json=config_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("success") == True
                    else:
                        return False
        except Exception as e:
            return False
    
    async def test_crm_connection_test(self) -> bool:
        """Тест проверки подключения к CRM"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/crm/test") as response:
                    if response.status == 200:
                        data = await response.json()
                        # Ожидаем ошибку, так как тестовый CRM недоступен
                        return data.get("success") == False
                    else:
                        return False
        except Exception as e:
            return False
    
    async def test_manual_sync(self) -> bool:
        """Тест ручной синхронизации"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.backend_url}/crm/sync") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("success") == True
                    else:
                        return False
        except Exception as e:
            return False
    
    async def test_sync_control(self) -> bool:
        """Тест управления синхронизацией"""
        try:
            async with aiohttp.ClientSession() as session:
                # Тест запуска синхронизации
                async with session.get(f"{self.backend_url}/crm/sync/start") as response:
                    if response.status != 200:
                        return False
                
                # Тест остановки синхронизации
                async with session.get(f"{self.backend_url}/crm/sync/stop") as response:
                    if response.status != 200:
                        return False
                
                return True
        except Exception as e:
            return False
    
    async def test_crm_data_endpoints(self) -> bool:
        """Тест эндпоинтов данных CRM"""
        try:
            async with aiohttp.ClientSession() as session:
                # Тест получения студентов
                async with session.get(f"{self.backend_url}/crm/students") as response:
                    if response.status != 200:
                        return False
                
                # Тест получения занятий
                async with session.get(f"{self.backend_url}/crm/lessons") as response:
                    if response.status != 200:
                        return False
                
                return True
        except Exception as e:
            return False
    
    def test_crm_integration_module(self) -> bool:
        """Тест модуля CRM интеграции"""
        try:
            # Тест создания интеграции
            config = DEFAULT_CRM_CONFIG.get('moodle', {})
            integration = CRMFactory.create_integration('moodle', config)
            
            # Тест создания сервиса синхронизации
            sync_service = CRMSyncService('moodle', config)
            
            return True
        except Exception as e:
            return False
    
    def test_crm_sync_service(self) -> bool:
        """Тест сервиса синхронизации"""
        try:
            config = DEFAULT_CRM_CONFIG.get('moodle', {})
            sync_service = CRMSyncService('moodle', config)
            
            # Проверяем методы сервиса
            status = sync_service.get_sync_status()
            
            return isinstance(status, dict) and 'crm_type' in status
        except Exception as e:
            return False
    
    async def test_webapp_api_calls(self) -> bool:
        """Тест API вызовов из веб-приложения"""
        try:
            # Имитируем вызовы API, которые делает веб-приложение
            async with aiohttp.ClientSession() as session:
                # Тест получения статуса CRM
                async with session.get(f"{self.backend_url}/crm/status") as response:
                    if response.status != 200:
                        return False
                
                # Тест конфигурации CRM
                config_data = {
                    "crm_type": "canvas",
                    "base_url": "https://test-canvas.com",
                    "api_token": "canvas_token_123",
                    "course_id": "course_123"
                }
                
                async with session.post(
                    f"{self.backend_url}/crm/configure",
                    json=config_data
                ) as response:
                    if response.status != 200:
                        return False
                
                return True
        except Exception as e:
            return False
    
    def test_admin_page_structure(self) -> bool:
        """Тест структуры админ-страницы"""
        try:
            # Проверяем наличие файлов админ-панели
            admin_files = [
                "webapp/src/pages/AdminPage.tsx",
                "webapp/src/pages/AdminPage.css",
                "webapp/src/services/api.ts"
            ]
            
            for file_path in admin_files:
                if not os.path.exists(file_path):
                    return False
            
            return True
        except Exception as e:
            return False
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("🧪 ТЕСТИРОВАНИЕ CRM/LMS ИНТЕГРАЦИИ")
        print("=" * 50)
        
        # Тесты backend
        print("🔧 Тестирование Backend:")
        
        backend_health = await self.test_backend_health()
        self.log_test(
            "Здоровье Backend API",
            backend_health,
            "Проверка доступности backend сервера"
        )
        
        crm_status = await self.test_crm_status_endpoint()
        self.log_test(
            "Эндпоинт статуса CRM",
            crm_status,
            "Проверка /crm/status endpoint"
        )
        
        crm_config = await self.test_crm_configuration()
        self.log_test(
            "Настройка CRM интеграции",
            crm_config,
            "Проверка /crm/configure endpoint"
        )
        
        crm_test = await self.test_crm_connection_test()
        self.log_test(
            "Тест подключения к CRM",
            crm_test,
            "Проверка /crm/test endpoint"
        )
        
        manual_sync = await self.test_manual_sync()
        self.log_test(
            "Ручная синхронизация",
            manual_sync,
            "Проверка /crm/sync endpoint"
        )
        
        sync_control = await self.test_sync_control()
        self.log_test(
            "Управление синхронизацией",
            sync_control,
            "Проверка /crm/sync/start и /crm/sync/stop"
        )
        
        data_endpoints = await self.test_crm_data_endpoints()
        self.log_test(
            "Эндпоинты данных CRM",
            data_endpoints,
            "Проверка /crm/students и /crm/lessons"
        )
        
        # Тесты модулей
        print("📦 Тестирование модулей:")
        
        integration_module = self.test_crm_integration_module()
        self.log_test(
            "Модуль CRM интеграции",
            integration_module,
            "Проверка crm_integration.py"
        )
        
        sync_service = self.test_crm_sync_service()
        self.log_test(
            "Сервис синхронизации",
            sync_service,
            "Проверка crm_sync_service.py"
        )
        
        # Тесты веб-приложения
        print("🌐 Тестирование веб-приложения:")
        
        webapp_api = await self.test_webapp_api_calls()
        self.log_test(
            "API вызовы веб-приложения",
            webapp_api,
            "Проверка API вызовов из React приложения"
        )
        
        admin_structure = self.test_admin_page_structure()
        self.log_test(
            "Структура админ-страницы",
            admin_structure,
            "Проверка файлов админ-панели"
        )
        
        # Итоговая статистика
        print("📊 ИТОГОВАЯ СТАТИСТИКА:")
        print("=" * 50)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        
        print(f"Всего тестов: {total_tests}")
        print(f"Пройдено: {passed_tests}")
        print(f"Провалено: {total_tests - passed_tests}")
        print(f"Успешность: {(passed_tests / total_tests) * 100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        else:
            print("\n⚠️ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
            
            print("\n❌ Проваленные тесты:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        return passed_tests == total_tests

async def main():
    """Главная функция тестирования"""
    tester = CRMIntegrationTester()
    
    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 