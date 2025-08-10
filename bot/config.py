import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Определяем базовую директорию проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Получаем токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в .env файле")

# URL для получения статуса сервера
STATUS_URL = os.getenv("STATUS_URL", "http://85.192.49.3:1212/status")

# Интервал обновления в секундах (по умолчанию 30 секунд)
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "30"))

# Путь к файлу хранения сообщений
STORAGE_PATH = BASE_DIR / "status_messages.json"

# Создаем файл хранения, если его нет
if not STORAGE_PATH.exists():
    STORAGE_PATH.write_text("[]", encoding="utf-8")
    print(f"✅ Создан файл хранения сообщений: {STORAGE_PATH}")