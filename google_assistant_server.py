from flask import Flask, request, jsonify
import aiohttp
import asyncio
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, SYSTEM_PROMPT

app = Flask(__name__)

async def get_deepseek_response(text):
    """Получение ответа от DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(DEEPSEEK_API_URL, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return "Извините, произошла ошибка при обработке вашего запроса."

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработка входящих запросов от Google Assistant"""
    request_json = request.get_json()
    
    # Получаем текст запроса
    query = request_json.get('queryResult', {}).get('queryText', '')
    
    # Если это первый запуск
    if request_json.get('queryResult', {}).get('intent', {}).get('displayName') == 'actions.intent.MAIN':
        response_text = (
            "Здравствуйте! Я Мэри П., ваш персональный эксперт в психологии, "
            "питании и фитнесе. Как я могу вам помочь?"
        )
    else:
        # Получаем ответ от DeepSeek
        response_text = asyncio.run(get_deepseek_response(query))
    
    # Формируем ответ для Google Assistant
    response = {
        "fulfillmentText": response_text,
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [response_text]
                }
            }
        ]
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 