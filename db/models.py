from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    level = Column(String, default="beginner")  # beginner, advanced
    progress = Column(Float, default=0.0)  # процент прогресса
    points = Column(Integer, default=0)  # баллы
    lessons_completed = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    notifications = relationship("Notification", back_populates="user")
    notification_settings = relationship("NotificationSettings", back_populates="user", uselist=False)
    bookings = relationship("Booking", back_populates="user")
    club_memberships = relationship("ClubMembership", back_populates="user")
    test_results = relationship("TestResult", back_populates="user")

class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    specialization = Column(String, nullable=True)  # beginner, advanced, grammar, speaking
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    lessons = relationship("Lesson", back_populates="teacher")

class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    level = Column(String, nullable=False)  # beginner, advanced
    duration = Column(Integer, default=60)  # в минутах
    max_students = Column(Integer, default=10)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    day_of_week = Column(String, nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(String, nullable=False)  # HH:MM
    location = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    teacher = relationship("Teacher", back_populates="lessons")
    bookings = relationship("Booking", back_populates="lesson")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    booking_date = Column(DateTime, nullable=False)
    status = Column(String, default="confirmed")  # confirmed, cancelled, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("User", back_populates="bookings")
    lesson = relationship("Lesson", back_populates="bookings")

class Club(Base):
    __tablename__ = "clubs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    max_participants = Column(Integer, default=10)
    day_of_week = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    duration = Column(Integer, default=90)  # в минутах
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    memberships = relationship("ClubMembership", back_populates="club")

class ClubMembership(Base):
    __tablename__ = "club_memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    club_id = Column(Integer, ForeignKey("clubs.id"))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Связи
    user = relationship("User", back_populates="club_memberships")
    club = relationship("Club", back_populates="memberships")

class Test(Base):
    __tablename__ = "tests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    level = Column(String, nullable=False)  # beginner, advanced
    questions = Column(Text, nullable=False)  # JSON строка с вопросами
    time_limit = Column(Integer, default=30)  # в минутах
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    results = relationship("TestResult", back_populates="test")

class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    test_id = Column(Integer, ForeignKey("tests.id"))
    score = Column(Float, nullable=False)  # процент правильных ответов
    answers = Column(Text, nullable=False)  # JSON строка с ответами
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("User", back_populates="test_results")
    test = relationship("Test", back_populates="results")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, nullable=False)  # lesson_reminder, test_notification, etc.
    is_read = Column(Boolean, default=False)
    scheduled_time = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("User", back_populates="notifications")

class NotificationSettings(Base):
    __tablename__ = "notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    lesson_reminders = Column(Boolean, default=True)
    test_notifications = Column(Boolean, default=True)
    club_reminders = Column(Boolean, default=True)
    daily_motivation = Column(Boolean, default=True)
    reminder_time = Column(String, default="09:00")  # HH:MM
    timezone = Column(String, default="Europe/Moscow")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user = relationship("User", back_populates="notification_settings") 