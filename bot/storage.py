import json
from typing import List, Dict, Any
from .config import STORAGE_PATH

class MessageStorage:
    """Класс для управления хранением сообщений"""
    
    @staticmethod
    def load() -> List[Dict[str, Any]]:
        """Загрузка списка сообщений из файла"""
        try:
            with open(STORAGE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки сообщений: {e}")
            return []
    
    @staticmethod
    def save(messages: List[Dict[str, Any]]) -> None:
        """Сохранение списка сообщений в файл"""
        try:
            with open(STORAGE_PATH, "w", encoding="utf-8") as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения сообщений: {e}")
    
    @staticmethod
    def add_message(chat_id: int, message_id: int) -> None:
        """Добавление нового сообщения в список"""
        messages = MessageStorage.load()
        
        # Проверяем, не существует ли уже такое сообщение
        if not any(m for m in messages if m["chat_id"] == chat_id and m["message_id"] == message_id):
            messages.append({
                "chat_id": chat_id,
                "message_id": message_id
            })
            MessageStorage.save(messages)
            print(f"✅ Добавлено автообновление: чат {chat_id}, сообщение {message_id}")
    
    @staticmethod
    def remove_message(chat_id: int, message_id: int) -> None:
        """Удаление сообщения из списка"""
        messages = MessageStorage.load()
        messages = [m for m in messages if not (m["chat_id"] == chat_id and m["message_id"] == message_id)]
        MessageStorage.save(messages)
        print(f"❌ Удалено автообновление: чат {chat_id}, сообщение {message_id}")