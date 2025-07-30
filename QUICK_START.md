# 🚀 Быстрый запуск

## 1. Активируйте виртуальное окружение
```bash
source venv/bin/activate
```

## 2. Запустите backend
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## 3. Протестируйте API
```bash
python test_bot.py
```

## 4. Запустите бота (требуется токен)
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
python run_bot.py
```

---

## 📋 Что готово

✅ **Telegram-бот:**
- Приветствие и выбор уровня
- Команды /start, /help, /profile, /schedule
- Интеграция с backend API
- Обработка всех кнопок

✅ **Backend API:**
- Расписание занятий
- Профили пользователей
- Клубы (4 вида)
- Тесты и уроки
- Бронирование занятий

⏳ **Мини-приложение (webapp):**
- Следующий этап разработки

---

## 🔗 Полезные ссылки

- API документация: http://localhost:8000/docs
- API статус: http://localhost:8000/ping
- Создать бота: https://t.me/BotFather 