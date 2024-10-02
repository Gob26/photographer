from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, PasswordField, SubmitField, FileField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

from app.models.user import User
from app.models.photosession import Category

#регистрация
class RegistrationForm(FlaskForm):  # Исправлено название класса
    name = StringField('ФИО', validators=[DataRequired(), Length(min=2, max=100)])
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    avatar = FileField('Загрузить свое фото', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Зарегистрироваться')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user:
            raise ValidationError('Логин занят')

#вход
class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


#Добавление фотосессии
class CreatePhotosessionForm(FlaskForm):
    title = StringField('Заголовок(title)', validators=[DataRequired(), Length(min=3, max=90)])
    meta_description = StringField('Описание для поисковиков(description)', validators=[Length(min=5, max=210)])
    content = TextAreaField('Текст описание')
    category = SelectField('Категория', choices=[(cat.name, cat.value) for cat in Category],
                           validators=[DataRequired()])
    photos = MultipleFileField('Фотографии', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])