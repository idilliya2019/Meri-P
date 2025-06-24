import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN

# Настройка подробного логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Простой обработчик голосовых сообщений для тестирования"""
    logger.info(f"=== ПОЛУЧЕНО ГОЛОСОВОЕ СООБЩЕНИЕ ===")
    logger.info(f"Пользователь ID: {update.effective_user.id}")
    logger.info(f"Сообщение ID: {update.message.message_id}")
    logger.info(f"Тип сообщения: {update.message.voice}")
    
    if update.message.voice:
        voice = update.message.voice
        logger.info(f"Длительность: {voice.duration} секунд")
        logger.info(f"Размер файла: {voice.file_size} байт")
        logger.info(f"MIME тип: {voice.mime_type}")
        
        # Отправляем подтверждение
        await update.message.reply_text(
            f"🎤 Получено голосовое сообщение!\n"
            f"Длительность: {voice.duration} сек\n"
            f"Размер: {voice.file_size} байт\n"
            f"Тип: {voice.mime_type}"
        )
    else:
        logger.warning("Голосовое сообщение не содержит данных voice")
        await update.message.reply_text("❌ Ошибка: голосовое сообщение не содержит данных")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    logger.info(f"Получено текстовое сообщение: {update.message.text}")
    await update.message.reply_text("✅ Текстовое сообщение получено!")

def main():
    """Запуск тестового бота"""
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(MessageHandler(filters.VOICE, handle_voice))
        application.add_handler(MessageHandler(filters.TEXT, handle_text))
        
        print("🤖 Тестовый бот запущен!")
        print("📱 Отправьте голосовое сообщение для тестирования")
        print("🛑 Для остановки нажмите Ctrl+C")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main() 