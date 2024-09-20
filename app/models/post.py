from ..extensions import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class Post(db.Model):
    #__tablename__ = 'blog_post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    content = db.Column(db.Text, nullable=False)
    snippet = db.Column(db.Text, nullable=True)       # под вопросом
    image = db.Column(db.PickleType, nullable=True)   # храним список ссылок на изображения
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Post {self.title}>' # аналог pprint для разраба , пригодится в будущем