import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    APPNAME = 'app'                                    # Имя приложения
    ROOT = os.path.abspath(os.path.dirname(__file__))  # Корень приложения (файл, где находится конфигурация)
    UPLOAD_PATH = os.path.join('static', 'upload')     # Путь для загрузки файлов
    SERVER_PATH = os.path.join(ROOT, UPLOAD_PATH)      # Полный путь к папке загрузок
 

    USER = os.environ.get('POSTGRES_USER', 'anna')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'annaanna')
    HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
    PORT = os.environ.get('POSTGRES_PORT', 5432)
    DB = os.environ.get('POSTGRES_DB', 'mydb')

    SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    SECRET_KEY = 'ferf5453rfrgwrs34t46245rf2454tfwrge'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Токен для Telegram-бота
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    #ВК
    VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')
    GROUP_ID = os.getenv('GROUP_ID')
    CHAT_ID = os.getenv('CHAT_ID')