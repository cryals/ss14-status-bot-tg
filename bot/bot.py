import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats
from .config import BOT_TOKEN, UPDATE_INTERVAL
from .storage import MessageStorage
from .formatter import create_status_message
from .api import ServerAPI

class StatusBot:
    """Основной класс бота"""
    
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher()
        self.update_task = None
        self.last_status_hash = None  # Для отслеживания изменений
        self.update_interval = UPDATE_INTERVAL  # Делаем интервал обновления динамическим
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_status, Command("status"))
        self.dp.message.register(self.cmd_sendstatus, Command("sendstatus"))
    
    async def cmd_start(self, message: Message):
        """Обработка команды /start"""
        await message.answer(
            "🤖 Привет! Я бот для отслеживания статуса сервера.\n\n"
            "Доступные команды:\n"
            "/status - показать текущий статус\n"
            "/sendstatus - запустить автообновление статуса в этом чате"
        )
    
    async def cmd_status(self, message: Message):
        """Обработка команды /status"""
        # Используем правильный метод для отправки chat action
        await self.bot.send_chat_action(message.chat.id, "typing")
        status_data = await ServerAPI.fetch_server_status()
        status_msg = create_status_message(status_data)
        await message.answer(
            status_msg,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    
    async def cmd_sendstatus(self, message: Message):
        """Обработка команды /sendstatus"""
        # Проверка прав администратора для групп
        if message.chat.type != "private" and not await self.is_admin(message):
            await message.answer("❌ Эта команда доступна только администраторам!")
            return
        
        # Используем правильный метод для отправки chat action
        await self.bot.send_chat_action(message.chat.id, "typing")
        status_data = await ServerAPI.fetch_server_status()
        status_msg = create_status_message(status_data)
        
        try:
            sent_message = await message.answer(
                status_msg,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            
            # Сохраняем сообщение для автообновления
            MessageStorage.add_message(message.chat.id, sent_message.message_id)
            
            await message.answer(
                "✅ Автообновление запущено в этом чате!",
                reply_to_message_id=sent_message.message_id
            )
        except Exception as e:
            print(f"⚠️ Ошибка отправки статуса: {e}")
            await message.answer("❌ Произошла ошибка при отправке сообщения!")
    
    async def is_admin(self, message: Message) -> bool:
        """Проверка прав администратора в группе"""
        if message.chat.type == "private":
            return True
        
        try:
            chat_member = await self.bot.get_chat_member(message.chat.id, message.from_user.id)
            return chat_member.status in ("administrator", "creator")
        except Exception as e:
            print(f"⚠️ Ошибка проверки прав администратора: {e}")
            return False
    
    async def update_status_messages(self):
        """Функция обновления сообщений"""
        try:
            status_data = await ServerAPI.fetch_server_status()
            
            # Создаем хеш от данных для сравнения
            current_hash = hash(str(status_data))
            
            # Проверяем, изменились ли данные
            if current_hash == self.last_status_hash:
                return  # Не обновляем, если данные не изменились
            
            self.last_status_hash = current_hash
            status_msg = create_status_message(status_data)
            messages = MessageStorage.load()
            
            if not messages:
                return
            
            for msg in messages[:]:  # Используем копию списка для безопасного удаления
                chat_id = msg["chat_id"]
                message_id = msg["message_id"]
                
                try:
                    await self.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=status_msg,
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
                    logging.info(f"✓ Сообщение {message_id} в чате {chat_id} успешно обновлено")
                except Exception as e:
                    error_msg = str(e).lower()
                    logging.error(f"⚠️ Ошибка обновления сообщения {message_id}: {e}")
                    
                    # Игнорируем ошибку, если сообщение не изменилось
                    if "message is not modified" in error_msg:
                        logging.info(f"- Содержимое сообщения не изменилось, пропускаем")
                        continue
                    
                    # Обработка flood control
                    if "flood control" in error_msg or "retry after" in error_msg:
                        # Извлекаем время задержки из сообщения об ошибке
                        match = re.search(r'retry after (\d+)', error_msg)
                        if match:
                            retry_after = int(match.group(1))
                            logging.warning(f"⚠️ Flood control активирован, увеличиваем интервал обновления до {retry_after} секунд")
                            # Увеличиваем интервал обновления
                            self.update_interval = max(self.update_interval, retry_after)
                        continue
                    
                    # Удаляем сообщение из списка при реальных ошибках
                    MessageStorage.remove_message(chat_id, message_id)
        except Exception as e:
            logging.error(f"⚠️ Критическая ошибка в update_status_messages: {e}")
    
    async def status_update_loop(self):
        """Цикл периодического обновления статуса"""
        logging.info(f"Автообновление запущено (проверка каждые {self.update_interval} секунд)")
        
        while True:
            try:
                await self.update_status_messages()
            except Exception as e:
                logging.error(f"⚠️ Ошибка в цикле обновления: {e}")
            
            # Используем динамический интервал
            logging.info(f"Следующее обновление через {self.update_interval} секунд")
            await asyncio.sleep(self.update_interval)
    
    async def set_bot_commands(self):
        """Установка команд бота"""
        private_commands = [
            BotCommand(command="start", description="Запустить бота"),
            BotCommand(command="status", description="Показать текущий статус"),
            BotCommand(command="sendstatus", description="Запустить автообновление"),
        ]
        
        group_commands = [
            BotCommand(command="status", description="Показать текущий статус"),
            BotCommand(command="sendstatus", description="Запустить автообновление (только администраторы)"),
        ]
        
        await self.bot.set_my_commands(
            commands=private_commands,
            scope=BotCommandScopeAllPrivateChats()
        )
        await self.bot.set_my_commands(
            commands=group_commands,
            scope=BotCommandScopeAllGroupChats()
        )
        logging.info("✅ Команды бота установлены")
    
    async def start(self):
        """Запуск бота"""
        logging.info("Запуск бота...")
        
        # Установка команд
        await self.set_bot_commands()
        
        # Запуск фоновой задачи обновления
        self.update_task = asyncio.create_task(self.status_update_loop())
        
        # Сразу обновляем статус
        await self.update_status_messages()
        
        # Запуск обработки сообщений
        logging.info("✅ Бот готов к работе!")
        await self.dp.start_polling(self.bot)
    
    async def stop(self):
        """Остановка бота"""
        logging.info("\nОстановка бота...")
        if self.update_task:
            self.update_task.cancel()
        await self.bot.session.close()
        logging.info("✅ Бот остановлен")

async def main():
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    bot = StatusBot()
    try:
        await bot.start()
    except (KeyboardInterrupt, SystemExit):
        await bot.stop()
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("\nПрограмма остановлена пользователем")