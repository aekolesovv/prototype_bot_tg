from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from .models import User, Teacher, Lesson, Club, Test, Notification, NotificationSettings, Booking, ClubMembership, TestResult
from .database import SessionLocal
import json
from datetime import datetime

class UserRepository:
    @staticmethod
    def get_by_telegram_id(telegram_id: str) -> Optional[User]:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                db.refresh(user)
            return user
        finally:
            db.close()
    
    @staticmethod
    def create_user(telegram_id: str, username: str = None, first_name: str = None, last_name: str = None) -> User:
        db = SessionLocal()
        try:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Создаем настройки уведомлений по умолчанию
            notification_settings = NotificationSettings(user_id=user.id)
            db.add(notification_settings)
            db.commit()
            
            return user
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def update_user_level(user_id: int, level: str) -> bool:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.level = level
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def update_progress(user_id: int, progress: float, points: int = None, lessons_completed: int = None) -> bool:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.progress = progress
                if points is not None:
                    user.points = points
                if lessons_completed is not None:
                    user.lessons_completed = lessons_completed
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

class LessonRepository:
    @staticmethod
    def get_all(level: Optional[str] = None) -> List[Lesson]:
        db = SessionLocal()
        try:
            query = db.query(Lesson).filter(Lesson.is_active == True)
            if level:
                query = query.filter(Lesson.level == level)
            lessons = query.all()
            # Отсоединяем объекты от сессии
            for lesson in lessons:
                db.refresh(lesson)
            return lessons
        finally:
            db.close()
    
    @staticmethod
    def get_by_id(lesson_id: int) -> Optional[Lesson]:
        db = SessionLocal()
        try:
            lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                db.refresh(lesson)
            return lesson
        finally:
            db.close()
    
    @staticmethod
    def get_schedule(level: Optional[str] = None) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            query = db.query(Lesson, Teacher).join(Teacher).filter(Lesson.is_active == True)
            if level:
                query = query.filter(Lesson.level == level)
            
            results = query.all()
            schedule = []
            
            for lesson, teacher in results:
                schedule.append({
                    "id": lesson.id,
                    "title": lesson.title,
                    "teacher": teacher.name,
                    "time": f"{lesson.day_of_week}, {lesson.start_time}",
                    "location": lesson.location,
                    "level": lesson.level,
                    "duration": f"{lesson.duration} мин"
                })
            
            return schedule
        finally:
            db.close()

class ClubRepository:
    @staticmethod
    def get_all() -> List[Club]:
        db = SessionLocal()
        try:
            clubs = db.query(Club).filter(Club.is_active == True).all()
            # Отсоединяем объекты от сессии
            for club in clubs:
                db.refresh(club)
            return clubs
        finally:
            db.close()
    
    @staticmethod
    def get_by_id(club_id: int) -> Optional[Club]:
        db = SessionLocal()
        try:
            club = db.query(Club).filter(Club.id == club_id).first()
            if club:
                db.refresh(club)
            return club
        finally:
            db.close()
    
    @staticmethod
    def get_clubs_with_membership_count() -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            clubs = db.query(Club).filter(Club.is_active == True).all()
            result = []
            
            for club in clubs:
                current_participants = db.query(ClubMembership).filter(
                    and_(ClubMembership.club_id == club.id, ClubMembership.is_active == True)
                ).count()
                
                result.append({
                    "id": club.id,
                    "name": club.name,
                    "description": club.description,
                    "schedule": f"{club.day_of_week}, {club.start_time}",
                    "max_participants": club.max_participants,
                    "current_participants": current_participants
                })
            
            return result
        finally:
            db.close()
    
    @staticmethod
    def join_club(user_id: int, club_id: int) -> bool:
        db = SessionLocal()
        try:
            # Проверяем, не состоит ли уже пользователь в клубе
            existing_membership = db.query(ClubMembership).filter(
                and_(ClubMembership.user_id == user_id, ClubMembership.club_id == club_id)
            ).first()
            
            if existing_membership:
                if not existing_membership.is_active:
                    existing_membership.is_active = True
                    db.commit()
                    return True
                return False  # Уже состоит в клубе
            
            # Проверяем, есть ли место в клубе
            club = db.query(Club).filter(Club.id == club_id).first()
            if not club:
                return False
            
            current_members = db.query(ClubMembership).filter(
                and_(ClubMembership.club_id == club_id, ClubMembership.is_active == True)
            ).count()
            
            if current_members >= club.max_participants:
                return False
            
            # Добавляем пользователя в клуб
            membership = ClubMembership(user_id=user_id, club_id=club_id)
            db.add(membership)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

class TestRepository:
    @staticmethod
    def get_all(level: Optional[str] = None) -> List[Test]:
        db = SessionLocal()
        try:
            query = db.query(Test).filter(Test.is_active == True)
            if level:
                query = query.filter(Test.level == level)
            tests = query.all()
            # Отсоединяем объекты от сессии
            for test in tests:
                db.refresh(test)
            return tests
        finally:
            db.close()
    
    @staticmethod
    def get_by_id(test_id: int) -> Optional[Test]:
        db = SessionLocal()
        try:
            test = db.query(Test).filter(Test.id == test_id).first()
            if test:
                db.refresh(test)
            return test
        finally:
            db.close()
    
    @staticmethod
    def submit_test_result(user_id: int, test_id: int, answers: Dict[str, Any], score: float) -> TestResult:
        db = SessionLocal()
        try:
            test_result = TestResult(
                user_id=user_id,
                test_id=test_id,
                score=score,
                answers=json.dumps(answers)
            )
            db.add(test_result)
            db.commit()
            db.refresh(test_result)
            return test_result
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

class NotificationRepository:
    @staticmethod
    def get_user_notifications(user_id: int, limit: int = 50) -> List[Notification]:
        db = SessionLocal()
        try:
            notifications = db.query(Notification).filter(
                Notification.user_id == user_id
            ).order_by(Notification.created_at.desc()).limit(limit).all()
            # Отсоединяем объекты от сессии
            for notification in notifications:
                db.refresh(notification)
            return notifications
        finally:
            db.close()
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        db = SessionLocal()
        try:
            return db.query(Notification).filter(
                and_(Notification.user_id == user_id, Notification.is_read == False)
            ).count()
        finally:
            db.close()
    
    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        db = SessionLocal()
        try:
            notification = db.query(Notification).filter(
                and_(Notification.id == notification_id, Notification.user_id == user_id)
            ).first()
            
            if notification:
                notification.is_read = True
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def mark_all_as_read(user_id: int) -> bool:
        db = SessionLocal()
        try:
            db.query(Notification).filter(
                and_(Notification.user_id == user_id, Notification.is_read == False)
            ).update({"is_read": True})
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def create_notification(user_id: int, title: str, message: str, notification_type: str, scheduled_time: Optional[datetime] = None) -> Notification:
        db = SessionLocal()
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                scheduled_time=scheduled_time
            )
            db.add(notification)
            db.commit()
            db.refresh(notification)
            return notification
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

class NotificationSettingsRepository:
    @staticmethod
    def get_user_settings(user_id: int) -> Optional[NotificationSettings]:
        db = SessionLocal()
        try:
            settings = db.query(NotificationSettings).filter(NotificationSettings.user_id == user_id).first()
            if settings:
                db.refresh(settings)
            return settings
        finally:
            db.close()
    
    @staticmethod
    def update_settings(user_id: int, settings: Dict[str, Any]) -> bool:
        db = SessionLocal()
        try:
            user_settings = db.query(NotificationSettings).filter(NotificationSettings.user_id == user_id).first()
            
            if not user_settings:
                user_settings = NotificationSettings(user_id=user_id)
                db.add(user_settings)
            
            for key, value in settings.items():
                if hasattr(user_settings, key):
                    setattr(user_settings, key, value)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

class BookingRepository:
    @staticmethod
    def create_booking(user_id: int, lesson_id: int, booking_date: datetime) -> Booking:
        db = SessionLocal()
        try:
            booking = Booking(
                user_id=user_id,
                lesson_id=lesson_id,
                booking_date=booking_date
            )
            db.add(booking)
            db.commit()
            db.refresh(booking)
            return booking
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def get_user_bookings(user_id: int) -> List[Booking]:
        db = SessionLocal()
        try:
            bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
            # Отсоединяем объекты от сессии
            for booking in bookings:
                db.refresh(booking)
            return bookings
        finally:
            db.close() 