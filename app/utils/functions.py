from PIL import Image
import secrets
from flask import current_app
import os

import random
from datetime import datetime, date

from app.models.photosession import Photosession


def get_photosessions_from_db():
    return Photosession.query.all()  # Получаем все фотосессии из базы данных


def get_random_photosessions(count=6):
    photosessions = get_photosessions_from_db()  # Получаем фотосессии из БД
    if not photosessions:  # Проверяем, есть ли фотосессии
        return []

    today = date.today()
    today_datetime = datetime.combine(today, datetime.min.time())
    random.seed(int(today_datetime.timestamp()))

    return random.sample(photosessions, min(len(photosessions), count))


import secrets
import os
from PIL import Image
from flask import current_app


def save_picture(picture, category_folder):
    # Генерируем уникальное имя для изображения
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)

    # Изменяем расширение на .webp
    picture_fn = random_hex + ".webp"

    # Путь к сохранению изображения
    picture_path = os.path.join(category_folder, picture_fn)

    # Открываем изображение с помощью PIL
    i = Image.open(picture)

    # Оптимизация: изменяем размер до необходимого и сохраняем в формате webp
    output_size = (800, 800)  # Вы можете изменить размер на подходящий
    i.thumbnail(output_size)

    # Пробуем сохранить с оптимизацией для уменьшения размера
    try:
        i.save(picture_path, format="WEBP", quality=85, optimize=True)
    except Exception as e:
        raise ValueError(f"Ошибка при сохранении изображения: {str(e)}")

    # Проверяем, не превышает ли размер 150 КБ
    if os.path.getsize(picture_path) > 150 * 1024:
        # Если изображение слишком большое, пробуем снизить качество
        i.save(picture_path, format="WEBP", quality=70, optimize=True)

    # Возвращаем новое имя файла для хранения в базе данных
    return picture_fn


def compress_image(image_path, output_path, quality=85): #сжимаем и переводим в формат webp
    # Открываем изображение
    img = Image.open(image_path)

    # Конвертируем в формат webp
    webp_image_path = f"{os.path.splitext(output_path)[0]}.webp"

    # Сжимаем и сохраняем
    img.save(webp_image_path, 'webp', quality=quality)

    return webp_image_path


def allowed_file(filename): # Проверка на допустимый формат
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
