import uuid
from datetime import datetime
from flask_login import UserMixin
from ..extensions import db, login_manager
from flask_security import RoleMixin

# Связь многие ко многим между User и Role
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), default='user')
    name = db.Column(db.String(250))
    login = db.Column(db.String(150))
    password = db.Column(db.String(150))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))  # Здесь исправлено

    # Связь с ролями
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
print(uuid.uuid4())