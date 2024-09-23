from flask import Blueprint, render_template, redirect
from app.utils.functions import save_picture
from ..forms import RegistraionForm
from ..models.user import User
from ..extensions import db, bcrypt

user = Blueprint('user', __name__)

@user.route('/user/register', methods=['GET', 'POST'])  # Методы корректны
def register():
    form = RegistraionForm()
    if form.validate_on_submit():  # Условие проверки формы на отправку
        avatar_filename = save_picture(form.avatar.data)  # Сохраняем картинку
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # Хэшируем пароль
        # Создаем нового пользователя с переданными данными
        new_user = User(
            name=form.name.data, 
            login=form.login.data, 
            avatar=avatar_filename, 
            password=hashed_password  # Добавляем запятую
        )
        db.session.add(new_user)  # Добавляем пользователя в сессию
        db.session.commit()  # Сохраняем изменения в базе данных
        print(f'Пользователь {form.name.data} успешно зарегистрирован')
        return redirect('/')
    return render_template('user/register.html', form=form)
