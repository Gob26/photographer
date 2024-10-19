import requests

# Укажите ваш пользовательский токен доступа и ID группы
VK_ACCESS_TOKEN = 'vk1.a.xUW3TJ_A4wu2gAC9lwQYDTxly0O1Z_K_sJp1Mv6xMbOA8to9d2Zty4NIvqsMjguQknu-DOY1-qWsrC96Ai5QbxOPp3ugfwxcHXiODjPf8Rdmd3JzPi_X_U5HitvJg8MEB6Guc5rSsKjOTeBleQsZTkoMfNcW5hB1fwvx-F6UjLatSg2W7ayfmjBWXkRVLycrt_2b5MWVgv73pFeMiH2MeA'
 # Замените на ваш новый токен
GROUP_ID = '-227896833'  # ID группы без знака минус


def check_group_access():
    # Получение информации о группе
    response = requests.get("https://api.vk.com/method/groups.getById", params={
        'group_id': GROUP_ID,
        'access_token': VK_ACCESS_TOKEN,
        'v': '5.131'
    })
    return response.json()


def upload_photo_to_wall(photo_path):
    # Получение URL для загрузки фотографии
    upload_url_response = requests.get("https://api.vk.com/method/photos.getWallUploadServer", params={
        'group_id': GROUP_ID,
        'access_token': VK_ACCESS_TOKEN,
        'v': '5.131'
    })

    upload_url = upload_url_response.json().get('response', {}).get('upload_url')

    if upload_url is None:
        print("Не удалось получить upload_url")
        print("Ошибка при получении upload_url:", upload_url_response.json())  # Выводим ошибку
        return

    # Загрузка фотографии
    with open(photo_path, 'rb') as photo:
        files = {'photo': photo}
        response = requests.post(upload_url, files=files)
        response_json = response.json()

    if 'error' in response_json:
        print("Ошибка при загрузке фотографии:", response_json['error'])
        return

    # Сохранение фотографии на стене
    save_response = requests.post("https://api.vk.com/method/photos.saveWallPhoto", params={
        'access_token': VK_ACCESS_TOKEN,
        'v': '5.131',
        'group_id': GROUP_ID,
        'server': response_json['server'],
        'photo': response_json['photo'],
        'hash': response_json['hash']
    })

    return save_response.json()


# Проверка доступа к группе
group_info = check_group_access()
print("Информация о группе:", group_info)

# Путь к тестовой фотографии
photo_path = '/app/static/img/1.jpg'  # Убедитесь, что путь к вашей фотографии правильный
upload_result = upload_photo_to_wall(photo_path)
print("Результат загрузки:", upload_result)
