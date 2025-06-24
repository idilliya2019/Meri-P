import speech_recognition as sr
import pyttsx3
import sounddevice as sd
import numpy as np
import queue
import threading
import time
import aiohttp
import asyncio
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, SYSTEM_PROMPT

class VoiceAssistant:
    def __init__(self):
        # Инициализация распознавателя речи
        self.recognizer = sr.Recognizer()
        
        # Инициализация синтезатора речи
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Скорость речи
        self.engine.setProperty('volume', 1.0)  # Громкость
        
        # Очередь для аудио
        self.audio_queue = queue.Queue()
        
        # Флаг для отслеживания состояния записи
        self.is_recording = False
        
        # История сообщений для контекста
        self.messages = []

    async def get_deepseek_response(self, text):
        """Получение ответа от DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Добавляем сообщение пользователя в историю
        self.messages.append({"role": "user", "content": text})
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                *self.messages
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result["choices"][0]["message"]["content"]
                    # Добавляем ответ ассистента в историю
                    self.messages.append({"role": "assistant", "content": response_text})
                    # Ограничиваем историю последними 10 сообщениями
                    if len(self.messages) > 10:
                        self.messages = self.messages[-10:]
                    return response_text
                else:
                    return "Извините, произошла ошибка при обработке вашего запроса."

    def speak(self, text):
        """Озвучивание текста"""
        self.engine.say(text)
        self.engine.runAndWait()

    def audio_callback(self, indata, frames, time, status):
        """Callback для записи аудио"""
        if status:
            print(status)
        self.audio_queue.put(indata.copy())

    def start_listening(self):
        """Начало прослушивания микрофона"""
        self.is_recording = True
        with sd.InputStream(callback=self.audio_callback,
                          channels=1,
                          samplerate=16000,
                          dtype=np.int16):
            print("Слушаю... (нажмите Ctrl+C для остановки)")
            while self.is_recording:
                time.sleep(0.1)

    def process_audio(self):
        """Обработка записанного аудио"""
        audio_data = np.concatenate(list(self.audio_queue.queue))
        self.audio_queue.queue.clear()
        
        # Сохраняем аудио во временный файл
        import wave
        with wave.open('temp.wav', 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data.tobytes())
        
        # Распознаем речь
        with sr.AudioFile('temp.wav') as source:
            audio = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                print(f"Вы сказали: {text}")
                return text
            except sr.UnknownValueError:
                print("Не удалось распознать речь")
                return None
            except sr.RequestError as e:
                print(f"Ошибка сервиса распознавания речи: {e}")
                return None

    async def run(self):
        """Основной цикл работы ассистента"""
        print("Привет! Я Мэри П., ваш голосовой ассистент.")
        print("Говорите, когда будете готовы (нажмите Ctrl+C для выхода)")
        
        while True:
            try:
                # Начинаем запись
                self.is_recording = True
                recording_thread = threading.Thread(target=self.start_listening)
                recording_thread.start()
                
                # Ждем 5 секунд записи
                time.sleep(5)
                self.is_recording = False
                recording_thread.join()
                
                # Обрабатываем записанное аудио
                text = self.process_audio()
                if text:
                    # Получаем ответ от DeepSeek
                    response = await self.get_deepseek_response(text)
                    print(f"Мэри П.: {response}")
                    # Озвучиваем ответ
                    self.speak(response)
                
            except KeyboardInterrupt:
                print("\nДо свидания!")
                break
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                continue

if __name__ == "__main__":
    assistant = VoiceAssistant()
    asyncio.run(assistant.run()) 