#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""

import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.init_db import init_db, create_sample_data

def main():
    print("🚀 Инициализация базы данных...")
    
    try:
        # Создаем таблицы
        init_db()
        print("✅ Таблицы созданы!")
        
        # Создаем образцы данных
        print("📝 Создание образцов данных...")
        create_sample_data()
        print("✅ Образцы данных созданы!")
        
        print("\n🎉 База данных успешно инициализирована!")
        print("📁 Файл базы данных: english_school.db")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 