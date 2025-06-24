import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config import TELEGRAM_TOKEN, DEEPSEEK_API_KEY, DEEPSEEK_API_URL, SYSTEM_PROMPT
import aiohttp
import json

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы для callback_data
EMERGENCY_HELP = "emergency_help"

async def get_deepseek_response(messages):
    """Получение ответа от DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(DEEPSEEK_API_URL, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"Ошибка API: {response.status}")
                return "Извините, произошла ошибка при обработке вашего запроса."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало разговора"""
    welcome_message = (
        "Добро пожаловать, дорогая! Я - Леди Совершенство Мэри П.\n"
        "Ваш персональный эксперт в психологии, питании и фитнесе.\n\n"
        "Для начала голосового разговора нажмите кнопку 'Позвонить' ниже."
    )
    
    # Создаем клавиатуру с кнопкой звонка
    keyboard = [
        [InlineKeyboardButton("📞 Позвонить", callback_data="start_call")],
        [InlineKeyboardButton("🚨 Экстренная помощь", callback_data=EMERGENCY_HELP)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def handle_call_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатия на кнопку звонка"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_call":
        # Инициируем звонок
        await context.bot.send_voice_chat_action(
            chat_id=query.message.chat_id,
            action="record_audio"
        )
        
        # Отправляем сообщение о начале звонка
        await query.message.reply_text(
            "Начинаю звонок... Пожалуйста, говорите после звукового сигнала."
        )
        
        # Здесь будет логика обработки звонка
        # В реальном приложении нужно использовать Telegram Voice Chat API

async def handle_emergency_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатия на кнопку экстренной помощи"""
    query = update.callback_query
    await query.answer()
    
    emergency_message = (
        "🚨 Экстренная психологическая помощь\n\n"
        "Если вам нужна срочная психологическая поддержка, вы можете позвонить на бесплатную горячую линию:\n\n"
        "📞 8-800-333-44-34\n\n"
        "Круглосуточно, бесплатно, анонимно.\n"
        "Наши специалисты готовы выслушать и поддержать вас в любое время."
    )
    
    await query.message.reply_text(emergency_message)

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений"""
    # Получаем голосовое сообщение
    voice = await update.message.voice.get_file()
    
    # Скачиваем файл
    voice_file = await voice.download_to_drive()
    
    # Здесь будет логика распознавания речи
    # В реальном приложении нужно использовать Speech-to-Text API
    
    # Получаем ответ от DeepSeek
    response = await get_deepseek_response([{"role": "user", "content": "Распознанный текст"}])
    
    # Отправляем ответ голосовым сообщением
    await update.message.reply_voice(
        voice=open("response.mp3", "rb"),
        caption=response
    )

def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_call_button, pattern="^start_call$"))
    application.add_handler(CallbackQueryHandler(handle_emergency_help, pattern=f"^{EMERGENCY_HELP}$"))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main() 