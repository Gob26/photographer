from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from sqlalchemy import String
from wtforms.fields.simple import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, EqualTo


class RegistraionForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired(), Length(min=2, max=100)])
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')]) #валидация пройдет если пароль совпадет
    avatar = FileField('Загрузить свое фото', validators=[FileAllowed(['jpg','jpeg', 'png'])]) #валидация на определенные файлы загрузки
    submit = SubmitField('Зарегистрироваться')