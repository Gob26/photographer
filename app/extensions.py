from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()    # Инициализация шифрования
login_manager = LoginManager()#И инициализируем в нашем файле _init__