#!/usr/bin/env python3
"""
Запуск бота с обработкой сигналов завершения
"""
import sys
import os
import asyncio
from bot.bot import main

if __name__ == "__main__":
    # Добавляем корневую директорию в PYTHONPATH
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Запускаем основной цикл
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nПрограмма остановлена пользователем (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)