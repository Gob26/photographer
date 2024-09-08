from flask import Flask
from app.extensions import db
from .config import Config
#импортируем роутеры
from .routes.user import user
from .routes.post import post
from .routes.main import main
from .routes.contacts import contacts


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    #Регистрация блюпринтов
    app.register_blueprint(user)
    app.register_blueprint(post)
    app.register_blueprint(main)
    app.register_blueprint(contacts)

    db.init_app(app)

    with app.app_context():
        db.create_all()








    return app