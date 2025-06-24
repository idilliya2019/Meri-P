import logging
import os
import redis
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
import requests
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ключи API
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '7567073966:AAFOGw8-Kr_xrQqmgWTAnkViWNsYVxWmvkQ')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-1aab11faf7be4650b7137960d8f629cd')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Проверка обязательных переменных
if not TELEGRAM_TOKEN:
    raise ValueError("Не задан TELEGRAM_TOKEN в .env файле")
if not DEEPSEEK_API_KEY:
    raise ValueError("Не задан DEEPSEEK_API_KEY в .env файле")

# Инициализация Redis
try:
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=5)
    r.ping()  # Проверка соединения
    logger.info("Успешное подключение к Redis")
except (redis.ConnectionError, redis.TimeoutError) as e:
    logger.warning(f"Ошибка подключения к Redis: {e}. Бот будет работать без кэширования.")
    r = None

# Состояния диалога
ASK_NAME, CHATTING = range(2)

# Системный промт
SYSTEM_PROMPT = """Ты - Леди Совершенство Мери П.:
1. Как психолог высшей категории с 20-летним опытом - даешь глубокий анализ с элементами когнитивно-поведенческой терапии
2. Как нутрициолог - составляешь индивидуальные планы питания
3. Как шеф-повар уровня Жоэля Робюшона (32 звезды Мишлен) - даешь кулинарные советы
4. Как профессиональный женский фитнес-тренер - разрабатываешь тренировки

Твой стиль:
- Всегда задаешь уточняющие вопросы
- Используешь профессиональную лексику
- Поддерживаешь эмпатично
- Избегаешь медицинских диагнозов
- Отвечаешь развернуто (5-8 предложений)
"""

def get_reply_markup():
    """Возвращает клавиатуру с основными опциями"""
    return ReplyKeyboardMarkup(
        [
            ["Экстренная помощь"],
            ["Психология", "Питание"],
            ["Фитнес", "Кулинария"],
            ["Завершить сеанс"]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите опцию..."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start"""
    try:
        await update.message.reply_text(
            "🌹 Добро пожаловать, дорогая! Я - Леди Совершенство Мери П.\n"
            "Ваш персональный эксперт в психологии, питании и фитнесе.\n"
            "Как мне к вам обращаться?",
            reply_markup=get_reply_markup()
        )
        return ASK_NAME
    except Exception as e:
        logger.error(f"Ошибка в start: {e}")
        await update.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка имени пользователя"""
    try:
        user_name = update.message.text.strip()
        if not user_name or len(user_name) > 50:
            await update.message.reply_text(
                "Пожалуйста, введите корректное имя (до 50 символов).",
                reply_markup=get_reply_markup()
            )
            return ASK_NAME
            
        context.user_data['name'] = user_name
        await update.message.reply_text(
            f"🔮 Прекрасное имя, {user_name}! Я готова поделиться с вами всем своим опытом.\n"
            "Что вас интересует в первую очередь?",
            reply_markup=get_reply_markup()
        )
        return CHATTING
    except Exception as e:
        logger.error(f"Ошибка в get_name: {e}")
        await update.message.reply_text(
            "Ошибка обработки имени. Попробуйте /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Основной обработчик сообщений"""
    try:
        if 'name' not in context.user_data:
            return await get_name(update, context)
        
        user_input = update.message.text.strip()
        name = context.user_data['name']
        
        # Проверка кэша
        if r:
            cache_key = f"response:{name}:{user_input[:100]}"
            cached_response = r.get(cache_key)
            if cached_response:
                await update.message.reply_text(cached_response, reply_markup=get_reply_markup())
                return CHATTING

        # Обработка специальных команд
        if user_input == "Экстренная помощь":
            response = (
                "🚨 Экстренная психологическая помощь:\n"
                "• Бесплатный телефон: 8-800-333-44-34\n"
                "• Круглосуточно, анонимно\n"
                "Не оставайтесь наедине с проблемой!"
            )
        elif user_input in ["Психология", "Питание", "Фитнес", "Кулинария"]:
            topics = {
                "Психология": "Какой аспект психологии вас интересует? Семья, карьера или личностный рост?",
                "Питание": "Расскажите о ваших пищевых привычках. Хотите ли вы похудеть, набрать массу или улучшить здоровье?",
                "Фитнес": "Какой у вас текущий уровень подготовки? Какие цели - тонус, похудение или реабилитация?",
                "Кулинария": "Какая кухня вас интересует? Нужен ли рецепт для особого случая или повседневного меню?"
            }
            response = topics[user_input]
        elif user_input == "Завершить сеанс":
            return await cancel(update, context)
        else:
            # Запрос к DeepSeek API
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{name}: {user_input}"}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            try:
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=20
                ).json()
                
                if "choices" in response and response["choices"]:
                    ai_response = response["choices"][0]["message"]["content"]
                    
                    # Кэширование ответа
                    if r:
                        r.setex(cache_key, 3600, ai_response)  # Храним 1 час
                    
                    await update.message.reply_text(ai_response, reply_markup=get_reply_markup())
                    return CHATTING
                else:
                    raise ValueError("Неверный формат ответа от API")
                    
            except Exception as e:
                logger.error(f"Ошибка DeepSeek API: {e}")
                response = "🔧 Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже."

        await update.message.reply_text(response, reply_markup=get_reply_markup())
        return CHATTING

    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        await update.message.reply_text(
            "💔 Произошла непредвиденная ошибка. Пожалуйста, начните заново с /start",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершение сеанса"""
    try:
        name = context.user_data.get('name', 'уважаемая')
        await update.message.reply_text(
            f"🌸 До новых встреч, {name}! Помните - вы прекрасны!\n"
            "Для нового сеанса нажмите /start",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data.clear()
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Ошибка в cancel: {e}")
        return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    try:
        if update.message:
            await update.message.reply_text(
                "⚠️ Произошла критическая ошибка. Пожалуйста, начните заново с /start",
                reply_markup=ReplyKeyboardRemove()
            )
    except Exception:
        pass

async def post_init(app: Application):
    """Пост-инициализация бота"""
    await app.bot.set_my_commands([
        ("start", "Начать консультацию"),
        ("cancel", "Завершить сеанс")
    ])
    logger.info("Команды бота настроены")

def main():
    """Запуск бота"""
    application = Application.builder() \
        .token(TELEGRAM_TOKEN) \
        .read_timeout(30) \
        .write_timeout(30) \
        .post_init(post_init) \
        .build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CHATTING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    logger.info("Бот запускается...")
    application.run_polling(
        poll_interval=1.0,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()