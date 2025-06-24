from flask import Flask, request, jsonify
import aiohttp
import asyncio
import os
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

@app.route('/alexa', methods=['POST'])
def alexa_webhook():
    """Обработка входящих запросов от Amazon Alexa"""
    request_json = request.get_json()
    
    # Получаем тип запроса
    request_type = request_json.get('request', {}).get('type')
    intent_name = request_json.get('request', {}).get('intent', {}).get('name')
    
    if request_type == 'LaunchRequest':
        # Приветствие при запуске навыка
        response_text = (
            "Здравствуйте! Я Мэри П., ваш персональный эксперт в психологии, "
            "питании и фитнесе. Как я могу вам помочь?"
        )
    elif request_type == 'IntentRequest':
        if intent_name == 'StartConversationIntent':
            response_text = (
                "Отлично! Я готова помочь вам. Расскажите, что вас беспокоит, "
                "или задайте любой вопрос о психологии, питании или фитнесе."
            )
        elif intent_name == 'AskQuestionIntent':
            # Получаем вопрос пользователя
            question = request_json.get('request', {}).get('intent', {}).get('slots', {}).get('question', {}).get('value', '')
            if question:
                response_text = asyncio.run(get_deepseek_response(question))
            else:
                response_text = "Извините, не удалось понять ваш вопрос. Попробуйте переформулировать."
        elif intent_name == 'AMAZON.HelpIntent':
            response_text = (
                "Я Мэри П., ваш персональный эксперт. Я могу помочь вам с вопросами "
                "психологии, составить план питания, дать кулинарные советы или "
                "разработать программу тренировок. Просто задайте мне вопрос!"
            )
        elif intent_name in ['AMAZON.StopIntent', 'AMAZON.CancelIntent']:
            response_text = "До свидания! Буду рада помочь вам снова."
        else:
            response_text = "Извините, не понимаю. Попробуйте переформулировать вопрос."
    else:
        response_text = "Извините, произошла ошибка."
    
    # Формируем ответ для Alexa
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": response_text
            },
            "shouldEndSession": False
        }
    }
    
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 