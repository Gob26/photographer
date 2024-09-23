from PIL import Image
import secrets
import os


def save_picture(picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename) # разделяем имя файла и расширение
    picture_fn = random_hex + f_ext







def compress_image(image_path, output_path, quality=85):
    # Открываем изображение
    img = Image.open(image_path)

    # Конвертируем в формат webp
    webp_image_path = f"{os.path.splitext(output_path)[0]}.webp"

    # Сжимаем и сохраняем
    img.save(webp_image_path, 'webp', quality=quality)

    return webp_image_path


def allowed_file(filename): # Проверка на допустимый формат
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
