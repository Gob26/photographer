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


def save_picture(picture):   #Сохраняем уменьшенное изображение и передаем кго новое имя
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename) # разделяем имя файла и расширение
    picture_fn = random_hex + f_ext               # формируем имя файла  
    picture_path = os.path.join(current_app.config['SERVER_PATH'], picture_fn) # путь к файлу
    output_size = (125, 125)
    i = Image.open(picture)      # открываем изображение
    i.thumbnail(output_size)     # изменяем размер
    i.save(picture_path)            
    return picture_fn           # возвращаем измененное имя для базы данных


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
