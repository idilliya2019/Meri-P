import logging
import json
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from config import TELEGRAM_TOKEN, DEEPSEEK_API_KEY, DEEPSEEK_API_URL, SYSTEM_PROMPT
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import os
from datetime import datetime
from flask import Flask, request

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния разговора
WAITING_NAME = 0

# Константы для callback_data
EMERGENCY_HELP = "emergency_help"
MENU_PSYCHOLOGY = "menu_psychology"
MENU_NUTRITION = "menu_nutrition"
MENU_COOKING = "menu_cooking"
MENU_FITNESS = "menu_fitness"
MENU_STATS = "menu_stats"
MENU_SETTINGS = "menu_settings"

# Flask приложение для webhook
app = Flask(__name__)

# Глобальная переменная для приложения Telegram
telegram_app = None

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
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Ошибка API: {response.status}")
                    return "Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже."
    except Exception as e:
        logger.error(f"Ошибка при обращении к API: {e}")
        return "Извините, произошла техническая ошибка. Попробуйте позже."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало разговора и запрос имени пользователя."""
    try:
        # Отправляем картинку Мэри Попинс
        with open('Мери Попинс сжат.jpg', 'rb') as photo:
            await update.message.reply_photo(photo)
    except FileNotFoundError:
        # Если картинка не найдена, отправляем только текст
        pass
    
    welcome_message = (
        "Добро пожаловать, дорогая! Я - Леди Совершенство Мэри П.\n"
        "Ваш персональный эксперт в психологии, питании и фитнесе.\n"
        "Как мне к вам обращаться?"
    )
    await update.message.reply_text(welcome_message)
    return WAITING_NAME

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка имени пользователя и начало основного диалога."""
    user_name = update.message.text
    context.user_data['name'] = user_name
    context.user_data['messages'] = []
    context.user_data['start_time'] = datetime.now()
    context.user_data['message_count'] = 0
    
    # Создаем основное меню
    keyboard = [
        [InlineKeyboardButton("🧠 Психология", callback_data=MENU_PSYCHOLOGY)],
        [InlineKeyboardButton("🥗 Питание", callback_data=MENU_NUTRITION)],
        [InlineKeyboardButton("👨‍🍳 Кулинария", callback_data=MENU_COOKING)],
        [InlineKeyboardButton("💪 Фитнес", callback_data=MENU_FITNESS)],
        [InlineKeyboardButton("📊 Статистика", callback_data=MENU_STATS)],
        [InlineKeyboardButton("⚙️ Настройки", callback_data=MENU_SETTINGS)],
        [InlineKeyboardButton("🚨 Экстренная помощь", callback_data=EMERGENCY_HELP)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    response = (
        f"Очень приятно познакомиться, {user_name}! Я готова помочь вам в следующих направлениях:\n\n"
        "🧠 Психологические консультации\n"
        "🥗 Индивидуальные планы питания\n"
        "👨‍🍳 Кулинарные советы\n"
        "💪 Персональные тренировки\n\n"
        "Выберите интересующее вас направление или просто напишите мне любой вопрос!"
    )
    await update.message.reply_text(response, reply_markup=reply_markup)
    return ConversationHandler.END

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка выбора пунктов меню."""
    query = update.callback_query
    await query.answer()
    
    if query.data == MENU_PSYCHOLOGY:
        response = (
            "🧠 Психологические консультации\n\n"
            "Я помогу вам с:\n"
            "• Анализом эмоционального состояния\n"
            "• Работой со стрессом и тревожностью\n"
            "• Улучшением отношений\n"
            "• Повышением самооценки\n"
            "• Постановкой целей и их достижением\n\n"
            "Расскажите, что вас беспокоит, и я дам профессиональный совет."
        )
    elif query.data == MENU_NUTRITION:
        response = (
            "🥗 Индивидуальные планы питания\n\n"
            "Я составлю для вас:\n"
            "• Персональный рацион питания\n"
            "• План для похудения или набора веса\n"
            "• Рекомендации по здоровому питанию\n"
            "• Меню с учетом ваших предпочтений\n\n"
            "Расскажите о ваших целях и предпочтениях в еде."
        )
    elif query.data == MENU_COOKING:
        response = (
            "👨‍🍳 Кулинарные советы\n\n"
            "Я поделюсь с вами:\n"
            "• Рецептами вкусных и полезных блюд\n"
            "• Секретами приготовления\n"
            "• Советами по выбору продуктов\n"
            "• Идеями для праздничного меню\n\n"
            "Что бы вы хотели приготовить?"
        )
    elif query.data == MENU_FITNESS:
        response = (
            "💪 Персональные тренировки\n\n"
            "Я разработаю для вас:\n"
            "• Индивидуальную программу тренировок\n"
            "• План для похудения или набора мышечной массы\n"
            "• Упражнения для дома или зала\n"
            "• Рекомендации по восстановлению\n\n"
            "Расскажите о вашем уровне подготовки и целях."
        )
    elif query.data == MENU_STATS:
        user_name = context.user_data.get('name', 'пользователь')
        message_count = context.user_data.get('message_count', 0)
        start_time = context.user_data.get('start_time', datetime.now())
        duration = datetime.now() - start_time
        
        response = (
            f"📊 Статистика для {user_name}\n\n"
            f"💬 Сообщений: {message_count}\n"
            f"⏱️ Время использования: {duration.days} дней, {duration.seconds // 3600} часов\n"
            f"🎯 Направления: Психология, Питание, Кулинария, Фитнес\n\n"
            "Продолжайте общение для получения более подробной статистики!"
        )
    elif query.data == MENU_SETTINGS:
        response = (
            "⚙️ Настройки\n\n"
            "Доступные опции:\n"
            "• Изменить имя\n"
            "• Настройки уведомлений\n"
            "• Сброс статистики\n"
            "• Очистка истории\n\n"
            "Для изменения настроек напишите мне."
        )
    
    # Создаем кнопку возврата в главное меню
    keyboard = [
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
        [InlineKeyboardButton("🚨 Экстренная помощь", callback_data=EMERGENCY_HELP)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(response, reply_markup=reply_markup)

async def handle_emergency_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка нажатия на кнопку экстренной помощи."""
    query = update.callback_query
    await query.answer()
    
    emergency_message = (
        "🚨 Экстренная психологическая помощь\n\n"
        "Если вам нужна срочная психологическая поддержка, вы можете позвонить на бесплатную горячую линию:\n\n"
        "📞 8-800-333-44-34\n\n"
        "Круглосуточно, бесплатно, анонимно.\n"
        "Наши специалисты готовы выслушать и поддержать вас в любое время.\n\n"
        "Также вы можете:\n"
        "• Обратиться к психологу в вашем городе\n"
        "• Поговорить с близкими людьми\n"
        "• Выполнить дыхательные упражнения\n"
        "• Прогуляться на свежем воздухе"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
        [InlineKeyboardButton("💬 Поговорить со мной", callback_data="talk_to_mary")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(emergency_message, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка обычных сообщений с использованием DeepSeek."""
    user_message = update.message.text
    
    # Увеличиваем счетчик сообщений
    context.user_data['message_count'] = context.user_data.get('message_count', 0) + 1
    
    # Добавляем сообщение пользователя в историю
    if 'messages' not in context.user_data:
        context.user_data['messages'] = []
    
    context.user_data['messages'].append({
        "role": "user",
        "content": user_message
    })
    
    # Получаем ответ от DeepSeek
    response = await get_deepseek_response(context.user_data['messages'])
    
    # Добавляем ответ ассистента в историю
    context.user_data['messages'].append({
        "role": "assistant",
        "content": response
    })
    
    # Ограничиваем историю сообщений последними 10 сообщениями
    if len(context.user_data['messages']) > 10:
        context.user_data['messages'] = context.user_data['messages'][-10:]
    
    # Создаем клавиатуру с кнопками
    keyboard = [
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
        [InlineKeyboardButton("🚨 Экстренная помощь", callback_data=EMERGENCY_HELP)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений: распознавание, DeepSeek, синтез ответа."""
    try:
        # Отправляем сообщение о начале обработки
        processing_msg = await update.message.reply_text("🎤 Обрабатываю ваше голосовое сообщение...")
        
        # Получаем файл голосового сообщения
        file = await update.message.voice.get_file()
        ogg_path = f"voice_{update.message.message_id}.ogg"
        wav_path = f"voice_{update.message.message_id}.wav"
        
        # Скачиваем файл
        await file.download_to_drive(ogg_path)
        
        # Конвертация ogg в wav
        try:
            audio = AudioSegment.from_ogg(ogg_path)
            audio.export(wav_path, format="wav")
        except Exception as e:
            logger.error(f"Ошибка конвертации аудио: {e}")
            await processing_msg.edit_text("❌ Ошибка при обработке аудио. Попробуйте отправить сообщение еще раз.")
            return

        # Распознавание речи
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(wav_path) as source:
                # Увеличиваем время ожидания для лучшего распознавания
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
                
                # Пытаемся распознать речь
                text = recognizer.recognize_google(audio_data, language="ru-RU")
                
                if not text.strip():
                    await processing_msg.edit_text("❌ Не удалось распознать речь. Попробуйте говорить четче и громче.")
                    return
                    
                await processing_msg.edit_text(f"🎤 Вы сказали: «{text}»")
                
        except sr.UnknownValueError:
            await processing_msg.edit_text("❌ Не удалось распознать речь. Попробуйте говорить четче и громче.")
            return
        except sr.RequestError as e:
            logger.error(f"Ошибка Google Speech Recognition: {e}")
            await processing_msg.edit_text("❌ Ошибка сервиса распознавания речи. Попробуйте отправить текстовое сообщение.")
            return
        except Exception as e:
            logger.error(f"Ошибка распознавания речи: {e}")
            await processing_msg.edit_text("❌ Ошибка при распознавании речи. Попробуйте еще раз.")
            return

        # Добавляем текст в историю и получаем ответ от DeepSeek
        if 'messages' not in context.user_data:
            context.user_data['messages'] = []
        
        context.user_data['messages'].append({"role": "user", "content": text})
        response = await get_deepseek_response(context.user_data['messages'])
        context.user_data['messages'].append({"role": "assistant", "content": response})
        
        if len(context.user_data['messages']) > 10:
            context.user_data['messages'] = context.user_data['messages'][-10:]

        # Озвучиваем ответ
        try:
            tts = gTTS(text=response, lang="ru", slow=False)
            mp3_path = f"response_{update.message.message_id}.mp3"
            tts.save(mp3_path)
            
            # Отправляем голосовое сообщение
            with open(mp3_path, "rb") as audio_file:
                await update.message.reply_voice(audio_file, caption="🎤 Ответ Мэри П.")
            
            # Удаляем временные файлы
            try:
                os.remove(mp3_path)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Ошибка синтеза речи: {e}")
            # Если синтез речи не работает, отправляем только текст
            await update.message.reply_text("⚠️ Не удалось создать голосовой ответ, но вот текстовый ответ:")

        # Отправляем текстовый ответ с кнопками
        keyboard = [
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
            [InlineKeyboardButton("🚨 Экстренная помощь", callback_data=EMERGENCY_HELP)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response, reply_markup=reply_markup)
        
        # Удаляем временные файлы
        try:
            os.remove(ogg_path)
            os.remove(wav_path)
        except:
            pass
        
    except Exception as e:
        logger.error(f"Общая ошибка при обработке голосового сообщения: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке голосового сообщения.\n"
            "Возможные причины:\n"
            "• Слишком тихая или нечеткая речь\n"
            "• Проблемы с интернет-соединением\n"
            "• Временная недоступность сервисов\n\n"
            "Попробуйте отправить текстовое сообщение или повторите голосовое сообщение."
        )

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка возврата в главное меню."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🧠 Психология", callback_data=MENU_PSYCHOLOGY)],
        [InlineKeyboardButton("🥗 Питание", callback_data=MENU_NUTRITION)],
        [InlineKeyboardButton("👨‍🍳 Кулинария", callback_data=MENU_COOKING)],
        [InlineKeyboardButton("💪 Фитнес", callback_data=MENU_FITNESS)],
        [InlineKeyboardButton("📊 Статистика", callback_data=MENU_STATS)],
        [InlineKeyboardButton("⚙️ Настройки", callback_data=MENU_SETTINGS)],
        [InlineKeyboardButton("🚨 Экстренная помощь", callback_data=EMERGENCY_HELP)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text("🔽 Выберите интересующее вас направление:", reply_markup=reply_markup)

async def handle_talk_to_mary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка кнопки 'Поговорить со мной'."""
    query = update.callback_query
    await query.answer()
    
    response = (
        "Конечно, дорогая! Я всегда готова выслушать и поддержать вас.\n\n"
        "Расскажите мне о том, что вас беспокоит, или задайте любой вопрос. "
        "Я помогу вам разобраться в ситуации и найти решение.\n\n"
        "Просто напишите мне или отправьте голосовое сообщение."
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")],
        [InlineKeyboardButton("🚨 Экстренная помощь", callback_data=EMERGENCY_HELP)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(response, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда помощи."""
    help_text = (
        "🤖 Помощь по использованию Мэри П.\n\n"
        "Доступные команды:\n"
        "/start - Начать разговор\n"
        "/help - Показать эту справку\n"
        "/menu - Главное меню\n"
        "/stats - Ваша статистика\n\n"
        "Возможности:\n"
        "• 💬 Текстовый чат\n"
        "• 🎤 Голосовые сообщения\n"
        "• 🧠 Психологические консультации\n"
        "• 🥗 Планы питания\n"
        "• 👨‍🍳 Кулинарные советы\n"
        "• 💪 Программы тренировок\n"
        "• 🚨 Экстренная помощь\n\n"
        "Просто напишите мне или отправьте голосовое сообщение!"
    )
    await update.message.reply_text(help_text)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда главного меню."""
    keyboard = [
        [InlineKeyboardButton("🧠 Психология", callback_data=MENU_PSYCHOLOGY)],
        [InlineKeyboardButton("🥗 Питание", callback_data=MENU_NUTRITION)],
        [InlineKeyboardButton("👨‍🍳 Кулинария", callback_data=MENU_COOKING)],
        [InlineKeyboardButton("💪 Фитнес", callback_data=MENU_FITNESS)],
        [InlineKeyboardButton("📊 Статистика", callback_data=MENU_STATS)],
        [InlineKeyboardButton("⚙️ Настройки", callback_data=MENU_SETTINGS)],
        [InlineKeyboardButton("🚨 Экстренная помощь", callback_data=EMERGENCY_HELP)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🔽 Выберите интересующее вас направление:", reply_markup=reply_markup)

# Webhook endpoint для Flask
@app.route('/webhook', methods=['POST'])
async def webhook():
    """Webhook endpoint для получения обновлений от Telegram"""
    if request.method == 'POST':
        update = Update.de_json(request.get_json(), telegram_app.bot)
        await telegram_app.process_update(update)
        return 'ok'
    return 'ok'

def main() -> None:
    """Запуск бота с webhook."""
    global telegram_app
    
    try:
        # Создаем приложение
        telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

        # Создаем обработчик разговора
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                WAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            },
            fallbacks=[],
        )

        # Добавляем обработчики
        telegram_app.add_handler(conv_handler)
        telegram_app.add_handler(CommandHandler('help', help_command))
        telegram_app.add_handler(CommandHandler('menu', menu_command))
        telegram_app.add_handler(CallbackQueryHandler(handle_menu_selection, pattern=f"^({MENU_PSYCHOLOGY}|{MENU_NUTRITION}|{MENU_COOKING}|{MENU_FITNESS}|{MENU_STATS}|{MENU_SETTINGS})$"))
        telegram_app.add_handler(CallbackQueryHandler(handle_emergency_help, pattern=f"^{EMERGENCY_HELP}$"))
        telegram_app.add_handler(MessageHandler(filters.VOICE, handle_voice))
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        telegram_app.add_handler(CallbackQueryHandler(handle_main_menu, pattern="^main_menu$"))
        telegram_app.add_handler(CallbackQueryHandler(handle_talk_to_mary, pattern="^talk_to_mary$"))

        print("🤖 Запуск бота Мэри П с webhook...")
        print("✅ Бот готов к работе!")
        print("📱 Найдите бота в Telegram и нажмите /start")
        print("🛑 Для остановки нажмите Ctrl+C")
        
        # Запускаем webhook
        telegram_app.run_webhook(
            listen='0.0.0.0',
            port=8443,
            url_path=TELEGRAM_TOKEN,
            webhook_url=f'https://your-domain.com/{TELEGRAM_TOKEN}'
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        print("💡 Попробуйте перезапустить бота через несколько секунд")

if __name__ == '__main__':
    main() 