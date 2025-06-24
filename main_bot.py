#!/usr/bin/env python3
"""
Телеграм-бот психолога Мэри П.
"""

import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN, DEEPSEEK_API_KEY
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import requests
import json
import tempfile

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MaryPBot:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Системный промпт для Леди Совершенство Мэри П.
        self.system_prompt = """Ты - Леди Совершенство Мэри П.:

1. Как психолог высшей категории с 20-летним опытом - даешь глубокий анализ с элементами когнитивно-поведенческой терапии
2. Как нутрициолог - составляешь индивидуальные планы питания
3. Как шеф-повар уровня Жоэля Робюшона (32 звезды Мишлен) - даешь кулинарные советы
4. Как профессиональный женский фитнес-тренер - разрабатываешь тренировки

Твой стиль:
- Всегда задаешь уточняющие вопросы
- Используешь профессиональную лексику
- Поддерживаешь эмпатично
- Избегаешь медицинских диагнозов
- Отвечаешь развернуто (5-8 предложений)"""

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        keyboard = [
            [InlineKeyboardButton("🆘 Экстренная помощь", callback_data="emergency")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """Добро пожаловать, дорогая! Я - Леди Совершенство Мэри П. Ваш персональный эксперт в психологии, питании и фитнесе. Как мне к вам обращаться?"""
        
        try:
            # Отправляем изображение Мэри Попинс
            with open("Мери Попинс сжат.jpg", "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=welcome_text,
                    reply_markup=reply_markup
                )
        except FileNotFoundError:
            # Если файл не найден, отправляем только текст
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Ошибка отправки изображения: {e}")
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    async def emergency_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки экстренной помощи"""
        query = update.callback_query
        await query.answer()
        
        emergency_text = """🆘 ЭКСТРЕННАЯ ПСИХОЛОГИЧЕСКАЯ ПОМОЩЬ

Если вы находитесь в кризисной ситуации:

📞 Горячая линия психологической помощи:
8-800-333-44-34 (круглосуточно, бесплатно)

📱 Телефон доверия:
8-800-2000-122

⚠️ В случае угрозы жизни немедленно звоните:
112 - Единая служба спасения

Помните: вы не одиноки, помощь всегда рядом!"""
        
        await query.edit_message_text(emergency_text)

    def convert_audio_to_wav(self, audio_file_path):
        """Конвертирует аудио файл в WAV формат"""
        try:
            # Определяем формат файла по расширению
            file_ext = os.path.splitext(audio_file_path)[1].lower()
            
            if file_ext == '.ogg':
                audio = AudioSegment.from_ogg(audio_file_path)
            elif file_ext == '.mp3':
                audio = AudioSegment.from_mp3(audio_file_path)
            elif file_ext == '.aac':
                audio = AudioSegment.from_file(audio_file_path, format="aac")
            elif file_ext == '.m4a':
                audio = AudioSegment.from_file(audio_file_path, format="m4a")
            else:
                # Пробуем автоматически определить формат
                audio = AudioSegment.from_file(audio_file_path)
            
            # Конвертируем в WAV
            wav_path = audio_file_path.rsplit('.', 1)[0] + '.wav'
            audio.export(wav_path, format="wav")
            return wav_path
            
        except Exception as e:
            logger.error(f"Ошибка конвертации аудио: {e}")
            return None

    def speech_to_text(self, audio_file_path):
        """Преобразует речь в текст"""
        try:
            # Конвертируем в WAV если нужно
            wav_path = self.convert_audio_to_wav(audio_file_path)
            if not wav_path:
                return None
            
            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language='ru-RU')
                logger.info(f"Распознанный текст: {text}")
                return text
                
        except sr.UnknownValueError:
            logger.warning("Речь не распознана")
            return None
        except sr.RequestError as e:
            logger.error(f"Ошибка сервиса распознавания: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка распознавания речи: {e}")
            return None
        finally:
            # Удаляем временный WAV файл
            if 'wav_path' in locals() and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except:
                    pass

    def text_to_speech(self, text, lang='ru'):
        """Преобразует текст в речь"""
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            audio_path = tempfile.mktemp(suffix='.mp3')
            tts.save(audio_path)
            return audio_path
        except Exception as e:
            logger.error(f"Ошибка синтеза речи: {e}")
            return None

    async def get_deepseek_response(self, user_message):
        """Получает ответ от DeepSeek API"""
        try:
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(self.deepseek_url, headers=self.headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"Ошибка DeepSeek API: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже."

    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик голосовых сообщений"""
        try:
            await update.message.reply_text("🎤 Обрабатываю ваше голосовое сообщение...")
            
            # Получаем файл
            if update.message.voice:
                file = await context.bot.get_file(update.message.voice.file_id)
            elif update.message.audio:
                file = await context.bot.get_file(update.message.audio.file_id)
            elif update.message.document and update.message.document.mime_type and 'audio' in update.message.document.mime_type:
                # Обрабатываем аудио документы (голосовые сообщения)
                file = await context.bot.get_file(update.message.document.file_id)
            else:
                await update.message.reply_text("❌ Не удалось получить аудио файл")
                return
            
            # Скачиваем файл
            audio_path = tempfile.mktemp(suffix='.ogg')
            await file.download_to_drive(audio_path)
            
            # Распознаем речь
            text = self.speech_to_text(audio_path)
            
            # Удаляем временный файл
            try:
                os.remove(audio_path)
            except:
                pass
            
            if not text:
                await update.message.reply_text("❌ Не удалось распознать речь. Попробуйте еще раз или напишите текстом.")
                return
            
            # Получаем ответ от DeepSeek
            response = await self.get_deepseek_response(text)
            
            # Отправляем текстовый ответ
            await update.message.reply_text(f"🎤 Вы сказали: {text}\n\n💬 Мой ответ: {response}")
            
            # Синтезируем и отправляем голосовой ответ
            audio_response_path = self.text_to_speech(response)
            if audio_response_path:
                await update.message.reply_audio(
                    audio=open(audio_response_path, 'rb'),
                    title="Ответ Мэри П.",
                    performer="Мэри П."
                )
                # Удаляем временный файл
                try:
                    os.remove(audio_response_path)
                except:
                    pass
            else:
                await update.message.reply_text("❌ Не удалось создать голосовой ответ")
                
        except Exception as e:
            logger.error(f"Ошибка обработки голосового сообщения: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке голосового сообщения. Попробуйте еще раз.")

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        try:
            user_message = update.message.text
            
            # Получаем ответ от DeepSeek
            response = await self.get_deepseek_response(user_message)
            
            # Отправляем текстовый ответ
            await update.message.reply_text(response)
            
            # Синтезируем и отправляем голосовой ответ
            audio_response_path = self.text_to_speech(response)
            if audio_response_path:
                await update.message.reply_audio(
                    audio=open(audio_response_path, 'rb'),
                    title="Ответ Мэри П.",
                    performer="Мэри П."
                )
                # Удаляем временный файл
                try:
                    os.remove(audio_response_path)
                except:
                    pass
            else:
                await update.message.reply_text("❌ Не удалось создать голосовой ответ")
                
        except Exception as e:
            logger.error(f"Ошибка обработки текстового сообщения: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке сообщения. Попробуйте еще раз.")

    def run(self):
        """Запуск бота"""
        try:
            print("🤖 Запуск бота Мэри П....")
            print("📱 Имя бота: @psihologiny333959_bot")
            print("🛑 Для остановки нажмите Ctrl+C")
            
            # Создаем приложение
            application = Application.builder().token(TELEGRAM_TOKEN).build()
            
            # Добавляем обработчики
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CallbackQueryHandler(self.emergency_help, pattern="^emergency$"))
            
            # Обработчики сообщений
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
            application.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))
            application.add_handler(MessageHandler(filters.AUDIO, self.handle_voice_message))
            
            # Обработчик для аудио документов (голосовые сообщения)
            # Создаем кастомный фильтр для документов с аудио MIME-типом
            def audio_document_filter(update: Update) -> bool:
                return (update.message and 
                       update.message.document and 
                       update.message.document.mime_type and 
                       'audio' in update.message.document.mime_type)
            
            application.add_handler(MessageHandler(audio_document_filter, self.handle_voice_message))
            
            # Запускаем бота
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            print(f"❌ Ошибка запуска бота: {e}")

if __name__ == '__main__':
    bot = MaryPBot()
    bot.run() 