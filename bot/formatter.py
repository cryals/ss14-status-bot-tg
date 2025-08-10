import datetime
import pytz
from typing import Optional, Dict, Any

def format_time(dt: datetime.datetime) -> str:
    """Форматирование времени в 24-часовом формате по МСК (UTC+3)"""
    # Явно указываем часовой пояс МСК
    msk_tz = pytz.timezone("Europe/Moscow")
    dt_msk = dt.astimezone(msk_tz)
    return dt_msk.strftime("%H:%M:%S %d.%m.%Y")

def calculate_round_time(start_time: Optional[str]) -> str:
    """Расчет времени раунда с обработкой разных форматов времени"""
    if not start_time:
        return "В лобби"
    
    try:
        # Удаляем 'Z' в конце, если есть
        clean_time = start_time.rstrip('Z')
        
        # Обрабатываем микросекунды (ограничиваем до 6 цифр)
        if '.' in clean_time:
            base_time, microseconds = clean_time.split('.')
            # Оставляем только первые 6 цифр микросекунд
            microseconds = microseconds[:6].ljust(6, '0')
            clean_time = f"{base_time}.{microseconds}"
        
        # Парсим дату с обработкой разных форматов
        try:
            # Пытаемся распарсить с микросекундами
            start = datetime.datetime.strptime(clean_time, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            try:
                # Пробуем без микросекунд
                start = datetime.datetime.strptime(clean_time, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                # Пробуем другие возможные форматы
                start = datetime.datetime.fromisoformat(clean_time)
        
        # Добавляем информацию о часовом поясе (UTC)
        start = start.replace(tzinfo=datetime.timezone.utc)
        
        now = datetime.datetime.now(datetime.timezone.utc)
        diff = now - start
        
        if diff.total_seconds() < 0:
            return "0 мин"
        
        minutes = int(diff.total_seconds() / 60)
        hours = minutes // 60
        minutes = minutes % 60
        
        if hours > 0:
            return f"{hours}ч {minutes}мин"
        return f"{minutes}мин"
    except Exception as e:
        print(f"⚠️ Ошибка расчета времени раунда: {e}")
        return "Ошибка"

def create_status_message(data: Optional[Dict[str, Any]]) -> str:  # Исправлено: добавлено имя параметра 'data'
    """Создание сообщения статуса"""
    # Уникальный временной штамп для гарантированного обновления
    timestamp = int(datetime.datetime.now().timestamp())
    
    if not data:  # Исправлено: использована переменная data
        return (
            "❌ Ошибка подключения\n"
            "Не удалось получить данные сервера. Проверьте подключение.\n\n"
            f"Обновлено: {format_time(datetime.datetime.now(datetime.timezone.utc))}\n\n"
            f"[Обновление: {timestamp}]"
        )

    round_time = calculate_round_time(data.get("round_start_time"))
    
    return (
        f"**Онлайн:** {data.get('players', 'N/A')}\n"
        f"**Карта:** {data.get('map', 'Неизвестно')}\n"
        f"**Раунд:** {data.get('round_id', 'N/A')}\n"
        f"**Режим:** {data.get('preset', 'N/A')}\n"
        f"**Время от начала смены:** {round_time}\n\n"
        f"Обновлено: {format_time(datetime.datetime.now(datetime.timezone.utc))}\n\n"
        f"[Обновление: {timestamp}]"
    )