#!/usr/bin/env python3
"""
Тест подключения бота к Telegram API
"""

import asyncio
import aiohttp
from config import TELEGRAM_TOKEN

async def test_bot_connection():
    """Тестирует подключение бота к Telegram API"""
    print("🔍 Тест подключения бота к Telegram API")
    print("=" * 50)
    
    # Тест 1: Получение информации о боте
    print("1. Получение информации о боте...")
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        bot_info = data['result']
                        print(f"✅ Бот найден: {bot_info['first_name']} (@{bot_info['username']})")
                        print(f"   ID: {bot_info['id']}")
                        print(f"   Может присоединяться к группам: {bot_info.get('can_join_groups', False)}")
                        print(f"   Может читать сообщения групп: {bot_info.get('can_read_all_group_messages', False)}")
                    else:
                        print(f"❌ Ошибка API: {data.get('description', 'Неизвестная ошибка')}")
                        return False
                else:
                    print(f"❌ HTTP ошибка: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    
    # Тест 2: Получение обновлений
    print("\n2. Получение обновлений...")
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        updates = data['result']
                        print(f"✅ Получено обновлений: {len(updates)}")
                        if updates:
                            print("   Последние обновления:")
                            for update in updates[-3:]:  # Показываем последние 3
                                update_id = update.get('update_id')
                                message = update.get('message', {})
                                user = message.get('from', {})
                                text = message.get('text', 'Нет текста')
                                print(f"   - ID: {update_id}, Пользователь: {user.get('first_name', 'Неизвестно')}, Текст: {text[:50]}...")
                        else:
                            print("   Обновлений нет")
                    else:
                        print(f"❌ Ошибка API: {data.get('description', 'Неизвестная ошибка')}")
                        return False
                else:
                    print(f"❌ HTTP ошибка: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Ошибка получения обновлений: {e}")
        return False
    
    # Тест 3: Проверка webhook
    print("\n3. Проверка webhook...")
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        webhook_info = data['result']
                        if webhook_info.get('url'):
                            print(f"⚠️  Webhook установлен: {webhook_info['url']}")
                            print("   Это может мешать получению обновлений через polling")
                        else:
                            print("✅ Webhook не установлен - polling должен работать")
                    else:
                        print(f"❌ Ошибка API: {data.get('description', 'Неизвестная ошибка')}")
                else:
                    print(f"❌ HTTP ошибка: {response.status}")
    except Exception as e:
        print(f"❌ Ошибка проверки webhook: {e}")
    
    print("\n🎯 Рекомендации:")
    print("1. Убедитесь, что вы отправляете сообщения правильному боту")
    print("2. Проверьте, что бот не заблокирован")
    print("3. Если webhook установлен, удалите его командой:")
    print(f"   curl -X POST https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_bot_connection()) 