# Руководство по базе данных

## Обзор

Проект использует SQLite базу данных для хранения всех данных приложения. База данных автоматически создается при первом запуске приложения.

## Структура базы данных

### Таблицы

#### 1. users
Хранит информацию о пользователях Telegram бота.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    telegram_id VARCHAR UNIQUE NOT NULL,
    username VARCHAR,
    first_name VARCHAR,
    last_name VARCHAR,
    level VARCHAR DEFAULT 'beginner',
    progress FLOAT DEFAULT 0.0,
    points INTEGER DEFAULT 0,
    lessons_completed INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

#### 2. teachers
Хранит информацию о преподавателях.

```sql
CREATE TABLE teachers (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR,
    phone VARCHAR,
    specialization VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. lessons
Хранит информацию о занятиях.

```sql
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    level VARCHAR NOT NULL,
    duration INTEGER DEFAULT 60,
    max_students INTEGER DEFAULT 10,
    teacher_id INTEGER REFERENCES teachers(id),
    day_of_week VARCHAR NOT NULL,
    start_time VARCHAR NOT NULL,
    location VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. bookings
Хранит информацию о бронированиях занятий.

```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    lesson_id INTEGER REFERENCES lessons(id),
    booking_date DATETIME NOT NULL,
    status VARCHAR DEFAULT 'confirmed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. clubs
Хранит информацию о клубах.

```sql
CREATE TABLE clubs (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    max_participants INTEGER DEFAULT 10,
    day_of_week VARCHAR NOT NULL,
    start_time VARCHAR NOT NULL,
    duration INTEGER DEFAULT 90,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 6. club_memberships
Хранит информацию о членстве в клубах.

```sql
CREATE TABLE club_memberships (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    club_id INTEGER REFERENCES clubs(id),
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 7. tests
Хранит информацию о тестах.

```sql
CREATE TABLE tests (
    id INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    level VARCHAR NOT NULL,
    questions TEXT NOT NULL, -- JSON строка
    time_limit INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 8. test_results
Хранит результаты тестов пользователей.

```sql
CREATE TABLE test_results (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    test_id INTEGER REFERENCES tests(id),
    score FLOAT NOT NULL,
    answers TEXT NOT NULL, -- JSON строка
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 9. notifications
Хранит уведомления пользователей.

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    scheduled_time DATETIME,
    sent_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 10. notification_settings
Хранит настройки уведомлений пользователей.

```sql
CREATE TABLE notification_settings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    lesson_reminders BOOLEAN DEFAULT TRUE,
    test_notifications BOOLEAN DEFAULT TRUE,
    club_reminders BOOLEAN DEFAULT TRUE,
    daily_motivation BOOLEAN DEFAULT TRUE,
    reminder_time VARCHAR DEFAULT '09:00',
    timezone VARCHAR DEFAULT 'Europe/Moscow',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

## Инициализация базы данных

### Автоматическая инициализация

База данных автоматически создается при запуске FastAPI приложения:

```python
# backend/main.py
@app.on_event("startup")
async def startup_event():
    init_db()
    create_sample_data()
```

### Ручная инициализация

Для ручной инициализации базы данных выполните:

```bash
python init_database.py
```

## Работа с базой данных

### Репозитории

Все операции с базой данных выполняются через репозитории в `db/repositories.py`:

- `UserRepository` - работа с пользователями
- `LessonRepository` - работа с занятиями
- `ClubRepository` - работа с клубами
- `TestRepository` - работа с тестами
- `NotificationRepository` - работа с уведомлениями
- `NotificationSettingsRepository` - работа с настройками уведомлений
- `BookingRepository` - работа с бронированиями

### Примеры использования

#### Создание пользователя

```python
from db.repositories import UserRepository

# Создание нового пользователя
user = UserRepository.create_user(
    telegram_id="123456789",
    username="john_doe",
    first_name="John",
    last_name="Doe"
)
```

#### Получение расписания

```python
from db.repositories import LessonRepository

# Получение расписания для начального уровня
schedule = LessonRepository.get_schedule(level="beginner")
```

#### Присоединение к клубу

```python
from db.repositories import ClubRepository, UserRepository

# Получение пользователя
user = UserRepository.get_by_telegram_id("123456789")

# Присоединение к клубу
success = ClubRepository.join_club(user.id, club_id=1)
```

## Образцы данных

При инициализации базы данных создаются следующие образцы данных:

### Преподаватели
- Анна Петрова (начальный уровень)
- Михаил Иванов (продвинутый уровень)
- Елена Сидорова (грамматика)
- Дмитрий Козлов (разговорная речь)

### Занятия
- Английский для начинающих (Понедельник, 18:00)
- Разговорный английский (Вторник, 19:00)
- Грамматика английского (Среда, 17:30)
- Бизнес-английский (Четверг, 20:00)

### Клубы
- Разговорный клуб (Пятница, 19:00)
- Клуб чтения (Суббота, 15:00)
- Клуб кино (Воскресенье, 16:00)
- Клуб делового английского (Четверг, 20:00)

### Тесты
- Начальный тест по английскому (3 вопроса)
- Продвинутый тест по английскому (3 вопроса)

## Резервное копирование

Для создания резервной копии базы данных:

```bash
cp english_school.db english_school_backup.db
```

Для восстановления из резервной копии:

```bash
cp english_school_backup.db english_school.db
```

## Мониторинг

Для проверки состояния базы данных используйте endpoint:

```
GET /api/v1/health
```

## Миграции

Для управления миграциями используется Alembic. Конфигурация находится в `alembic.ini`.

### Создание миграции

```bash
alembic revision --autogenerate -m "Описание изменений"
```

### Применение миграций

```bash
alembic upgrade head
```

### Откат миграций

```bash
alembic downgrade -1
```

## Безопасность

- Все SQL-запросы используют параметризованные запросы для предотвращения SQL-инъекций
- Доступ к базе данных ограничен через репозитории
- Валидация данных выполняется на уровне Pydantic моделей

## Производительность

- Используются индексы для часто запрашиваемых полей
- Соединения с базой данных закрываются автоматически
- Используется пул соединений для оптимизации производительности 