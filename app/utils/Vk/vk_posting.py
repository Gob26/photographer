import requests
from flask import url_for

from app import Config

access_token = Config.VK_ACCESS_TOKEN
group_id = Config.GROUP_ID


def post_vk_group(photosession):

    # Текст сообщения
    message = (f"{photosession.title} \n\n {photosession.meta_description} "
               f"\n\n {url_for('photosession.view_photoshoot', category_name=photosession.category.name, id=photosession.id, slug=photosession.slug, _external=True)}")

    # URL для API ВКонтакте
    url = "https://api.vk.com/method/wall.post"

    # Параметры запроса
    payload = {
        'owner_id': -int(group_id),  # ID группы с отрицательным значением
        'message': message,
        'from_group': 1,
        'access_token': access_token,
        'v': '5.131'
    }

    # Отправка POST-запроса
    response = requests.post(url, data=payload)

    # Обработка ответа
    if response.status_code == 200:
        response_json = response.json()
        if 'error' in response_json:
            print(f"Ошибка при публикации поста: {response_json['error']['error_msg']}")
        else:
            print("Пост успешно опубликован!")
    else:
        print(f"Ошибка: {response.status_code} - {response.text}")
