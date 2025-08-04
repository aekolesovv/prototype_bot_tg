from fastapi import APIRouter, Query
from typing import List, Optional
import json
import asyncio
from pydantic import BaseModel

router = APIRouter()

# Pydantic модели
class NotificationRequest(BaseModel):
    user_id: str
    notification_type: str
    title: str
    message: str
    scheduled_time: Optional[str] = None

class NotificationSettingsRequest(BaseModel):
    user_id: str
    lesson_reminders: bool = True
    test_notifications: bool = True
    club_reminders: bool = True
    daily_motivation: bool = True
    reminder_time: str = "09:00"
    timezone: str = "Europe/Moscow"

class CRMConfigRequest(BaseModel):
    crm_type: str
    base_url: str
    api_token: str
    course_id: Optional[str] = None

# Моковые данные (в реальном проекте используйте БД)
MOCK_SCHEDULE = [
    {
        "id": 1,
        "title": "Английский для начинающих",
        "teacher": "Анна Петрова",
        "time": "Понедельник, 18:00",
        "location": "Аудитория 1",
        "level": "beginner",
        "duration": "60 мин"
    },
    {
        "id": 2,
        "title": "Разговорный английский",
        "teacher": "Михаил Иванов",
        "time": "Вторник, 19:00",
        "location": "Аудитория 2",
        "level": "advanced",
        "duration": "90 мин"
    },
    {
        "id": 3,
        "title": "Грамматика английского",
        "teacher": "Елена Сидорова",
        "time": "Среда, 17:30",
        "location": "Аудитория 1",
        "level": "beginner",
        "duration": "60 мин"
    }
]

MOCK_CLUBS = [
    {
        "id": 1,
        "name": "Разговорный клуб",
        "description": "Практика разговорного английского",
        "schedule": "Пятница, 19:00",
        "max_participants": 10,
        "current_participants": 7
    },
    {
        "id": 2,
        "name": "Клуб чтения",
        "description": "Чтение и обсуждение книг на английском",
        "schedule": "Суббота, 15:00",
        "max_participants": 8,
        "current_participants": 5
    },
    {
        "id": 3,
        "name": "Клуб кино",
        "description": "Просмотр и обсуждение фильмов на английском",
        "schedule": "Воскресенье, 16:00",
        "max_participants": 12,
        "current_participants": 9
    },
    {
        "id": 4,
        "name": "Клуб делового английского",
        "description": "Бизнес-английский и деловая переписка",
        "schedule": "Четверг, 20:00",
        "max_participants": 6,
        "current_participants": 4
    }
]

MOCK_PROFILES = {
    "123456789": {
        "user_id": "123456789",
        "level": "beginner",
        "progress": 65,
        "lessons_completed": 12,
        "points": 850,
        "current_streak": 5,
        "total_study_time": "45 часов"
    },
    "987654321": {
        "user_id": "987654321",
        "level": "advanced",
        "progress": 78,
        "lessons_completed": 25,
        "points": 1200,
        "current_streak": 12,
        "total_study_time": "120 часов"
    }
}

# Моковые данные для уведомлений
MOCK_NOTIFICATIONS = {
    "123456789": [
        {
            "id": 1,
            "type": "lesson_reminder",
            "title": "Напоминание о занятии",
            "message": "Завтра в 18:00 у вас занятие 'Английский для начинающих'",
            "scheduled_time": "2024-01-15T18:00:00",
            "is_read": False,
            "created_at": "2024-01-14T10:00:00"
        },
        {
            "id": 2,
            "type": "test_reminder",
            "title": "Доступен новый тест",
            "message": "Пройдите тест 'Грамматика Present Simple' для получения баллов",
            "scheduled_time": None,
            "is_read": True,
            "created_at": "2024-01-13T15:30:00"
        }
    ],
    "987654321": [
        {
            "id": 3,
            "type": "club_reminder",
            "title": "Клуб разговорного английского",
            "message": "Сегодня в 19:00 состоится встреча разговорного клуба",
            "scheduled_time": "2024-01-15T19:00:00",
            "is_read": False,
            "created_at": "2024-01-15T09:00:00"
        }
    ]
}

MOCK_NOTIFICATION_SETTINGS = {
    "123456789": {
        "lesson_reminders": True,
        "test_notifications": True,
        "club_reminders": True,
        "daily_motivation": True,
        "reminder_time": "09:00",
        "timezone": "Europe/Moscow"
    },
    "987654321": {
        "lesson_reminders": True,
        "test_notifications": False,
        "club_reminders": True,
        "daily_motivation": False,
        "reminder_time": "08:00",
        "timezone": "Europe/Moscow"
    }
}

@router.get('/schedule')
def get_schedule(
    level: Optional[str] = Query(None, description="Уровень обучения"),
    user_id: Optional[str] = Query(None, description="ID пользователя")
):
    """Получить расписание занятий"""
    if level and level != "all":
        filtered_schedule = [lesson for lesson in MOCK_SCHEDULE if lesson["level"] == level]
    else:
        filtered_schedule = MOCK_SCHEDULE
    
    return {
        "schedule": filtered_schedule,
        "total": len(filtered_schedule),
        "level": level
    }

@router.post('/book')
def book_lesson(
    lesson_id: int,
    user_id: str,
    date: Optional[str] = None
):
    """Забронировать урок"""
    # Находим урок в расписании
    lesson = next((l for l in MOCK_SCHEDULE if l["id"] == lesson_id), None)
    
    if not lesson:
        return {"success": False, "error": "Урок не найден"}
    
    return {
        "success": True,
        "message": f"Урок '{lesson['title']}' забронирован успешно!",
        "lesson": lesson,
        "booking_id": f"BK{lesson_id}_{user_id}"
    }

@router.get('/clubs')
def get_clubs():
    """Получить список клубов"""
    return {
        "clubs": MOCK_CLUBS,
        "total": len(MOCK_CLUBS)
    }

@router.post('/clubs/{club_id}/join')
def join_club(club_id: int, user_id: str):
    """Присоединиться к клубу"""
    club = next((c for c in MOCK_CLUBS if c["id"] == club_id), None)
    
    if not club:
        return {"success": False, "error": "Клуб не найден"}
    
    if club["current_participants"] >= club["max_participants"]:
        return {"success": False, "error": "Клуб переполнен"}
    
    # В реальном проекте здесь была бы логика добавления пользователя
    return {
        "success": True,
        "message": f"Вы успешно присоединились к клубу '{club['name']}'!",
        "club": club
    }

@router.get('/profile')
def get_profile(user_id: str = Query(..., description="ID пользователя")):
    """Получить профиль пользователя"""
    profile = MOCK_PROFILES.get(user_id, {
        "user_id": user_id,
        "level": "Не выбран",
        "progress": 0,
        "lessons_completed": 0,
        "points": 0,
        "current_streak": 0,
        "total_study_time": "0 часов"
    })
    
    return profile

@router.post('/test')
def submit_test(
    test_id: int,
    user_id: str,
    answers: dict
):
    """Отправить результаты теста"""
    # Простая логика подсчета баллов
    correct_answers = 0
    total_questions = len(answers)
    
    # Моковая проверка ответов
    for question_id, answer in answers.items():
        if answer in ["correct", "A", "1"]:  # Примеры правильных ответов
            correct_answers += 1
    
    score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    
    return {
        "success": True,
        "score": score,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "message": f"Тест завершен! Ваш результат: {score}%"
    }

@router.get('/tests')
def get_tests(level: Optional[str] = Query(None, description="Уровень теста")):
    """Получить доступные тесты"""
    mock_tests = [
        {
            "id": 1,
            "title": "Базовый тест по грамматике",
            "level": "beginner",
            "questions_count": 10,
            "duration": "15 минут"
        },
        {
            "id": 2,
            "title": "Тест на знание времен",
            "level": "beginner",
            "questions_count": 15,
            "duration": "20 минут"
        },
        {
            "id": 3,
            "title": "Продвинутый тест по лексике",
            "level": "advanced",
            "questions_count": 20,
            "duration": "25 минут"
        }
    ]
    
    if level:
        filtered_tests = [test for test in mock_tests if test["level"] == level]
    else:
        filtered_tests = mock_tests
    
    return {"tests": filtered_tests}

@router.get('/lessons')
def get_lessons(level: Optional[str] = Query(None, description="Уровень урока")):
    """Получить доступные уроки"""
    mock_lessons = [
        {
            "id": 1,
            "title": "Приветствие и знакомство",
            "level": "beginner",
            "duration": "30 минут",
            "type": "video"
        },
        {
            "id": 2,
            "title": "Present Simple",
            "level": "beginner",
            "duration": "45 минут",
            "type": "interactive"
        },
        {
            "id": 3,
            "title": "Business English Basics",
            "level": "advanced",
            "duration": "60 минут",
            "type": "video"
        }
    ]
    
    if level:
        filtered_lessons = [lesson for lesson in mock_lessons if lesson["level"] == level]
    else:
        filtered_lessons = mock_lessons
    
    return {"lessons": filtered_lessons}

@router.get('/notifications')
def get_notifications(user_id: str = Query(..., description="ID пользователя")):
    """Получить уведомления пользователя"""
    notifications = MOCK_NOTIFICATIONS.get(user_id, [])
    return {
        "notifications": notifications,
        "unread_count": len([n for n in notifications if not n["is_read"]])
    }

@router.post('/notifications/{notification_id}/read')
def mark_notification_read(notification_id: int, user_id: str):
    """Отметить уведомление как прочитанное"""
    user_notifications = MOCK_NOTIFICATIONS.get(user_id, [])
    
    for notification in user_notifications:
        if notification["id"] == notification_id:
            notification["is_read"] = True
            return {"success": True, "message": "Уведомление отмечено как прочитанное"}
    
    return {"success": False, "message": "Уведомление не найдено"}

@router.post('/notifications/read-all')
def mark_all_notifications_read(user_id: str):
    """Отметить все уведомления как прочитанные"""
    user_notifications = MOCK_NOTIFICATIONS.get(user_id, [])
    
    for notification in user_notifications:
        notification["is_read"] = True
    
    return {"success": True, "message": "Все уведомления отмечены как прочитанные"}

@router.get('/notifications/settings')
def get_notification_settings(user_id: str = Query(..., description="ID пользователя")):
    """Получить настройки уведомлений пользователя"""
    settings = MOCK_NOTIFICATION_SETTINGS.get(user_id, {
        "lesson_reminders": True,
        "test_notifications": True,
        "club_reminders": True,
        "daily_motivation": True,
        "reminder_time": "09:00",
        "timezone": "Europe/Moscow"
    })
    return settings

@router.post('/notifications/settings')
def update_notification_settings(request: NotificationSettingsRequest):
    """Обновить настройки уведомлений"""
    MOCK_NOTIFICATION_SETTINGS[request.user_id] = {
        "lesson_reminders": request.lesson_reminders,
        "test_notifications": request.test_notifications,
        "club_reminders": request.club_reminders,
        "daily_motivation": request.daily_motivation,
        "reminder_time": request.reminder_time,
        "timezone": request.timezone
    }
    
    return {
        "success": True,
        "message": "Настройки уведомлений обновлены",
        "settings": MOCK_NOTIFICATION_SETTINGS[request.user_id]
    }

# Импорт модулей CRM/LMS
from .crm_integration import CRMFactory, DEFAULT_CRM_CONFIG
from .crm_sync_service import CRMSyncService, crm_cache

@router.post('/notifications/send')
def send_notification(request: NotificationRequest):
    """Отправить уведомление пользователю"""
    import datetime
    
    notification = {
        "id": len(MOCK_NOTIFICATIONS.get(request.user_id, [])) + 1,
        "type": request.notification_type,
        "title": request.title,
        "message": request.message,
        "scheduled_time": request.scheduled_time,
        "is_read": False,
        "created_at": datetime.datetime.now().isoformat()
    }
    
    if request.user_id not in MOCK_NOTIFICATIONS:
        MOCK_NOTIFICATIONS[request.user_id] = []
    
    MOCK_NOTIFICATIONS[request.user_id].append(notification)
    
    return {
        "success": True,
        "message": "Уведомление отправлено",
        "notification": notification
    }

# Глобальный экземпляр сервиса синхронизации
crm_sync_service = None

@router.get('/crm/status')
def get_crm_status():
    """Получить статус интеграции с CRM/LMS"""
    global crm_sync_service
    
    if crm_sync_service is None:
        return {
            "status": "not_configured",
            "message": "CRM/LMS интеграция не настроена"
        }
    
    return crm_sync_service.get_sync_status()

@router.post('/crm/sync')
async def manual_crm_sync():
    """Запустить ручную синхронизацию с CRM/LMS"""
    global crm_sync_service
    
    if crm_sync_service is None:
        return {
            "success": False,
            "message": "CRM/LMS интеграция не настроена"
        }
    
    try:
        await crm_sync_service.manual_sync()
        return {
            "success": True,
            "message": "Синхронизация завершена успешно"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка синхронизации: {str(e)}"
        }

@router.get('/crm/students')
def get_crm_students():
    """Получить список студентов из CRM/LMS"""
    students = list(crm_cache.students.values())
    return {
        "students": [entry['data'] for entry in students],
        "total": len(students)
    }

@router.get('/crm/lessons')
def get_crm_lessons(level: Optional[str] = Query(None, description="Уровень занятия")):
    """Получить занятия из CRM/LMS"""
    lessons = crm_cache.get_lessons(level)
    return {
        "lessons": lessons,
        "total": len(lessons)
    }

@router.get('/crm/student/{student_id}')
def get_crm_student(student_id: str):
    """Получить данные студента из CRM/LMS"""
    student = crm_cache.get_student(student_id)
    if student:
        return student
    else:
        return {
            "error": "Студент не найден",
            "student_id": student_id
        }

@router.post('/crm/configure')
def configure_crm_integration(request: CRMConfigRequest):
    """Настроить интеграцию с CRM/LMS"""
    global crm_sync_service
    
    try:
        config = {
            'base_url': request.base_url,
            'timeout': 30
        }
        
        if request.crm_type.lower() == 'moodle':
            config['webservice_token'] = request.api_token
            config['course_id'] = int(request.course_id) if request.course_id else 1
        elif request.crm_type.lower() == 'canvas':
            config['access_token'] = request.api_token
            config['course_id'] = request.course_id or ''
        else:
            return {
                "success": False,
                "message": f"Неподдерживаемый тип CRM/LMS: {request.crm_type}"
            }
        
        # Создаем новый сервис синхронизации
        crm_sync_service = CRMSyncService(request.crm_type, config)
        
        return {
            "success": True,
            "message": f"Интеграция с {request.crm_type.upper()} настроена успешно",
            "config": {
                "crm_type": request.crm_type,
                "base_url": request.base_url,
                "course_id": request.course_id
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка настройки интеграции: {str(e)}"
        }

@router.get('/crm/test')
async def test_crm_connection():
    """Тестирование подключения к CRM/LMS"""
    global crm_sync_service
    
    if crm_sync_service is None:
        return {
            "success": False,
            "message": "CRM/LMS интеграция не настроена"
        }
    
    try:
        async with CRMFactory.create_integration(
            crm_sync_service.crm_type, 
            crm_sync_service.config
        ) as crm:
            # Проверка здоровья
            is_healthy = await crm.health_check()
            
            if is_healthy:
                # Получение тестовых данных
                students = await crm.get_students()
                lessons = await crm.get_lessons()
                
                return {
                    "success": True,
                    "message": "Подключение к CRM/LMS успешно",
                    "data": {
                        "students_count": len(students),
                        "lessons_count": len(lessons),
                        "crm_type": crm_sync_service.crm_type
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "CRM/LMS недоступен"
                }
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка подключения: {str(e)}"
        }

@router.get('/crm/sync/start')
async def start_crm_sync():
    """Запустить автоматическую синхронизацию"""
    global crm_sync_service
    
    if crm_sync_service is None:
        return {
            "success": False,
            "message": "CRM/LMS интеграция не настроена"
        }
    
    try:
        # Запускаем синхронизацию в фоне
        asyncio.create_task(crm_sync_service.start_sync())
        
        return {
            "success": True,
            "message": "Автоматическая синхронизация запущена"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка запуска синхронизации: {str(e)}"
        }

@router.get('/crm/sync/stop')
def stop_crm_sync():
    """Остановить автоматическую синхронизацию"""
    global crm_sync_service
    
    if crm_sync_service is None:
        return {
            "success": False,
            "message": "CRM/LMS интеграция не настроена"
        }
    
    try:
        asyncio.create_task(crm_sync_service.stop_sync())
        
        return {
            "success": True,
            "message": "Автоматическая синхронизация остановлена"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка остановки синхронизации: {str(e)}"
        }

@router.get('/health')
def health_check():
    """Проверка здоровья API"""
    return {
        "status": "healthy",
        "message": "Backend API работает",
        "timestamp": "2024-01-15T12:00:00Z"
    }
