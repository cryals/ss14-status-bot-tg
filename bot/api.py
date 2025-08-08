import aiohttp
import asyncio
from typing import Optional, Dict, Any
from .config import STATUS_URL

class ServerAPI:
    """Класс для взаимодействия с API сервера"""
    
    @staticmethod
    async def fetch_server_status() -> Optional[Dict[str, Any]]:
        """Получение статуса сервера"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(STATUS_URL) as response:
                    if response.status == 200:
                        return await response.json()
                    print(f"⚠️ Ошибка получения данных: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"⚠️ Ошибка при получении данных: {e}")
            return None

# Тестовый вызов для проверки API
async def test_api():
    status = await ServerAPI.fetch_server_status()
    if status:
        print("✅ Подключение к API успешно")
        print(f"Пример данных: players={status.get('players')}, map={status.get('map')}")
    else:
        print("❌ Не удалось подключиться к API")

if __name__ == "__main__":
    asyncio.run(test_api())