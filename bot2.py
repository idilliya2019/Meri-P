import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
import requests

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ключи API
TELEGRAM_TOKEN = "7567073966:AAFOGw8-Kr_xrQqmgWTAnkViWNsYVxWmvkQ"
DEEPSEEK_API_KEY = "sk-1aab11faf7be4650b7137960d8f629cd"

# Состояния диалога
ASK_NAME, CHATTING = range(2)

# Клавиатура
def get_reply_markup():
    return ReplyKeyboardMarkup(
        [
            ["О себе", "Помощь"],
            ["Совет", "Мотивация"],
            ["Завершить"]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начинаем диалог, спрашиваем имя"""
    await update.message.reply_text(
        "Привет, дорогая! Я Маша - твой виртуальный помощник.\n"
        "Как мне к тебе обращаться?",
        reply_markup=get_reply_markup()
    )
    return ASK_NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем имя пользователя"""
    user_name = update.message.text
    context.user_data['name'] = user_name
    await update.message.reply_text(
        f"Очень приятно, {user_name}! 💖\n"
        "Чем могу помочь?",
        reply_markup=get_reply_markup()
    )
    return CHATTING

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка всех текстовых сообщений"""
    if 'name' not in context.user_data:
        return await get_name(update, context)
    
    user_input = update.message.text
    name = context.user_data['name']

    # Обработка специальных команд
    if user_input == "О себе":
        response = (
            "Я Маша - твой виртуальный помощник! 💁‍♀️\n"
            "Могу помочь с:\n"
            "- Психологическими вопросами\n"
            "- Питанием и рецептами\n"
            "- Фитнес-советами\n"
            "Спрашивай о чем угодно!"
        )
    elif user_input == "Помощь":
        response = "Просто напиши мне о том, что тебя волнует, и я постараюсь помочь!"
    elif user_input == "Совет":
        response = "Совет на сегодня: выдели время для себя! Даже 15 минут в день могут изменить твое настроение. 🌸"
    elif user_input == "Мотивация":
        response = "Ты сильнее, чем думаешь! Помни - каждый день - это новый шанс. 💪"
    elif user_input == "Завершить":
        return await cancel(update, context)
    else:
        # Запрос к DeepSeek для обычных сообщений
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты - женский бот Маша. Отвечай как психолог, нутрициолог и тренер. "
                    "Будь дружелюбной, используй эмодзи. Избегай запрещенных тем. "
                    "Отвечай развернуто (3-5 предложений)."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            "temperature": 0.7
        }
        
        try:
            api_response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            api_response.raise_for_status()
            response = api_response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"API Error: {e}")
            response = "Ой, что-то я растерялась... Давай попробуем еще раз? 💫"

    await update.message.reply_text(response, reply_markup=get_reply_markup())
    return CHATTING

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершение диалога"""
    name = context.user_data.get('name', 'дорогая')
    await update.message.reply_text(
        f"До новых встреч, {name}! Напиши /start когда захочешь продолжить.",
        reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True)
    )
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    """Запуск бота"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Обработчики
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CHATTING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    
    # Обработка неизвестных команд
    application.add_handler(MessageHandler(filters.ALL, handle_message))
    
    try:
        logger.info("Бот запущен и работает...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        logger.info("Бот остановлен")

if __name__ == '__main__':
    main()