#!/usr/bin/env python3
"""
Простой тест голосовых функций
"""

import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import os

def test_voice_functions():
    """Тестирует основные голосовые функции"""
    print("🎤 Тест голосовых функций")
    print("=" * 40)
    
    # Тест 1: Создание тестового аудио
    print("1. Создание тестового аудио...")
    try:
        test_text = "Привет, это тестовое сообщение"
        tts = gTTS(text=test_text, lang="ru", slow=False)
        tts.save("test_audio.mp3")
        print("✅ Тестовый аудиофайл создан")
    except Exception as e:
        print(f"❌ Ошибка создания аудио: {e}")
        return
    
    # Тест 2: Конвертация MP3 в WAV
    print("2. Конвертация MP3 в WAV...")
    try:
        audio = AudioSegment.from_mp3("test_audio.mp3")
        audio.export("test_audio.wav", format="wav")
        print("✅ Конвертация выполнена")
    except Exception as e:
        print(f"❌ Ошибка конвертации: {e}")
        return
    
    # Тест 3: Распознавание речи
    print("3. Распознавание речи...")
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile("test_audio.wav") as source:
            print("   Загружаю аудиофайл...")
            audio_data = recognizer.record(source)
            print("   Отправляю на распознавание...")
            
            text = recognizer.recognize_google(audio_data, language="ru-RU")
            print(f"✅ Распознанный текст: '{text}'")
            
            if test_text.lower() in text.lower():
                print("✅ Распознавание работает корректно!")
            else:
                print("⚠️  Распознавание работает, но точность низкая")
                
    except sr.UnknownValueError:
        print("❌ Не удалось распознать речь")
    except sr.RequestError as e:
        print(f"❌ Ошибка сервиса распознавания: {e}")
    except Exception as e:
        print(f"❌ Ошибка распознавания: {e}")
    
    # Очистка
    try:
        os.remove("test_audio.mp3")
        os.remove("test_audio.wav")
        print("✅ Временные файлы удалены")
    except:
        print("⚠️  Не удалось удалить временные файлы")
    
    print("\n🎯 Результат теста:")
    print("Если все этапы прошли успешно, голосовые функции должны работать!")

if __name__ == "__main__":
    test_voice_functions() 