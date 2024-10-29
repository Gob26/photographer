from slugify import slugify
from sqlalchemy import JSON

from ..extensions import db
from datetime import datetime

class Post(db.Model):
    __tablename__ = 'blog_post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(350), nullable=False)
    slug = db.Column(db.String(350), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    snippet = db.Column(db.String(350), nullable=True)       # под вопросом
    images = db.Column(JSON)   # храним список ссылок на изображения
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, title):
        self.title = title
        self.slug = self.generate_slug()

    def generate_slug(self):
        return slugify(self.title)

    def __repr__(self):
        return f'<Post {self.title}>' # аналог pprint для разраба , пригодится в будущем