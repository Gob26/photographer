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


from PIL import Image
import os
from io import BytesIO

def optimize_image(image_file, max_size_kb=200, quality_start=95):
    """
    Оптимизирует изображение: сжимает до указанного размера и конвертирует в WebP формат.
    
    Args:
        image_file: FileStorage объект или путь к файлу
        max_size_kb: Максимальный размер файла в килобайтах
        quality_start: Начальное значение качества для WebP
        
    Returns:
        BytesIO: Оптимизированное изображение в формате WebP
        str: Новое имя файла с расширением .webp
    """
    # Открываем изображение
    if hasattr(image_file, 'read'):
        # Если передан FileStorage объект
        image = Image.open(image_file)
    else:
        # Если передан путь к файлу
        image = Image.open(image_file)
    
    # Конвертируем в RGB, если изображение в RGBA
    if image.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1])
        image = background
    
    # Максимальный размер в байтах
    max_size_bytes = max_size_kb * 1024
    
    # Получаем размеры изображения
    width, height = image.size
    
    # Если размер больше 1920px по широкой стороне, уменьшаем с сохранением пропорций
    max_dimension = 1920
    if width > max_dimension or height > max_dimension:
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Буфер для хранения оптимизированного изображения
    output_buffer = BytesIO()
    
    # Начальное качество
    quality = quality_start
    
    # Пробуем разные уровни качества, пока не достигнем целевого размера
    while quality > 5:
        output_buffer.seek(0)
        output_buffer.truncate()
        
        # Сохраняем в формат WebP с текущим качеством
        image.save(output_buffer, format='WebP', quality=quality, optimize=True)
        
        # Проверяем размер
        if output_buffer.tell() <= max_size_bytes:
            break
            
        # Уменьшаем качество и пробуем снова
        quality -= 5
    
    # Генерируем новое имя файла
    original_filename = os.path.splitext(
        image_file.filename if hasattr(image_file, 'filename') 
        else os.path.basename(image_file)
    )[0]
    new_filename = f"{original_filename}.webp"
    
    # Возвращаем буфер с изображением и новое имя файла
    output_buffer.seek(0)
    return output_buffer, new_filename


def save_picture(picture):   #Сохраняем уменьшенное изображение и передаем его новое имя
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
