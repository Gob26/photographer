from datetime import datetime

from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50),default='user')
    name = db.Column(db.String(250))
    login = db.Column(db.String(150))
    password = db.Column(db.String(150))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(200))