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
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    meta_description = db.Column(db.String(250), nullable=True)
    content = db.Column(db.Text, nullable=True)
    category = db.Column(db.Enum(Category), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    photos = db.relationship('Photo', backref='photosession', lazy=True)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(250), nullable=False)
    photosession_id = db.Column(db.Integer, db.ForeignKey('photosession.id'), nullable=False)


    def __repr__(self):
        return f"Photosession {self.id}"