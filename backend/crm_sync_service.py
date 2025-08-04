"""
Сервис синхронизации данных с CRM/LMS системами
Обеспечивает автоматическую синхронизацию студентов, занятий и прогресса
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .crm_integration import CRMFactory, DEFAULT_CRM_CONFIG

logger = logging.getLogger(__name__)

class CRMSyncService:
    """Сервис синхронизации с CRM/LMS"""
    
    def __init__(self, crm_type: str = 'moodle', config: Optional[Dict[str, Any]] = None):
        self.crm_type = crm_type
        self.config = config or DEFAULT_CRM_CONFIG.get(crm_type, {})
        self.sync_interval = 300  # 5 минут
        self.running = False
        self.last_sync = None
        
    async def start_sync(self):
        """Запуск автоматической синхронизации"""
        self.running = True
        logger.info(f"Запуск синхронизации с {self.crm_type.upper()}")
        
        while self.running:
            try:
                await self.sync_all_data()
                self.last_sync = datetime.now()
                logger.info(f"Синхронизация завершена: {self.last_sync}")
                
                # Ждем до следующей синхронизации
                await asyncio.sleep(self.sync_interval)
                
            except Exception as e:
                logger.error(f"Ошибка синхронизации: {e}")
                await asyncio.sleep(60)  # Ждем минуту при ошибке
    
    async def stop_sync(self):
        """Остановка синхронизации"""
        self.running = False
        logger.info("Синхронизация остановлена")
    
    async def sync_all_data(self):
        """Синхронизация всех данных"""
        try:
            async with CRMFactory.create_integration(self.crm_type, self.config) as crm:
                # Синхронизация студентов
                await self.sync_students(crm)
                
                # Синхронизация занятий
                await self.sync_lessons(crm)
                
                # Синхронизация прогресса
                await self.sync_progress(crm)
                
                # Синхронизация тестов
                await self.sync_tests(crm)
                
        except Exception as e:
            logger.error(f"Ошибка синхронизации данных: {e}")
    
    async def sync_students(self, crm):
        """Синхронизация студентов"""
        try:
            students = await crm.get_students()
            logger.info(f"Получено {len(students)} студентов из {self.crm_type}")
            
            # Здесь будет логика сохранения в базу данных
            # Пока просто логируем
            for student in students:
                logger.debug(f"Студент: {student.get('firstname')} {student.get('lastname')} - {student.get('level')}")
                
        except Exception as e:
            logger.error(f"Ошибка синхронизации студентов: {e}")
    
    async def sync_lessons(self, crm):
        """Синхронизация занятий"""
        try:
            # Получаем занятия на ближайшие 30 дней
            start_date = datetime.now().isoformat()
            end_date = (datetime.now() + timedelta(days=30)).isoformat()
            
            lessons = await crm.get_lessons(start_date, end_date)
            logger.info(f"Получено {len(lessons)} занятий из {self.crm_type}")
            
            for lesson in lessons:
                logger.debug(f"Занятие: {lesson.get('title')} - {lesson.get('start_time')}")
                
        except Exception as e:
            logger.error(f"Ошибка синхронизации занятий: {e}")
    
    async def sync_progress(self, crm):
        """Синхронизация прогресса студентов"""
        try:
            # Получаем список студентов (в реальном проекте из БД)
            student_ids = ["123456789", "987654321"]
            
            for student_id in student_ids:
                progress = await crm.get_student_progress(student_id)
                if progress:
                    logger.info(f"Прогресс студента {student_id}: {progress.get('completion_percentage')}%")
                    
        except Exception as e:
            logger.error(f"Ошибка синхронизации прогресса: {e}")
    
    async def sync_tests(self, crm):
        """Синхронизация тестов"""
        try:
            tests = await crm.get_tests()
            logger.info(f"Получено {len(tests)} тестов из {self.crm_type}")
            
            for test in tests:
                logger.debug(f"Тест: {test.get('title', 'Без названия')}")
                
        except Exception as e:
            logger.error(f"Ошибка синхронизации тестов: {e}")
    
    async def manual_sync(self):
        """Ручная синхронизация"""
        logger.info("Запуск ручной синхронизации")
        await self.sync_all_data()
        self.last_sync = datetime.now()
        logger.info("Ручная синхронизация завершена")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Получение статуса синхронизации"""
        return {
            'crm_type': self.crm_type,
            'running': self.running,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_interval': self.sync_interval
        }

class CRMCache:
    """Кэш для данных CRM/LMS"""
    
    def __init__(self):
        self.students = {}
        self.lessons = {}
        self.progress = {}
        self.tests = {}
        self.cache_timeout = 3600  # 1 час
    
    def update_students(self, students: List[Dict[str, Any]]):
        """Обновление кэша студентов"""
        self.students = {
            student['id']: {
                'data': student,
                'timestamp': datetime.now()
            }
            for student in students
        }
    
    def update_lessons(self, lessons: List[Dict[str, Any]]):
        """Обновление кэша занятий"""
        self.lessons = {
            lesson['id']: {
                'data': lesson,
                'timestamp': datetime.now()
            }
            for lesson in lessons
        }
    
    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Получение студента из кэша"""
        if student_id in self.students:
            cache_entry = self.students[student_id]
            if (datetime.now() - cache_entry['timestamp']).seconds < self.cache_timeout:
                return cache_entry['data']
        return None
    
    def get_lessons(self, level: str = None) -> List[Dict[str, Any]]:
        """Получение занятий из кэша"""
        lessons = []
        for lesson_id, cache_entry in self.lessons.items():
            if (datetime.now() - cache_entry['timestamp']).seconds < self.cache_timeout:
                lesson = cache_entry['data']
                if level is None or lesson.get('level') == level:
                    lessons.append(lesson)
        return lessons
    
    def clear_expired(self):
        """Очистка устаревших данных"""
        current_time = datetime.now()
        
        # Очистка студентов
        expired_students = [
            student_id for student_id, cache_entry in self.students.items()
            if (current_time - cache_entry['timestamp']).seconds >= self.cache_timeout
        ]
        for student_id in expired_students:
            del self.students[student_id]
        
        # Очистка занятий
        expired_lessons = [
            lesson_id for lesson_id, cache_entry in self.lessons.items()
            if (current_time - cache_entry['timestamp']).seconds >= self.cache_timeout
        ]
        for lesson_id in expired_lessons:
            del self.lessons[lesson_id]

# Глобальный экземпляр кэша
crm_cache = CRMCache()

async def start_crm_sync(crm_type: str = 'moodle'):
    """Запуск синхронизации CRM/LMS"""
    sync_service = CRMSyncService(crm_type)
    await sync_service.start_sync()

async def test_crm_sync():
    """Тестирование синхронизации CRM/LMS"""
    print("🧪 Тестирование синхронизации CRM/LMS...")
    
    sync_service = CRMSyncService('moodle')
    
    try:
        # Тест ручной синхронизации
        await sync_service.manual_sync()
        
        # Проверка статуса
        status = sync_service.get_sync_status()
        print(f"✅ Статус синхронизации: {status}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка тестирования синхронизации: {e}")
        return False

if __name__ == "__main__":
    # Тестирование синхронизации
    asyncio.run(test_crm_sync()) 