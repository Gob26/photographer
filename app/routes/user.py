from crypt import methods
from flask import Blueprint, render_template, redirect

from ..forms import RegistraionForm
from ..models.user import User
from ..extensions import db, bcrypt


user = Blueprint('user', __name__)


@user.route('/user/register', methods=['GET', 'POST'])  # Заменяем на список
def register():
    form = RegistraionForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # Передаем пароль в хэш
        user = User(name=form.name.data, login=form.login.data, avatar=form.avatar.data, password=hashed_password)
        return redirect('/')
    else:
        print('Ошибка')
    return render_template('user/register.html', form=form)
