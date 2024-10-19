import requests
from app import Config

access_token = Config.VK_ACCESS_TOKEN
group_id = Config.GROUP_ID

def post_vk_group(title, description):

    # Текст сообщения
    message = f"{title} \n {description}"

    # URL для API ВКонтакте
    url = "https://api.vk.com/method/wall.post"

    # Параметры запроса
    payload = {
        'owner_id': group_id,  # ID группы с отрицательным значением
        'message': message,
        'access_token': access_token,
        'v': '5.131'
    }

    # Отправка POST-запроса
    response = requests.post(url, data=payload)

    # Возврат результата в виде JSON
    return response.json()
