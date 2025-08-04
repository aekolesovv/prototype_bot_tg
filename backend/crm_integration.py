"""
Интеграция с CRM/LMS системами
Поддерживает интеграцию с популярными системами управления обучением
"""

import asyncio
import aiohttp
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CRMIntegration:
    """Базовый класс для интеграции с CRM/LMS системами"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get('base_url', '')
        self.api_key = config.get('api_key', '')
        self.timeout = config.get('timeout', 30)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> bool:
        """Проверка доступности CRM/LMS системы"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Ошибка проверки здоровья CRM/LMS: {e}")
            return False
    
    async def get_students(self) -> List[Dict[str, Any]]:
        """Получение списка студентов"""
        raise NotImplementedError
    
    async def get_lessons(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Получение расписания занятий"""
        raise NotImplementedError
    
    async def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        """Получение прогресса студента"""
        raise NotImplementedError
    
    async def create_lesson_booking(self, student_id: str, lesson_id: str, date: str) -> bool:
        """Бронирование занятия"""
        raise NotImplementedError
    
    async def get_tests(self, student_id: str = None) -> List[Dict[str, Any]]:
        """Получение доступных тестов"""
        raise NotImplementedError
    
    async def submit_test_results(self, student_id: str, test_id: str, results: Dict[str, Any]) -> bool:
        """Отправка результатов теста"""
        raise NotImplementedError

class MoodleIntegration(CRMIntegration):
    """Интеграция с Moodle LMS"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webservice_token = config.get('webservice_token', '')
        self.session.headers.update({
            'Authorization': f'Bearer {self.webservice_token}'
        })
    
    async def get_students(self) -> List[Dict[str, Any]]:
        """Получение списка студентов из Moodle"""
        try:
            params = {
                'wstoken': self.webservice_token,
                'wsfunction': 'core_enrol_get_enrolled_users',
                'moodlewsrestformat': 'json',
                'courseid': self.config.get('course_id', 1)
            }
            
            async with self.session.get(f"{self.base_url}/webservice/rest/server.php", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    students = []
                    for user in data:
                        students.append({
                            'id': str(user.get('id')),
                            'username': user.get('username'),
                            'firstname': user.get('firstname'),
                            'lastname': user.get('lastname'),
                            'email': user.get('email'),
                            'level': self._determine_level(user),
                            'enrolled_date': user.get('enrolleddate')
                        })
                    return students
                else:
                    logger.error(f"Ошибка получения студентов: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Ошибка интеграции с Moodle: {e}")
            return []
    
    async def get_lessons(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Получение расписания занятий из Moodle"""
        try:
            params = {
                'wstoken': self.webservice_token,
                'wsfunction': 'core_calendar_get_calendar_events',
                'moodlewsrestformat': 'json',
                'events[courseids][]': self.config.get('course_id', 1)
            }
            
            if start_date:
                params['events[timestartfrom]'] = start_date
            if end_date:
                params['events[timestartto]'] = end_date
            
            async with self.session.get(f"{self.base_url}/webservice/rest/server.php", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    lessons = []
                    for event in data.get('events', []):
                        if event.get('eventtype') == 'course':
                            lessons.append({
                                'id': str(event.get('id')),
                                'title': event.get('name'),
                                'description': event.get('description'),
                                'start_time': event.get('timestart'),
                                'end_time': event.get('timeduration'),
                                'location': event.get('location', 'Онлайн'),
                                'teacher': self._get_teacher_name(event),
                                'level': self._determine_lesson_level(event)
                            })
                    return lessons
                else:
                    logger.error(f"Ошибка получения занятий: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Ошибка получения занятий из Moodle: {e}")
            return []
    
    async def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        """Получение прогресса студента из Moodle"""
        try:
            params = {
                'wstoken': self.webservice_token,
                'wsfunction': 'core_completion_get_activities_completion_status',
                'moodlewsrestformat': 'json',
                'userid': student_id,
                'courseid': self.config.get('course_id', 1)
            }
            
            async with self.session.get(f"{self.base_url}/webservice/rest/server.php", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    progress = {
                        'student_id': student_id,
                        'completed_activities': 0,
                        'total_activities': len(data.get('statuses', [])),
                        'completion_percentage': 0,
                        'last_activity': None,
                        'points': 0
                    }
                    
                    for status in data.get('statuses', []):
                        if status.get('state') == 1:  # Completed
                            progress['completed_activities'] += 1
                    
                    if progress['total_activities'] > 0:
                        progress['completion_percentage'] = int(
                            (progress['completed_activities'] / progress['total_activities']) * 100
                        )
                    
                    return progress
                else:
                    logger.error(f"Ошибка получения прогресса: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Ошибка получения прогресса из Moodle: {e}")
            return {}
    
    def _determine_level(self, user: Dict[str, Any]) -> str:
        """Определение уровня студента"""
        # Логика определения уровня на основе данных пользователя
        # В реальном проекте здесь будет более сложная логика
        return "beginner"
    
    def _determine_lesson_level(self, event: Dict[str, Any]) -> str:
        """Определение уровня занятия"""
        # Логика определения уровня занятия
        return "beginner"
    
    def _get_teacher_name(self, event: Dict[str, Any]) -> str:
        """Получение имени преподавателя"""
        # В реальном проекте здесь будет логика получения преподавателя
        return "Преподаватель"

class CanvasIntegration(CRMIntegration):
    """Интеграция с Canvas LMS"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.access_token = config.get('access_token', '')
        self.course_id = config.get('course_id', '')
        self.session.headers.update({
            'Authorization': f'Bearer {self.access_token}'
        })
    
    async def get_students(self) -> List[Dict[str, Any]]:
        """Получение списка студентов из Canvas"""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/courses/{self.course_id}/users") as response:
                if response.status == 200:
                    data = await response.json()
                    students = []
                    for user in data:
                        if user.get('enrollment_type') == 'student':
                            students.append({
                                'id': str(user.get('id')),
                                'username': user.get('login_id'),
                                'firstname': user.get('first_name'),
                                'lastname': user.get('last_name'),
                                'email': user.get('email'),
                                'level': self._determine_level(user),
                                'enrolled_date': user.get('created_at')
                            })
                    return students
                else:
                    logger.error(f"Ошибка получения студентов: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Ошибка интеграции с Canvas: {e}")
            return []
    
    async def get_lessons(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Получение расписания занятий из Canvas"""
        try:
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
            
            async with self.session.get(f"{self.base_url}/api/v1/courses/{self.course_id}/calendar_events", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    lessons = []
                    for event in data:
                        lessons.append({
                            'id': str(event.get('id')),
                            'title': event.get('title'),
                            'description': event.get('description'),
                            'start_time': event.get('start_at'),
                            'end_time': event.get('end_at'),
                            'location': event.get('location_name', 'Онлайн'),
                            'teacher': self._get_teacher_name(event),
                            'level': self._determine_lesson_level(event)
                        })
                    return lessons
                else:
                    logger.error(f"Ошибка получения занятий: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Ошибка получения занятий из Canvas: {e}")
            return []
    
    def _determine_level(self, user: Dict[str, Any]) -> str:
        """Определение уровня студента"""
        return "beginner"
    
    def _determine_lesson_level(self, event: Dict[str, Any]) -> str:
        """Определение уровня занятия"""
        return "beginner"
    
    def _get_teacher_name(self, event: Dict[str, Any]) -> str:
        """Получение имени преподавателя"""
        return "Преподаватель"

class CRMFactory:
    """Фабрика для создания интеграций с CRM/LMS"""
    
    @staticmethod
    def create_integration(crm_type: str, config: Dict[str, Any]) -> CRMIntegration:
        """Создание интеграции по типу CRM/LMS"""
        if crm_type.lower() == 'moodle':
            return MoodleIntegration(config)
        elif crm_type.lower() == 'canvas':
            return CanvasIntegration(config)
        else:
            raise ValueError(f"Неподдерживаемый тип CRM/LMS: {crm_type}")

# Конфигурация по умолчанию
DEFAULT_CRM_CONFIG = {
    'moodle': {
        'base_url': os.getenv('MOODLE_URL', 'https://your-moodle-site.com'),
        'webservice_token': os.getenv('MOODLE_TOKEN', ''),
        'course_id': int(os.getenv('MOODLE_COURSE_ID', 1)),
        'timeout': 30
    },
    'canvas': {
        'base_url': os.getenv('CANVAS_URL', 'https://your-canvas-site.com'),
        'access_token': os.getenv('CANVAS_TOKEN', ''),
        'course_id': os.getenv('CANVAS_COURSE_ID', ''),
        'timeout': 30
    }
}

async def test_crm_integration(crm_type: str = 'moodle'):
    """Тестирование интеграции с CRM/LMS"""
    config = DEFAULT_CRM_CONFIG.get(crm_type, {})
    
    if not config.get('base_url') or not config.get('webservice_token' if crm_type == 'moodle' else 'access_token'):
        print(f"❌ Не настроена конфигурация для {crm_type}")
        return False
    
    try:
        async with CRMFactory.create_integration(crm_type, config) as crm:
            # Проверка здоровья
            if await crm.health_check():
                print(f"✅ {crm_type.upper()} доступен")
                
                # Получение студентов
                students = await crm.get_students()
                print(f"📚 Найдено студентов: {len(students)}")
                
                # Получение занятий
                lessons = await crm.get_lessons()
                print(f"📅 Найдено занятий: {len(lessons)}")
                
                return True
            else:
                print(f"❌ {crm_type.upper()} недоступен")
                return False
    except Exception as e:
        print(f"❌ Ошибка интеграции с {crm_type}: {e}")
        return False

if __name__ == "__main__":
    # Тестирование интеграции
    asyncio.run(test_crm_integration('moodle')) 