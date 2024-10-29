from flask import Flask
from app.extensions import db, migrate, login_manager, cache
from dotenv import load_dotenv
from .config import Config
from app.tracking.user_tracking import track_user

# Импортируем роутеры
from .routes.user import user
from .routes.post import post
from .routes.services import services
from .routes.main import main
from .routes.contacts import contacts
from .routes.photosession import photoshoot_bp
from .routes.gpt_idea import gpt
from .routes.yandex_map import map

# Импортируем Flask-Admin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models.user import User, Role  # Импортируй свои модели

def create_app(config_class=Config):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)  # Инициализация конфигурации

    @app.before_request
    def before_request():
        track_user()  # Вызов функции отслеживания перед каждым запросом

    # Регистрация блюпринтов
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
    db.init_app(app)  # Инициализация базы данных
    migrate.init_app(app, db)  # Инициализация миграции
    login_manager.init_app(app)  # Инициализация авторизации

    # Настройки Login Manager
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'Нужно авторизоваться для доступа к этой станице'

    # Инициализация админ-панели
    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

    # Регистрация моделей
    admin.add_view(ModelView(User, db.session, endpoint='admin_user'))
    admin.add_view(ModelView(Role, db.session))

    with app.app_context():
        db.create_all()

    return app 
