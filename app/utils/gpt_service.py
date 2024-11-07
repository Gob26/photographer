import requests
from aiohttp.helpers import AppKey
from app import Config


API_KEY = Config.API_KEY
URL = Config.URL

''' МОДЕЛИ НА ВЫБОР
#https://github.com/selfsff/GPT4ALL-Free-GPT-API?tab=readme-ov-file
#https://docs.gpt4-all.xyz/information/models

gpt-4o-mini / gpt-4o-mini-2024-07-18

gpt-3.5-turbo

dall-e-3

mistral-large-latest

mistral-small-latest

open-mistral-nemo

llama-3-70b

llama-3-8b

llama-3.1-405b

llama-3.1-70b

wizardlm-2-8x22b

mixtral-8x22b'''


def get_gpt_response(user_message):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        'model': 'gpt-4o-mini',
        'messages': [{'role': 'user', 'content': user_message}],
    }

    try:
        response = requests.post(URL, headers=headers, json=data)
        response.raise_for_status()  # Если код ответа не 200, вызывает исключение
        response_data = response.json()

        # Возвращаем ответ от GPT
        return response_data['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        # Логируем ошибку и возвращаем сообщение об ошибке
        print(f'Ошибка при запросе к GPT API: {e}')
        return f'Ошибка при запросе к GPT API: {e}'
