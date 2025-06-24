import logging
import os
import redis
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

# Инициализация Redis
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

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

# Клавиатура
def get_reply_markup():
    return ReplyKeyboardMarkup(
        [
            ["Обо мне", "Экстренная помощь"],
            ["Психология", "Питание"],
            ["Фитнес", "Кулинария"],
            ["Завершить сеанс"]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите опцию..."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Инициализация диалога"""
    try:
        await update.message.reply_text(
            "🌹 Добро пожаловать, дорогая! Я - Леди Совершенство Мери П.\n"
            "Ваш персональный эксперт в психологии, питании и фитнесе.\n"
            "Как мне к вам обращаться?",
            reply_markup=get_reply_markup()
        )
        return ASK_NAME
    except Exception as e:
        logger.error(f"Start error: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте /start")
        return ConversationHandler.END

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка имени пользователя"""
    try:
        user_name = update.message.text
        context.user_data['name'] = user_name
        await update.message.reply_text(
            f"🔮 Прекрасное имя, {user_name}! Я готова поделиться с вами всем своим опытом.\n"
            "Что вас интересует в первую очередь?",
            reply_markup=get_reply_markup()
        )
        return CHATTING
    except Exception as e:
        logger.error(f"Name error: {e}")
        await update.message.reply_text("Ошибка обработки имени. Попробуйте /start")
        return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Основной обработчик сообщений"""
    try:
        if 'name' not in context.user_data:
            return await get_name(update, context)
        
        user_input = update.message.text
        name = context.user_data['name']
        cache_key = f"response:{user_input[:50]}"

        # Проверка кэша
        cached_response = r.get(cache_key)
        if cached_response:
            await update.message.reply_text(cached_response, reply_markup=get_reply_markup())
            return CHATTING

        # Обработка специальных команд
        if user_input == "Обо мне":
            response = (
                "👑 Я - Леди Совершенство Мери П.:\n"
                "• 20 лет психологической практики\n"
                "• Автор 5 книг по нутрициологии\n"
                "• Шеф-повар с 32 звёздами Мишлен\n"
                "• Создатель методики 'Фитнес для женщин 40+'\n"
                "Чем могу быть полезной?"
            )
        elif user_input == "Экстренная помощь":
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
            # Запрос к DeepSeek с оптимизацией
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
                "X-Request-Timeout": "15" 
            }
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{name}: {user_input}"}
                ],
                "temperature": 0.7,
                "max_tokens": 300,
                "stream": False  # Для стабильности
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
                
                # Кэшируем ответ на 1 час
                r.setex(cache_key, 3600, response)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"API Request failed: {e}")
                response = "⏳ Произошла задержка в обработке. Пожалуйста, повторите вопрос через минуту."
            except Exception as e:
                logger.error(f"API Processing error: {e}")
                response = "🔧 Временные технические сложности. Попробуйте переформулировать вопрос."

        await update.message.reply_text(response, reply_markup=get_reply_markup())
        return CHATTING

    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        await update.message.reply_text(
            "💔 Произошла непредвиденная ошибка. Пожалуйста, начните заново с /start",
            reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True)
        )
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершение сеанса"""
    try:
        name = context.user_data.get('name', 'уважаемая')
        await update.message.reply_text(
            f"🌸 До новых встреч, {name}! Помните - вы прекрасны!\n"
            "Для нового сеанса нажмите /start",
            reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True)
        )
        context.user_data.clear()
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Cancel error: {e}")
        return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок"""
    logger.error(f"Update {update} caused error: {context.error}")
    try:
        await update.message.reply_text(
            "⚠️ Произошла критическая ошибка. Система автоматически перезагружается...\n"
            "Пожалуйста, начните заново с /start",
            reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True)
        )
    except:
        pass  # Если даже ответить не можем

def main() -> None:
    """Конфигурация и запуск бота"""
    application = Application.builder() \
        .token(TELEGRAM_TOKEN) \
        .read_timeout(40) \
        .write_timeout(40) \
        .pool_timeout(40) \
        .post_init(post_init) \
        .build()

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
    application.add_error_handler(error_handler)

    # Оптимизированный запуск
    try:
        logger.info("Бот Леди Совершенство Мери П. запущен!")
        application.run_polling(
            poll_interval=1.0,
            timeout=30,
            drop_pending_updates=True
        )
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
    finally:
        logger.info("Бот завершил работу")

async def post_init(app: Application):
    """Пост-инициализация"""
    await app.bot.set_my_commands([
        ("start", "Начать консультацию"),
        ("cancel", "Завершить сеанс")
    ])
    logger.info("Команды бота обновлены")

if __name__ == '__main__':
    main()