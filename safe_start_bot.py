#!/usr/bin/env python3
"""
Безопасный запуск бота Мэри П. с проверкой процессов
"""

import os
import subprocess
import time
import sys
import signal

def check_python_version():
    """Проверяет версию Python"""
    version = sys.version_info
    if version.major == 3 and version.minor in [10, 11]:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - подходящая версия")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - несовместимая версия")
        print("💡 Установите Python 3.10 или 3.11")
        return False

def check_processes():
    """Проверяет, есть ли уже запущенные процессы бота"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            if 'lady_perfection_bot' in result.stdout:
                print("⚠️  Обнаружены запущенные процессы бота")
                return True
        else:  # Unix
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'lady_perfection_bot' in result.stdout:
                print("⚠️  Обнаружены запущенные процессы бота")
                return True
        return False
    except Exception as e:
        print(f"⚠️  Не удалось проверить процессы: {e}")
        return False

def stop_existing_processes():
    """Останавливает существующие процессы бота"""
    print("🛑 Останавливаю существующие процессы...")
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                         capture_output=True, text=True)
        else:  # Unix
            subprocess.run(['pkill', '-f', 'lady_perfection_bot'], 
                         capture_output=True, text=True)
        time.sleep(3)
        print("✅ Процессы остановлены")
    except Exception as e:
        print(f"⚠️  Ошибка при остановке процессов: {e}")

def check_dependencies():
    """Проверяет наличие необходимых зависимостей"""
    required_packages = [
        'telegram',
        'aiohttp',
        'speech_recognition',
        'pydub',
        'gtts'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - не установлен")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Установите недостающие пакеты:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    return True

def check_config():
    """Проверяет наличие конфигурационного файла"""
    if not os.path.exists('config.py'):
        print("❌ Файл config.py не найден")
        print("💡 Создайте файл config.py с настройками бота")
        return False
    
    try:
        from config import TELEGRAM_TOKEN, DEEPSEEK_API_KEY
        if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "YOUR_TELEGRAM_TOKEN":
            print("❌ TELEGRAM_TOKEN не настроен в config.py")
            return False
        if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "YOUR_DEEPSEEK_API_KEY":
            print("❌ DEEPSEEK_API_KEY не настроен в config.py")
            return False
        print("✅ Конфигурация проверена")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта config.py: {e}")
        return False

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    print("\n🛑 Получен сигнал завершения. Останавливаю бота...")
    sys.exit(0)

def main():
    """Основная функция запуска"""
    print("🚀 Безопасный запуск бота Мэри П.")
    print("=" * 50)
    
    # Регистрируем обработчик сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Проверяем версию Python
    if not check_python_version():
        return
    
    print("\n📦 Проверка зависимостей:")
    if not check_dependencies():
        return
    
    print("\n⚙️  Проверка конфигурации:")
    if not check_config():
        return
    
    print("\n🔍 Проверка процессов:")
    if check_processes():
        response = input("❓ Обнаружены запущенные процессы. Остановить их? (y/n): ")
        if response.lower() in ['y', 'yes', 'да', 'д']:
            stop_existing_processes()
        else:
            print("❌ Запуск отменен")
            return
    
    print("\n🎯 Выбор режима запуска:")
    print("1. Обычный режим (polling)")
    print("2. Простой режим (без голосовых функций)")
    print("3. Только текстовый режим")
    
    choice = input("Выберите режим (1-3): ").strip()
    
    if choice == "1":
        bot_file = "lady_perfection_bot.py"
    elif choice == "2":
        bot_file = "lady_perfection_bot_simple.py"
    elif choice == "3":
        bot_file = "lady_perfection_bot_text_only.py"
    else:
        print("❌ Неверный выбор")
        return
    
    if not os.path.exists(bot_file):
        print(f"❌ Файл {bot_file} не найден")
        return
    
    print(f"\n🚀 Запуск бота в режиме: {bot_file}")
    print("=" * 50)
    
    try:
        # Запускаем бота
        subprocess.run([sys.executable, bot_file])
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main() 