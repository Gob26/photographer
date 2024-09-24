from flask import Blueprint, render_template, redirect, flash
from app.utils.functions import save_picture
from ..forms import RegistrationForm  # Исправлено имя класса
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
