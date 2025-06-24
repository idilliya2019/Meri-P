#!/usr/bin/env python3
"""
Максимально простой бот для тестирования
"""

import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех сообщений"""
    logger.info(f"=== ПОЛУЧЕНО СООБЩЕНИЕ ===")
    logger.info(f"Тип сообщения: {update.message}")
    logger.info(f"Пользователь: {update.effective_user.id} - {update.effective_user.first_name}")
    logger.info(f"Сообщение ID: {update.message.message_id}")
    
    if update.message.text:
        logger.info(f"Текст: {update.message.text}")
        await update.message.reply_text(f"✅ Получено текстовое сообщение: {update.message.text}")
    
    elif update.message.voice:
        logger.info(f"Голосовое сообщение: {update.message.voice}")
        await update.message.reply_text("🎤 Получено голосовое сообщение!")
    
    elif update.message.audio:
        logger.info(f"Аудио сообщение: {update.message.audio}")
        await update.message.reply_text("🎵 Получено аудио сообщение!")
    
    else:
        logger.info(f"Другой тип сообщения: {type(update.message)}")
        await update.message.reply_text("📎 Получено сообщение другого типа!")

def main():
    """Запуск простого бота"""
    try:
        print("🤖 Запуск простого тестового бота...")
        print(f"📱 Имя бота: @psihologiny333959_bot")
        print("📝 Отправьте любое сообщение для тестирования")
        print("🛑 Для остановки нажмите Ctrl+C")
        
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем обработчик всех сообщений
        application.add_handler(MessageHandler(filters.ALL, handle_all_messages))
        
        # Запускаем бота
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main() 