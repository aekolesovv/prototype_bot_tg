from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
import json
import asyncio
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from db.repositories import (
    UserRepository, LessonRepository, ClubRepository, TestRepository,
    NotificationRepository, NotificationSettingsRepository, BookingRepository
)
from .auth import get_current_user, create_telegram_token
from datetime import datetime

router = APIRouter()

# Pydantic модели
class NotificationRequest(BaseModel):
    notification_type: str
    title: str
    message: str
    scheduled_time: Optional[str] = None

class NotificationSettingsRequest(BaseModel):
    lesson_reminders: bool = True
    test_notifications: bool = True
    club_reminders: bool = True
    daily_motivation: bool = True
    reminder_time: str = "09:00"
    timezone: str = "Europe/Moscow"

class BookingRequest(BaseModel):
    lesson_id: int
    booking_date: Optional[str] = None

class TestSubmissionRequest(BaseModel):
    test_id: int
    answers: dict

class LoginRequest(BaseModel):
    telegram_id: str

@router.post('/auth/login')
def login(request: LoginRequest):
    """Получить токен доступа для Telegram пользователя"""
    try:
        # Получаем или создаем пользователя
        user = UserRepository.get_by_telegram_id(request.telegram_id)
        if not user:
            user = UserRepository.create_user(request.telegram_id)
        
        # Создаем токен
        token = create_telegram_token(request.telegram_id)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.telegram_id,
            "level": user.level
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при авторизации: {str(e)}")

@router.get('/schedule')
def get_schedule(
    level: Optional[str] = Query(None, description="Уровень обучения"),
    current_user = Depends(get_current_user)
):
    """Получить расписание занятий (защищенный)"""
    try:
        schedule = LessonRepository.get_schedule(level)
        return {
            "schedule": schedule,
            "total": len(schedule),
            "level": level
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении расписания: {str(e)}")

@router.post('/book')
def book_lesson(
    request: BookingRequest,
    current_user = Depends(get_current_user)
):
    """Забронировать урок (защищенный)"""
    try:
        # Проверяем существование урока
        lesson = LessonRepository.get_by_id(request.lesson_id)
        if not lesson:
            raise HTTPException(status_code=404, detail="Урок не найден")
        
        # Парсим дату бронирования
        booking_date = datetime.now()
        if request.booking_date:
            try:
                booking_date = datetime.fromisoformat(request.booking_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Неверный формат даты")
        
        # Создаем бронирование
        booking = BookingRepository.create_booking(current_user.id, request.lesson_id, booking_date)
        
        return {
            "success": True,
            "message": f"Урок '{lesson.title}' забронирован успешно!",
            "lesson": {
                "id": lesson.id,
                "title": lesson.title,
                "teacher": lesson.teacher.name if lesson.teacher else "Не назначен",
                "time": f"{lesson.day_of_week}, {lesson.start_time}",
                "location": lesson.location
            },
            "booking_id": booking.id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при бронировании: {str(e)}")

@router.get('/clubs')
def get_clubs(current_user = Depends(get_current_user)):
    """Получить список клубов (защищенный)"""
    try:
        clubs = ClubRepository.get_clubs_with_membership_count()
        return {
            "clubs": clubs,
            "total": len(clubs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении клубов: {str(e)}")

@router.post('/clubs/{club_id}/join')
def join_club(
    club_id: int, 
    current_user = Depends(get_current_user)
):
    """Присоединиться к клубу (защищенный)"""
    try:
        # Проверяем существование клуба
        club = ClubRepository.get_by_id(club_id)
        if not club:
            raise HTTPException(status_code=404, detail="Клуб не найден")
        
        # Пытаемся присоединиться к клубу
        success = ClubRepository.join_club(current_user.id, club_id)
        
        if success:
            return {
                "success": True,
                "message": f"Вы успешно присоединились к клубу '{club.name}'!",
                "club": {
                    "id": club.id,
                    "name": club.name,
                    "description": club.description,
                    "schedule": f"{club.day_of_week}, {club.start_time}"
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Не удалось присоединиться к клубу. Возможно, клуб переполнен или вы уже состоите в нем.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при присоединении к клубу: {str(e)}")

@router.get('/profile')
def get_profile(current_user = Depends(get_current_user)):
    """Получить профиль пользователя (защищенный)"""
    try:
        return {
            "user_id": current_user.telegram_id,
            "level": current_user.level,
            "progress": current_user.progress,
            "lessons_completed": current_user.lessons_completed,
            "points": current_user.points,
            "current_streak": 0,  # TODO: Добавить логику подсчета стрика
            "total_study_time": "0 часов"  # TODO: Добавить логику подсчета времени
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении профиля: {str(e)}")

@router.post('/test')
def submit_test(
    request: TestSubmissionRequest,
    current_user = Depends(get_current_user)
):
    """Отправить результаты теста (защищенный)"""
    try:
        # Получаем тест
        test = TestRepository.get_by_id(request.test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Тест не найден")
        
        # Парсим вопросы из JSON
        questions = json.loads(test.questions)
        
        # Подсчитываем правильные ответы
        correct_answers = 0
        total_questions = len(questions)
        
        for i, question in enumerate(questions):
            user_answer = request.answers.get(str(i))
            if user_answer is not None and user_answer == question["correct_answer"]:
                correct_answers += 1
        
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Сохраняем результат
        test_result = TestRepository.submit_test_result(current_user.id, request.test_id, request.answers, score)
        
        # Обновляем прогресс пользователя
        new_progress = min(current_user.progress + (score / 10), 100)  # Увеличиваем прогресс на 10% от результата
        UserRepository.update_progress(current_user.id, new_progress, current_user.points + int(score))
        
        return {
            "success": True,
            "score": score,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "message": f"Тест завершен! Ваш результат: {score:.1f}%"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при отправке теста: {str(e)}")

@router.get('/tests')
def get_tests(
    level: Optional[str] = Query(None, description="Уровень теста"),
    current_user = Depends(get_current_user)
):
    """Получить список тестов (защищенный)"""
    try:
        tests = TestRepository.get_all(level)
        test_list = []
        
        for test in tests:
            questions = json.loads(test.questions)
            test_list.append({
                "id": test.id,
                "title": test.title,
                "description": test.description,
                "level": test.level,
                "questions_count": len(questions),
                "time_limit": test.time_limit
            })
        
        return {
            "tests": test_list,
            "total": len(test_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении тестов: {str(e)}")

@router.get('/notifications')
def get_notifications(current_user = Depends(get_current_user)):
    """Получить уведомления пользователя (защищенный)"""
    try:
        notifications = NotificationRepository.get_user_notifications(current_user.id)
        unread_count = NotificationRepository.get_unread_count(current_user.id)
        
        notification_list = []
        for notification in notifications:
            notification_list.append({
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "is_read": notification.is_read,
                "notification_type": notification.notification_type,
                "created_at": notification.created_at.isoformat() if notification.created_at else None
            })
        
        return {
            "notifications": notification_list,
            "unread_count": unread_count,
            "total": len(notification_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении уведомлений: {str(e)}")

@router.post('/notifications/{notification_id}/read')
def mark_notification_read(
    notification_id: int, 
    current_user = Depends(get_current_user)
):
    """Отметить уведомление как прочитанное (защищенный)"""
    try:
        success = NotificationRepository.mark_as_read(notification_id, current_user.id)
        
        if success:
            return {"success": True, "message": "Уведомление отмечено как прочитанное"}
        else:
            raise HTTPException(status_code=404, detail="Уведомление не найдено")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении уведомления: {str(e)}")

@router.post('/notifications/read-all')
def mark_all_notifications_read(current_user = Depends(get_current_user)):
    """Отметить все уведомления как прочитанные (защищенный)"""
    try:
        success = NotificationRepository.mark_all_as_read(current_user.id)
        
        if success:
            return {"success": True, "message": "Все уведомления отмечены как прочитанные"}
        else:
            raise HTTPException(status_code=500, detail="Ошибка при обновлении уведомлений")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении уведомлений: {str(e)}")

@router.get('/notifications/settings')
def get_notification_settings(current_user = Depends(get_current_user)):
    """Получить настройки уведомлений пользователя (защищенный)"""
    try:
        settings = NotificationSettingsRepository.get_user_settings(current_user.id)
        
        if not settings:
            # Создаем настройки по умолчанию
            settings = NotificationSettingsRepository.update_settings(current_user.id, {})
        
        return {
            "lesson_reminders": settings.lesson_reminders,
            "test_notifications": settings.test_notifications,
            "club_reminders": settings.club_reminders,
            "daily_motivation": settings.daily_motivation,
            "reminder_time": settings.reminder_time,
            "timezone": settings.timezone
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении настроек: {str(e)}")

@router.post('/notifications/settings')
def update_notification_settings(
    request: NotificationSettingsRequest,
    current_user = Depends(get_current_user)
):
    """Обновить настройки уведомлений пользователя (защищенный)"""
    try:
        settings = {
            "lesson_reminders": request.lesson_reminders,
            "test_notifications": request.test_notifications,
            "club_reminders": request.club_reminders,
            "daily_motivation": request.daily_motivation,
            "reminder_time": request.reminder_time,
            "timezone": request.timezone
        }
        
        success = NotificationSettingsRepository.update_settings(current_user.id, settings)
        
        if success:
            return {"success": True, "message": "Настройки уведомлений обновлены"}
        else:
            raise HTTPException(status_code=500, detail="Ошибка при обновлении настроек")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении настроек: {str(e)}")

@router.get('/health')
def health_check():
    """Проверка здоровья API (публичный)"""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    } 