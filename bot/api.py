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