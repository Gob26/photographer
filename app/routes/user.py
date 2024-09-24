from crypt import methods

from flask import Blueprint
from urllib3 import request
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user
from app.utils.functions import save_picture
from ..forms import RegistrationForm, LoginForm # Исправлено имя класса
from ..models.user import User
from ..extensions import db, bcrypt

user = Blueprint('user', __name__)


@user.route('/user/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Исправлено имя класса
    if form.validate_on_submit():
        # Проверка на наличие файла аватара
        avatar_filename = save_picture(form.avatar.data) if form.avatar.data else None

        # Хэшируем пароль
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Создаем нового пользователя
        new_user = User(
            name=form.name.data,
            login=form.login.data,
            avatar=avatar_filename,
            password=hashed_password
        )

        try:
            db.session.add(new_user)  # Добавляем пользователя в сессию
            db.session.commit()  # Сохраняем изменения в базе данных
            flash(f'Пользователь {form.name.data} успешно зарегистрирован', 'success')
            return redirect('/')
        except Exception as e:
            db.session.rollback()  # Откат изменений при ошибке
            flash('Произошла ошибка при регистрации пользователя. Попробуйте еще раз.', 'danger')
    return render_template('user/register.html', form=form)


@user.route('/user/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Исправлено имя класса
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')  # возвращаем пользователя на страницу которую он хотел
            flash(f'Пользователь {form.login.data} успешно', 'success')
            return redirect(next_page) if next_page else redirect(url_for('post.all'))
        else:
            flash("Ошибка: Неверный логин или пароль", "danger")  # Уточнено сообщение об ошибке
    return render_template('user/login.html', form=form)


@user.route('/user/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('post.all'))