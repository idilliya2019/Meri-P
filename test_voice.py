#!/usr/bin/env python3
"""
Тестовый скрипт для диагностики голосовых функций
"""

import speech_recognition as sr
from pydub import AudioSegment
import os

def test_speech_recognition():
    """Тестирует распознавание речи"""
    print("🎤 Тестирование распознавания речи...")
    
    # Создаем тестовый аудиофайл
    test_text = "Привет, это тестовое сообщение"
    
    try:
        # Пытаемся создать тестовый файл
        from gtts import gTTS
        tts = gTTS(text=test_text, lang="ru", slow=False)
        tts.save("test_audio.mp3")
        print("✅ Тестовый аудиофайл создан")
        
        # Конвертируем в wav
        audio = AudioSegment.from_mp3("test_audio.mp3")
        audio.export("test_audio.wav", format="wav")
        print("✅ Конвертация в WAV выполнена")
        
        # Тестируем распознавание
        recognizer = sr.Recognizer()
        with sr.AudioFile("test_audio.wav") as source:
            print("🎧 Загружаю аудиофайл...")
            audio_data = recognizer.record(source)
            print("🎧 Аудио загружено, распознаю речь...")
            
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            print(f"✅ Распознанный текст: '{text}'")
            
            if test_text.lower() in text.lower():
                print("✅ Распознавание работает корректно!")
            else:
                print("⚠️  Распознавание работает, но точность низкая")
                
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        print(f"Тип ошибки: {type(e).__name__}")
        
        # Дополнительная диагностика
        if "ffmpeg" in str(e).lower():
            print("💡 Проблема с ffmpeg. Установите ffmpeg:")
            print("Windows: скачайте с https://ffmpeg.org/download.html")
            print("Или используйте: pip install ffmpeg-python")
        elif "google" in str(e).lower():
            print("💡 Проблема с Google Speech Recognition")
            print("Проверьте интернет-соединение")
        elif "audio" in str(e).lower():
            print("💡 Проблема с аудиофайлом")
            print("Проверьте права доступа к файлам")
    
    finally:
        # Удаляем тестовые файлы
        for file in ["test_audio.mp3", "test_audio.wav"]:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except:
                pass

def test_audio_formats():
    """Тестирует поддержку различных аудиоформатов"""
    print("\n🎵 Тестирование аудиоформатов...")
    
    formats = ['mp3', 'wav', 'ogg', 'm4a']
    
    for format in formats:
        try:
            if format == 'mp3':
                audio = AudioSegment.from_mp3("test_audio.mp3")
            elif format == 'wav':
                audio = AudioSegment.from_wav("test_audio.wav")
            elif format == 'ogg':
                audio = AudioSegment.from_ogg("test_audio.ogg")
            elif format == 'm4a':
                audio = AudioSegment.from_file("test_audio.m4a", format="m4a")
                
            print(f"✅ Формат {format} поддерживается")
        except Exception as e:
            print(f"❌ Формат {format} не поддерживается: {e}")

def check_dependencies():
    """Проверяет установленные зависимости"""
    print("\n📦 Проверка зависимостей...")
    
    dependencies = [
        ('speech_recognition', 'sr'),
        ('pydub', 'AudioSegment'),
        ('gtts', 'gTTS'),
        ('aiohttp', 'aiohttp')
    ]
    
    for package, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {package} установлен")
        except ImportError:
            print(f"❌ {package} не установлен")

if __name__ == "__main__":
    print("🔍 Диагностика голосовых функций")
    print("=" * 50)
    
    check_dependencies()
    test_speech_recognition()
    test_audio_formats()
    
    print("\n💡 Рекомендации:")
    print("1. Убедитесь, что ffmpeg установлен")
    print("2. Проверьте интернет-соединение")
    print("3. Убедитесь, что микрофон работает")
    print("4. Попробуйте говорить четко и громко") 