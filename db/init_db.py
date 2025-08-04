from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from .models import Base, User, Teacher, Lesson, Club, Test, NotificationSettings
import json

def init_db():
    """Создает таблицы в базе данных"""
    Base.metadata.create_all(bind=engine)

def create_sample_data():
    """Создает образцы данных для тестирования"""
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли уже данные
        if db.query(User).first():
            print("База данных уже содержит данные. Пропускаем создание образцов.")
            return
        
        # Создаем преподавателей
        teachers = [
            Teacher(name="Анна Петрова", email="anna@englishschool.com", specialization="beginner"),
            Teacher(name="Михаил Иванов", email="mikhail@englishschool.com", specialization="advanced"),
            Teacher(name="Елена Сидорова", email="elena@englishschool.com", specialization="grammar"),
            Teacher(name="Дмитрий Козлов", email="dmitry@englishschool.com", specialization="speaking")
        ]
        
        for teacher in teachers:
            db.add(teacher)
        db.commit()
        
        # Создаем уроки
        lessons = [
            Lesson(
                title="Английский для начинающих",
                description="Основы грамматики и лексики для начинающих",
                level="beginner",
                duration=60,
                max_students=10,
                teacher_id=1,
                day_of_week="Monday",
                start_time="18:00",
                location="Аудитория 1"
            ),
            Lesson(
                title="Разговорный английский",
                description="Практика разговорной речи",
                level="advanced",
                duration=90,
                max_students=8,
                teacher_id=2,
                day_of_week="Tuesday",
                start_time="19:00",
                location="Аудитория 2"
            ),
            Lesson(
                title="Грамматика английского",
                description="Углубленное изучение грамматики",
                level="beginner",
                duration=60,
                max_students=12,
                teacher_id=3,
                day_of_week="Wednesday",
                start_time="17:30",
                location="Аудитория 1"
            ),
            Lesson(
                title="Бизнес-английский",
                description="Английский для делового общения",
                level="advanced",
                duration=90,
                max_students=6,
                teacher_id=4,
                day_of_week="Thursday",
                start_time="20:00",
                location="Аудитория 3"
            )
        ]
        
        for lesson in lessons:
            db.add(lesson)
        db.commit()
        
        # Создаем клубы
        clubs = [
            Club(
                name="Разговорный клуб",
                description="Практика разговорного английского в неформальной обстановке",
                max_participants=10,
                day_of_week="Friday",
                start_time="19:00",
                duration=90
            ),
            Club(
                name="Клуб чтения",
                description="Чтение и обсуждение книг на английском языке",
                max_participants=8,
                day_of_week="Saturday",
                start_time="15:00",
                duration=120
            ),
            Club(
                name="Клуб кино",
                description="Просмотр и обсуждение фильмов на английском языке",
                max_participants=12,
                day_of_week="Sunday",
                start_time="16:00",
                duration=150
            ),
            Club(
                name="Клуб делового английского",
                description="Бизнес-английский и деловая переписка",
                max_participants=6,
                day_of_week="Thursday",
                start_time="20:00",
                duration=90
            )
        ]
        
        for club in clubs:
            db.add(club)
        db.commit()
        
        # Создаем тесты
        beginner_test_questions = json.dumps([
            {
                "question": "What is the correct form of the verb 'to be' for 'I'?",
                "options": ["am", "is", "are", "be"],
                "correct_answer": 0
            },
            {
                "question": "Which word is a color?",
                "options": ["run", "blue", "fast", "happy"],
                "correct_answer": 1
            },
            {
                "question": "How do you say 'Hello' in English?",
                "options": ["Goodbye", "Hello", "Thank you", "Please"],
                "correct_answer": 1
            }
        ])
        
        advanced_test_questions = json.dumps([
            {
                "question": "Choose the correct form: 'If I ___ rich, I would travel the world.'",
                "options": ["am", "was", "were", "will be"],
                "correct_answer": 2
            },
            {
                "question": "Which sentence is grammatically correct?",
                "options": [
                    "I have been working here since 2 years",
                    "I have been working here for 2 years",
                    "I am working here since 2 years",
                    "I work here since 2 years"
                ],
                "correct_answer": 1
            },
            {
                "question": "What does 'procrastinate' mean?",
                "options": ["To work hard", "To delay or postpone", "To celebrate", "To study"],
                "correct_answer": 1
            }
        ])
        
        tests = [
            Test(
                title="Начальный тест по английскому",
                description="Тест для проверки базовых знаний английского языка",
                level="beginner",
                questions=beginner_test_questions,
                time_limit=15
            ),
            Test(
                title="Продвинутый тест по английскому",
                description="Тест для проверки продвинутых знаний английского языка",
                level="advanced",
                questions=advanced_test_questions,
                time_limit=20
            )
        ]
        
        for test in tests:
            db.add(test)
        db.commit()
        
        print("✅ Образцы данных успешно созданы!")
        
    except Exception as e:
        print(f"❌ Ошибка при создании образцов данных: {e}")
        db.rollback()
    finally:
        db.close()

def create_user_if_not_exists(telegram_id: str, username: str = None, first_name: str = None, last_name: str = None):
    """Создает пользователя, если он не существует"""
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
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
            
            print(f"✅ Создан новый пользователь: {telegram_id}")
            return user
        else:
            print(f"ℹ️ Пользователь уже существует: {telegram_id}")
            return user
            
    except Exception as e:
        print(f"❌ Ошибка при создании пользователя: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Инициализация базы данных...")
    init_db()
    print("✅ Таблицы созданы!")
    
    print("📝 Создание образцов данных...")
    create_sample_data()
    print("✅ Инициализация завершена!") 