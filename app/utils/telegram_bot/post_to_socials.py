import requests
from flask import url_for

from app import Config


def send_photosession_to_telegram(photosession, photo_paths):
    telegram_token = Config.TELEGRAM_BOT_TOKEN
    chat_id = Config.CHAT_ID  # Укажите идентификатор вашего канала
    message = (
        f"📸 Новая фотосессия !!!\n\n"
        f"**Название:** {photosession.title}\n"
        f"**Описание:** {photosession.meta_description}\n"
        f"**Ссылка:** {url_for('photosession.view_photoshoot', category_name=photosession.category.name, id=photosession.id, _external=True)}"
    )

    # Отправляем сообщение и фотографии по очереди
    url = f'https://api.telegram.org/bot{telegram_token}/sendPhoto'

    # Сначала отправим текст сообщения
    requests.post(f'https://api.telegram.org/bot{telegram_token}/sendMessage', json={
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'  # Используем Markdown для форматирования текста
    })

    # Затем отправим фотографии
    for photo_path in photo_paths:
        with open(photo_path, 'rb') as photo_file:
            files = {'photo': photo_file}
            payload = {
                'chat_id': chat_id,
                'caption': message,  # Можно добавить заголовок к фотографии
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, data=payload, files=files)
            if response.status_code != 200:
                print(f"Ошибка при отправке фотографии в Telegram: {response.text}")
