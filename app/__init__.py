from flask import Flask
from app.extensions import db, migrate, login_manager, cache
from dotenv import load_dotenv
from .config import Config
#импортируем роутеры
from .routes.user import user
from .routes.post import post
from .routes.services import services
from .routes.main import main
from .routes.contacts import contacts
from .routes.photosession import photoshoot_bp
from .routes.gpt_idea import gpt
from .routes.yandex_map import map
def create_app(config_class=Config):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class) # Инициализация конфигурации

    #Регистрация блюпринтов
    app.register_blueprint(user)
    app.register_blueprint(post)
    app.register_blueprint(services)
    app.register_blueprint(main)
    app.register_blueprint(contacts)
    app.register_blueprint(photoshoot_bp)
    app.register_blueprint(gpt)
    app.register_blueprint(map)
    # Инициализация кэша
    cache.init_app(app)  # Инициализация кэша
    db.init_app(app)                    # Инициализация базы данных
    migrate.init_app(app, db)           # Инициализация миграции
    login_manager.init_app(app)         # Инициализация авторизации

    #LoGIN Manager  #Настройки логин менеджера
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'Нужно авторизоваться для доступа к этой станице'

    with app.app_context():
        db.create_all()

    return app 

