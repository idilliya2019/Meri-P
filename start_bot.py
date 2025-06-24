#!/usr/bin/env python3
"""
Скрипт для безопасного запуска бота Мэри П.
"""

import os
import sys
import subprocess
import time
import signal

def check_python_processes():
    """Проверяет, есть ли уже запущенные процессы Python с нашим ботом"""
    try:
        # На Windows
        if os.name == 'nt':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            if 'python.exe' in result.stdout:
                print("⚠️  Обнаружены запущенные процессы Python")
                return True
        # На Unix-системах
        else:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'lady_perfection_bot.py' in result.stdout:
                print("⚠️  Обнаружен уже запущенный бот")
                return True
    except Exception as e:
        print(f"⚠️  Не удалось проверить процессы: {e}")
    
    return False

def kill_python_processes():
    """Завершает все процессы Python (осторожно!)"""
    try:
        if os.name == 'nt':
            # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                         capture_output=True)
        else:
            # Unix
            subprocess.run(['pkill', '-f', 'lady_perfection_bot.py'], 
                         capture_output=True)
        print("✅ Завершены все процессы Python")
        time.sleep(2)  # Ждем завершения
    except Exception as e:
        print(f"⚠️  Не удалось завершить процессы: {e}")

def main():
    """Основная функция запуска"""
    print("🤖 Запуск бота Мэри П...")
    
    # Проверяем наличие файлов
    required_files = ['lady_perfection_bot.py', 'config.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Файл {file} не найден!")
            return
    
    # Проверяем процессы
    if check_python_processes():
        print("🔄 Завершаю предыдущие процессы...")
        kill_python_processes()
    
    print("🚀 Запускаю бота...")
    
    try:
        # Запускаем бота
        subprocess.run([sys.executable, 'lady_perfection_bot.py'])
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")

if __name__ == "__main__":
    main() 