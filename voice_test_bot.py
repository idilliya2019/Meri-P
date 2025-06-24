#!/usr/bin/env python3
"""
Бот для тестирования голосовых сообщений
"""

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

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    logger.info(f"=== ТЕКСТОВОЕ СООБЩЕНИЕ ===")
    logger.info(f"Пользователь: {update.effective_user.first_name}")
    logger.info(f"Текст: {update.message.text}")
    await update.message.reply_text(f"✅ Текст получен: {update.message.text}")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик голосовых сообщений"""
    logger.info(f"=== ГОЛОСОВОЕ СООБЩЕНИЕ ===")
    logger.info(f"Пользователь: {update.effective_user.first_name}")
    
    if update.message.voice:
        voice = update.message.voice
        logger.info(f"Длительность: {voice.duration} сек")
        logger.info(f"Размер: {voice.file_size} байт")
        logger.info(f"MIME тип: {voice.mime_type}")
        logger.info(f"File ID: {voice.file_id}")
        
        await update.message.reply_text(
            f"🎤 Голосовое сообщение получено!\n"
            f"Длительность: {voice.duration} сек\n"
            f"Размер: {voice.file_size} байт\n"
            f"Тип: {voice.mime_type}"
        )
    else:
        logger.warning("Голосовое сообщение не содержит данных voice")
        await update.message.reply_text("❌ Ошибка: нет данных голосового сообщения")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик аудио сообщений"""
    logger.info(f"=== АУДИО СООБЩЕНИЕ ===")
    logger.info(f"Пользователь: {update.effective_user.first_name}")
    
    if update.message.audio:
        audio = update.message.audio
        logger.info(f"Название: {audio.title}")
        logger.info(f"Исполнитель: {audio.performer}")
        logger.info(f"Длительность: {audio.duration} сек")
        logger.info(f"Размер: {audio.file_size} байт")
        logger.info(f"MIME тип: {audio.mime_type}")
        
        await update.message.reply_text(
            f"🎵 Аудио файл получен!\n"
            f"Название: {audio.title or 'Не указано'}\n"
            f"Исполнитель: {audio.performer or 'Не указано'}\n"
            f"Длительность: {audio.duration} сек"
        )
    else:
        logger.warning("Аудио сообщение не содержит данных audio")
        await update.message.reply_text("❌ Ошибка: нет данных аудио файла")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик документов"""
    logger.info(f"=== ДОКУМЕНТ ===")
    logger.info(f"Пользователь: {update.effective_user.first_name}")
    
    if update.message.document:
        doc = update.message.document
        logger.info(f"Имя файла: {doc.file_name}")
        logger.info(f"Размер: {doc.file_size} байт")
        logger.info(f"MIME тип: {doc.mime_type}")
        
        await update.message.reply_text(
            f"📎 Документ получен!\n"
            f"Имя: {doc.file_name}\n"
            f"Размер: {doc.file_size} байт\n"
            f"Тип: {doc.mime_type}"
        )

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех сообщений для диагностики"""
    logger.info(f"=== ДИАГНОСТИКА СООБЩЕНИЯ ===")
    logger.info(f"Пользователь: {update.effective_user.first_name}")
    logger.info(f"Тип сообщения: {type(update.message)}")
    
    # Проверяем все возможные типы
    message_types = []
    if update.message.text: 
        message_types.append("text")
        logger.info(f"Текст: {update.message.text}")
    if update.message.voice: 
        message_types.append("voice")
        logger.info(f"Voice: {update.message.voice}")
    if update.message.audio: 
        message_types.append("audio")
        logger.info(f"Audio: {update.message.audio}")
    if update.message.document: 
        message_types.append("document")
        logger.info(f"Document: {update.message.document}")
    if update.message.photo: 
        message_types.append("photo")
        logger.info(f"Photo: {update.message.photo}")
    if update.message.video: 
        message_types.append("video")
        logger.info(f"Video: {update.message.video}")
    if update.message.sticker: 
        message_types.append("sticker")
        logger.info(f"Sticker: {update.message.sticker}")
    if update.message.animation: 
        message_types.append("animation")
        logger.info(f"Animation: {update.message.animation}")
    
    logger.info(f"Найденные типы: {message_types}")
    
    # Отправляем ответ в зависимости от типа
    if "text" in message_types:
        await update.message.reply_text(f"✅ Текст получен: {update.message.text}")
    elif "voice" in message_types:
        voice = update.message.voice
        await update.message.reply_text(
            f"🎤 Голосовое сообщение получено!\n"
            f"Длительность: {voice.duration} сек\n"
            f"Размер: {voice.file_size} байт\n"
            f"Тип: {voice.mime_type}"
        )
    elif "audio" in message_types:
        audio = update.message.audio
        await update.message.reply_text(
            f"🎵 Аудио файл получен!\n"
            f"Название: {audio.title or 'Не указано'}\n"
            f"Исполнитель: {audio.performer or 'Не указано'}\n"
            f"Длительность: {audio.duration} сек"
        )
    else:
        await update.message.reply_text(f"📎 Сообщение получено. Типы: {message_types}")

def main():
    """Запуск бота для тестирования голосовых сообщений"""
    try:
        print("🤖 Запуск бота для тестирования голосовых сообщений...")
        print("📱 Имя бота: @psihologiny333959_bot")
        print("🎤 Отправьте голосовое сообщение для тестирования")
        print("📝 Отправьте текстовое сообщение для сравнения")
        print("🛑 Для остановки нажмите Ctrl+C")
        
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем один универсальный обработчик для всех сообщений
        application.add_handler(MessageHandler(filters.ALL, handle_all_messages))
        
        # Запускаем бота
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main() 