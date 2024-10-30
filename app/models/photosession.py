from sqlalchemy import Boolean
from sqlalchemy.dialects.postgresql import ENUM
from slugify import slugify
from app import db
from datetime import datetime
import enum


class Category(enum.Enum):
    wedding = 'Свадебная фотосессия'
    family = 'Семейная фотосессия'
    children = 'Детская фотосессия'
    male = 'Мужская фотосессия'
    female = 'Женская фотосессия'
    couple = 'Фотосессия пары'
    portrait = 'Портретная фотосессия'
    studio = 'Фотосессия в студии'
    street = 'Уличная фотосессия'
    reportage = 'Репортажная фотосессия'
    group = 'Групповая фотосессия'
    discharge = 'Фотосессия на выписку'
    wedding_photographer = 'Фотограф на венчание'
    baptism_photographer = 'Фотограф на крещение'


class Photosession(db.Model):
    __tablename__ = 'photosession'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    meta_description = db.Column(db.String(250), nullable=True)
    content = db.Column(db.Text, nullable=True)
    category = db.Column(ENUM(Category), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    photos = db.relationship('Photo', backref='photosession', lazy=True)
    show_on_main = db.Column(Boolean, default=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    slug = db.Column(db.String, unique=True, nullable=False)

    def __init__(self, title, slug, meta_description, content, category, created_at=None, show_on_main=False, latitude=None, longitude=None):
        self.title = title
        self.slug = slug
        self.meta_description = meta_description
        self.content = content
        self.category = category
        self.created_at = created_at or datetime.utcnow()
        self.show_on_main = show_on_main
        self.latitude = latitude  # Добавляем latitude
        self.longitude = longitude  # Добавляем longitude


class Photo(db.Model):
    __tablename__ = 'photo'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(250), nullable=False)
    photosession_id = db.Column(db.Integer, db.ForeignKey('photosession.id'), nullable=False)

    def __repr__(self):
        return f"Photo {self.id} in Photosession {self.photosession_id}"