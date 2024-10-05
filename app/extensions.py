from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_caching import Cache

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()    # Инициализация шифрования
login_manager = LoginManager()#И инициализируем в нашем файле _init__
# Инициализация кэша
cache = Cache()  # Инициализация кэша с приложением