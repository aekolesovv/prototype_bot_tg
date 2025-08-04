from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes_db import router
from db.init_db import init_db, create_sample_data

app = FastAPI(
    title="English School API",
    description="API для школы английского языка",
    version="1.0.0"
)

# Настройка CORS для Telegram Web App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Инициализация базы данных при запуске"""
    print("🚀 Инициализация базы данных...")
    init_db()
    print("✅ База данных готова!")
    
    # Создаем образцы данных только если база пустая
    try:
        create_sample_data()
        print("✅ Образцы данных созданы!")
    except Exception as e:
        print(f"ℹ️ Образцы данных уже существуют: {e}")

@app.get('/ping')
def ping():
    return {'status': 'ok', 'message': 'English School API is running'}

@app.get('/')
def root():
    return {
        'message': 'Welcome to English School API',
        'version': '1.0.0',
        'endpoints': {
            'schedule': '/schedule',
            'profile': '/profile',
            'clubs': '/clubs',
            'tests': '/tests',
            'lessons': '/lessons'
        }
    }

app.include_router(router, prefix="/api/v1")
