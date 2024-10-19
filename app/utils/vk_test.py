import requests

def post_to_vk_group():
    # Замените на свой токен сообщества с правильными правами (scope=wall,groups)
    vk_access_token = 'vk1.a.aGio1tAYwP5tIe5f0B-voDJ6r-hrMot61q9vMCT7D7SEm8U6QfHtRTTC9w_mfwWHSAiyDSZKSLl9DatufFAqrpLV-a-wQrB2QlVdyxGmlyanrMv48rmKDUQ6HLD5cJTLDOpuTbJQgZMzZdtwcbiNzeQlCm2B-gFfC_AV5bp_jWY66OL2IhUuCkT0Tz6A92GVW4UsEWpz9Z9kPLc0GTzswA'

    # ID группы с отрицательным значением
    group_id = '-227896833'

    # Текст сообщения
    message = "Привет! Это тестовое сообщение для проверки работы API."

    # URL для API ВКонтакте
    url = "https://api.vk.com/method/wall.post"

    # Параметры запроса
    payload = {
        'owner_id': group_id,  # ID группы с отрицательным значением
        'message': message,
        'access_token': vk_access_token,
        'v': '5.131'
    }

    # Отправка POST-запроса
    response = requests.post(url, data=payload)

    # Возврат результата в виде JSON
    return response.json()

# Вызов функции для отправки сообщения
result = post_to_vk_group()
print(result)
