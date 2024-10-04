import requests

# Замените 'your_api_key' на ваш реальный API-ключ
API_KEY = 'sk-nZ1fNktvkOPFqAiK44F4E1AcA0Ac45CfA21c989c6fEbE262'
URL = 'https://neuroapi.host/v1/chat/completions'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json',
}

data = {
    'model': 'gpt-3.5-turbo',  # Вы можете выбрать модель, которую хотите использовать
    'messages': [{'role': 'user', 'content': 'что я спрашивал '}],
}

response = requests.post(URL, headers=headers, json=data)

if response.status_code == 200:
    response_data = response.json()
    reply = response_data['choices'][0]['message']['content']
    print('Ответ GPT:', reply)
else:
    print('Ошибка:', response.status_code, response.text)
