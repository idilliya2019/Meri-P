#!/usr/bin/env python3
"""
Скрипт для полной остановки всех процессов бота Мэри П.
"""

import os
import subprocess
import time

def stop_all_bot_processes():
    """Останавливает все процессы, связанные с ботом"""
    print("🛑 Останавливаю все процессы бота...")
    
    try:
        # На Windows
        if os.name == 'nt':
            # Останавливаем все процессы python.exe
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                         capture_output=True, text=True)
            print("✅ Завершены все процессы Python")
            
            # Также проверяем процессы python310.exe
            subprocess.run(['taskkill', '/F', '/IM', 'python310.exe'], 
                         capture_output=True, text=True)
            print("✅ Завершены все процессы Python 3.10")
            
        # На Unix-системах
        else:
            # Останавливаем процессы с нашим ботом
            subprocess.run(['pkill', '-f', 'lady_perfection_bot.py'], 
                         capture_output=True, text=True)
            print("✅ Завершены процессы бота")
            
            # Также останавливаем все python процессы (осторожно!)
            subprocess.run(['pkill', '-f', 'python.*lady_perfection'], 
                         capture_output=True, text=True)
            print("✅ Завершены все связанные процессы")
            
    except Exception as e:
        print(f"⚠️  Ошибка при остановке процессов: {e}")
    
    # Ждем завершения
    time.sleep(3)
    print("✅ Все процессы остановлены")

def check_processes():
    """Проверяет, остались ли процессы"""
    try:
        if os.name == 'nt':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            if 'python.exe' in result.stdout:
                print("⚠️  Все еще есть процессы Python")
                return True
            else:
                print("✅ Все процессы Python остановлены")
                return False
        else:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'lady_perfection_bot.py' in result.stdout:
                print("⚠️  Все еще есть процессы бота")
                return True
            else:
                print("✅ Все процессы бота остановлены")
                return False
    except Exception as e:
        print(f"⚠️  Не удалось проверить процессы: {e}")
        return False

def main():
    """Основная функция"""
    print("🛑 Полная остановка бота Мэри П...")
    
    # Останавливаем процессы
    stop_all_bot_processes()
    
    # Проверяем результат
    if check_processes():
        print("⚠️  Некоторые процессы все еще работают")
        print("💡 Попробуйте перезагрузить компьютер")
    else:
        print("✅ Все процессы успешно остановлены")
        print("🚀 Теперь можно запускать бота заново")

if __name__ == "__main__":
    main() 