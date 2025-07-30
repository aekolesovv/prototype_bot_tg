# English School Telegram Bot & Mini App

## Структура проекта

- `bot/` — Telegram-бот на Python (aiogram)
- `backend/` — FastAPI backend (API, логика, интеграции)
- `webapp/` — Мини-приложение на React (Telegram Web App)
- `db/` — Миграции и схемы БД

---

## Быстрый старт

### 1. Клонируйте репозиторий и создайте виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Запуск Telegram-бота

- Укажите токен бота в переменной окружения `TELEGRAM_BOT_TOKEN` или замените в `bot/bot.py`.
- Запустите:

```bash
python bot/bot.py
```

### 3. Запуск FastAPI backend

```bash
uvicorn backend.main:app --reload
```

### 4. Мини-приложение (webapp)

- Реализуется на React (создайте через create-react-app или Vite).
- Подключите Telegram Web Apps SDK.

---

## Описание

Бот и мини-приложение для школы английского языка:
- Запись на занятия, расписание, мини-уроки, напоминания, связь с преподавателем.
- 4 вида клубов (динамически управляются админом).
- Мини-приложение: светлый минималистичный дизайн, кэширование, адаптивность.
- Интеграция с внешними CRM/LMS через API.

---

## TODO
- [ ] Реализовать webapp (React)
- [ ] Добавить интеграцию с CRM/LMS
- [ ] Реализовать админ-панель 