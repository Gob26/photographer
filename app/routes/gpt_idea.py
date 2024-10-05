from flask import Blueprint, render_template, request, flash
from ..forms import GPTForm
from app.utils.gpt_service import get_gpt_response  # Импортируем функцию из gpt_service

gpt = Blueprint('gpt', __name__)

@gpt.route('/idea', methods=['POST', 'GET'])
def gpt_page():
    response_message = None  # Ответ GPT
    form = GPTForm()   # Создание экземпляра формы

    if form.validate_on_submit():  # Проверяем, была ли форма отправлена и валидна ли она
        flash("Ответ получен, листайте вниз)", 'info') #флеш о получении ответа
        free_text = form.free_text.data
        category = form.category.data
        style = form.style.data
        place = form.place.data

        if request.method == 'POST':
            # Формируем пользовательское сообщение для GPT
            user_message = f"Представь, что ты фотограф мирового уровня, работающий в Ставрополе. " \
                          f"Пожалуйста, предложи оригинальную идею для  '{category}' в стиле '{style}'. " \
                          f"Место съемки — '{place}'. Также учти дополнительную информацию: '{free_text}'. " \
                          f"Предложи различные идеи, включая время съемки, освещение, подходящие наряды, аксессуары, позы и декор. " \
                          f"Будь креативным и дай советы, которые помогут создать незабываемые фотографии. Отвечай только на русском и без заголовков"

            print(f'Пользовательское сообщение: {user_message}')  # Логируем сообщение пользователя

            # Получаем ответ от GPT через нашу функцию
            response_message = get_gpt_response(user_message)

    return render_template('main/idea.html', form=form, gpt_response=response_message)
