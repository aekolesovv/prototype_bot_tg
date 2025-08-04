# English School Telegram Bot & Mini App

## Структура проекта

- `bot/` — Telegram-бот на Python (aiogram)
- `backend/` — FastAPI backend (API, логика, интеграции)
- `webapp/` — Мини-приложение на React (Telegram Web App)
- `db/` — Миграции и схемы БД

---

## Быстрый старт

### 1. Настройка окружения

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd english-school-bot

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройка Telegram-бота

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен и настройте переменные окружения:

**Способ 1: Через файл .env (рекомендуется)**
```bash
# Скопируйте шаблон
cp .env.example .env

# Отредактируйте файл .env и добавьте ваш токен
TELEGRAM_BOT_TOKEN=your_bot_token_here
BACKEND_URL=http://localhost:8000/api/v1
```

**Способ 2: Через переменную окружения**
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

### 3. Запуск FastAPI backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу: http://localhost:8000
Документация API: http://localhost:8000/docs

### 4. Запуск Telegram-бота

```bash
python run_bot.py
```

Или напрямую:
```bash
python bot/bot.py
```

### 5. Мини-приложение (webapp)

```bash
cd webapp
npm install
npm start
```

Приложение будет доступно по адресу: http://localhost:3000

---

## Функциональность

### Telegram-бот:
- ✅ Приветствие и выбор уровня обучения
- ✅ Команды: /start, /help, /profile, /schedule, /notifications
- ✅ Кнопки для мини-приложения и связи с преподавателем
- ✅ Интеграция с backend API
- ✅ Обработка всех основных функций
- ✅ Система уведомлений с автоматической отправкой

### Backend API:
- ✅ Расписание занятий (/api/v1/schedule)
- ✅ Профиль пользователя (/api/v1/profile)
- ✅ Клубы (/api/v1/clubs)
- ✅ Тесты (/api/v1/tests)
- ✅ Уроки (/api/v1/lessons)
- ✅ Бронирование занятий (/api/v1/book)
- ✅ Система уведомлений (/api/v1/notifications)
- ✅ CRM/LMS интеграция (/api/v1/crm/*)

### Мини-приложение (webapp):
- ✅ Главное меню с навигацией
- ✅ Расписание занятий
- ✅ Бронирование уроков
- ✅ Элегантная цветовая схема (бордовые, кремовые, нежно-розовые тона)
- ✅ Система уведомлений с настройками
- ✅ Администрирование CRM/LMS
- ⏳ Мини-тесты
- ⏳ Профиль ученика
- ⏳ Клубы (4 вида)

---

## API Endpoints

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/v1/schedule` | GET | Расписание занятий |
| `/api/v1/profile` | GET | Профиль пользователя |
| `/api/v1/clubs` | GET | Список клубов |
| `/api/v1/tests` | GET | Доступные тесты |
| `/api/v1/lessons` | GET | Доступные уроки |
| `/api/v1/book` | POST | Бронирование урока |
| `/api/v1/test` | POST | Отправка результатов теста |
| `/api/v1/notifications` | GET | Получение уведомлений |
| `/api/v1/notifications/settings` | GET/POST | Настройки уведомлений |
| `/api/v1/notifications/send` | POST | Отправка уведомления |
| `/api/v1/crm/status` | GET | Статус CRM/LMS интеграции |
| `/api/v1/crm/configure` | POST | Настройка CRM/LMS |
| `/api/v1/crm/test` | GET | Тест подключения CRM/LMS |
| `/api/v1/crm/sync` | POST | Ручная синхронизация |
| `/api/v1/crm/sync/start` | GET | Запуск автосинхронизации |
| `/api/v1/crm/sync/stop` | GET | Остановка автосинхронизации |

---

## TODO
- [x] Реализовать webapp (React)
- [x] Настроить уведомления
- [x] Добавить интеграцию с CRM/LMS
- [x] Реализовать админ-панель
- [ ] Добавить базу данных
- [ ] Реализовать остальные страницы (клубы, тесты, профиль)
