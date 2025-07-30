from fastapi import APIRouter, Query
from typing import List, Optional
import json

router = APIRouter()

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
