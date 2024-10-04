from flask import Blueprint, render_template, request
from ..forms import GPTForm
import requests

gpt = Blueprint('gpt', __name__)

API_KEY = 'sk-nZ1fNktvkOPFqAiK44F4E1AcA0Ac45CfA21c989c6fEbE262'
URL = 'https://neuroapi.host/v1/chat/completions'

@gpt.route('/idea', methods=['POST', 'GET'])
def gpt_page():
    response_message = None  # Ответ GPT
    form = GPTForm()   # Создание экземпляра формы

    if form.validate_on_submit():  # Проверяем, была ли форма отправлена и валидна ли она
        free_text = form.free_text.data
        category = form.category.data
        style = form.style.data
        place = form.place.data

        if request.method == 'POST':
            user_message = f"Представь, что ты фотограф мирового уровня, работающий в Ставрополе. " \
                          f"Пожалуйста, предложи оригинальную идею для  '{category}' в стиле '{style}'. " \
                          f"Место съемки — '{place}'. Также учти дополнительную информацию: '{free_text}'. " \
                          f"Предложи различные идеи, включая время съемки, освещение, подходящие наряды, аксессуары, позы и декор. " \
                          f"Будь креативным и дай советы, которые помогут создать незабываемые фотографии. Отвечай только на русском и без заголовков"

            print(f'Пользовательское сообщение: {user_message}')  # Логируем сообщение пользователя

            headers = {
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json',
            }

            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': user_message}],
            }

            response = requests.post(URL, headers=headers, json=data)
            print(f'Статус ответа: {response.status_code}')  # Логируем статус ответа

            if response.status_code == 200:
                response_data = response.json()
                print(f'Ответ от API: {response_data}')  # Логируем полный ответ от API
                response_message = response_data['choices'][0]['message']['content']
            else:
                response_message = f'Ошибка: {response.status_code} - {response.text}'
                print(response_message)  # Логируем ошибку

    return render_template('main/idea.html', form=form, gpt_response=response_message)
