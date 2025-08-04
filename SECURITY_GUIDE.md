# Руководство по безопасности базы данных

## Текущие риски безопасности

### 🔴 Критические риски:

1. **Доступ к файлу базы данных**
   - SQLite файл находится в корне проекта
   - Любой, кто имеет доступ к серверу, может скопировать файл
   - Данные не зашифрованы

2. **Отсутствие аутентификации в API**
   - Все endpoints доступны без авторизации
   - Можно получить доступ к данным любого пользователя

3. **Отсутствие шифрования**
   - Пароли и личные данные хранятся в открытом виде
   - Нет защиты от несанкционированного доступа

## Меры безопасности

### 1. **Аутентификация и авторизация**

#### JWT токены
```python
# backend/auth.py
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
```

#### Защищенные endpoints
```python
@router.get('/profile')
def get_profile(current_user = Depends(get_current_user)):
    # Только авторизованные пользователи
```

### 2. **Защита файла базы данных**

#### Перемещение в безопасную директорию
```bash
# Создайте отдельную директорию для данных
mkdir -p /var/lib/english-school/db
chmod 700 /var/lib/english-school/db
mv english_school.db /var/lib/english-school/db/
```

#### Обновление конфигурации
```python
# db/database.py
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:////var/lib/english-school/db/english_school.db')
```

### 3. **Шифрование данных**

#### Установка SQLCipher
```bash
pip install pysqlcipher3
```

#### Обновление конфигурации с шифрованием
```python
# db/database.py
from pysqlcipher3 import dbapi2 as sqlite

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:////var/lib/english-school/db/english_school.db')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your-database-password')

def get_encrypted_db():
    conn = sqlite.connect('/var/lib/english-school/db/english_school.db')
    conn.execute(f"PRAGMA key='{DB_PASSWORD}'")
    return conn
```

### 4. **Переменные окружения**

#### Создайте файл .env
```bash
# .env
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
DB_PASSWORD=your-database-encryption-password
DATABASE_URL=sqlite:////var/lib/english-school/db/english_school.db
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

#### Загрузите переменные
```python
# backend/main.py
from dotenv import load_dotenv
load_dotenv()
```

### 5. **Ограничение доступа к API**

#### CORS настройки
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-webapp-domain.com"],  # Только ваш домен
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

#### Rate Limiting
```python
# backend/middleware.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get('/api/v1/profile')
@limiter.limit("5/minute")  # Максимум 5 запросов в минуту
def get_profile(request: Request, current_user = Depends(get_current_user)):
    # ...
```

### 6. **Логирование и мониторинг**

#### Настройка логирования
```python
# backend/logging.py
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/english-school/api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_security_event(event_type: str, user_id: str, details: str):
    logger.warning(f"SECURITY: {event_type} - User: {user_id} - {details}")
```

### 7. **Резервное копирование**

#### Автоматические бэкапы
```bash
#!/bin/bash
# backup_db.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/english-school"
mkdir -p $BACKUP_DIR

# Создаем бэкап
cp /var/lib/english-school/db/english_school.db $BACKUP_DIR/english_school_$DATE.db

# Удаляем старые бэкапы (оставляем последние 7 дней)
find $BACKUP_DIR -name "english_school_*.db" -mtime +7 -delete
```

#### Добавьте в crontab
```bash
# crontab -e
0 2 * * * /path/to/backup_db.sh
```

## Рекомендации для продакшена

### 1. **Используйте PostgreSQL вместо SQLite**
```python
# db/database.py
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/english_school')
```

### 2. **Добавьте HTTPS**
```python
# backend/main.py
import ssl

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
```

### 3. **Используйте reverse proxy (Nginx)**
```nginx
# /etc/nginx/sites-available/english-school
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. **Добавьте файрвол**
```bash
# ufw
sudo ufw allow 22/tcp
sudo ufw allow 443/tcp
sudo ufw deny 80/tcp
sudo ufw enable
```

### 5. **Регулярные обновления**
```bash
# Обновляйте зависимости
pip install --upgrade -r requirements.txt

# Проверяйте уязвимости
safety check
```

## Чек-лист безопасности

### ✅ Обязательные меры:
- [ ] Переместить БД в безопасную директорию
- [ ] Настроить JWT аутентификацию
- [ ] Добавить переменные окружения
- [ ] Настроить CORS
- [ ] Добавить rate limiting
- [ ] Настроить логирование
- [ ] Создать бэкапы

### 🔒 Дополнительные меры:
- [ ] Шифрование базы данных
- [ ] HTTPS сертификат
- [ ] Reverse proxy (Nginx)
- [ ] Файрвол
- [ ] Мониторинг безопасности
- [ ] Регулярные обновления

## Экстренные меры

### Если база данных скомпрометирована:

1. **Немедленно остановите сервер**
```bash
sudo systemctl stop english-school-api
```

2. **Смените все пароли и ключи**
```bash
# Обновите JWT_SECRET_KEY
# Обновите DB_PASSWORD
# Обновите TELEGRAM_BOT_TOKEN
```

3. **Восстановите из бэкапа**
```bash
cp /var/backups/english-school/english_school_20240801_020000.db /var/lib/english-school/db/english_school.db
```

4. **Проверьте логи на подозрительную активность**
```bash
grep "SECURITY" /var/log/english-school/api.log
```

5. **Перезапустите сервер**
```bash
sudo systemctl start english-school-api
```

## Заключение

Безопасность базы данных критически важна. Начните с обязательных мер и постепенно добавляйте дополнительные. Регулярно проверяйте безопасность и обновляйте систему. 