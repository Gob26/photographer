import requests

API_KEY = 'sk-nZ1fNktvkOPFqAiK44F4E1AcA0Ac45CfA21c989c6fEbE262'
URL = 'https://neuroapi.host/v1/chat/completions'

def get_gpt_response(user_message):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        'model': 'gpt-3.5-turbo',
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
