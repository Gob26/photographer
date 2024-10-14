from crypt import methods

from flask import Blueprint, render_template, request, flash, url_for
from flask_login import login_required
from werkzeug.utils import redirect

from ..extensions import db
from ..forms import CreateServicesForm
from ..models.services import Service

services = Blueprint('services', __name__)

@services.route('/services')
def services_page():
    all_services = Service.query.all()
    return render_template('services/services.html', services=all_services)


@services.route('/services/create', methods=['GET', 'POST'])
@login_required
def create_service():
    # Наша форма для услуг
    form = CreateServicesForm()
    # Проверка на валидность формы
    if form.validate_on_submit():
        #Создаем новый объект услугу
        new_service = Service(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data
        )
        try:
            #Добавляем в базу
            db.session.add(new_service)
            db.session.commit()

            flash('Фотосессия успешно создана!', 'success')
            #перенаправляем на все услуги
            return redirect(url_for('services.services_page'))

        except Exception as e:
            db.session.rollback()  # Откат транзакции в случае ошибки
            flash(f'Ошибка при добавлении услуги: {str(e)}', 'danger')
            print((f"Error : {str(e)}"))
    return render_template('services/create_service.html', form=form)


@services.route('/services/<int:service_id>/update', methods=['POST', 'GET'])
@login_required
def update(service_id):
    service = Service.query.get_or_404(service_id)
    form = CreateServicesForm(obj=service)

    if form.validate_on_submit():
        try:
            # Обновление данных услуги
            service.name = form.name.data
            service.description = form.description.data
            service.price = form.price.data

            db.session.commit()
            flash('Услуга успешно изменена!', 'success')
            # Перенаправление на страницу с услугами после успешного обновления
            return redirect(url_for('services.services_page'))

        except Exception as e:
            db.session.rollback()
            flash('При изменении услуги произошла ошибка', 'danger')
            print(f"Error: {str(e)}")
            # Перенаправление на ту же страницу, если возникла ошибка
            return redirect(url_for('services.update', service_id=service_id))

    # Отображение формы с текущими данными для редактирования услуги
    return render_template('services/update.html', form=form, service=service)


@services.route('/services/<int:service_id>/delete', methods=['POST'])
@login_required
def delete(service_id):
    service = Service.query.get_or_404(service_id)

    try:
        db.session.delete(service)
        db.session.commit()

        flash('Услуга успешно удалена', 'success')
        return redirect(url_for('services.services_page'))

    except Exception as e:
        db.session.rollback()
        flash('При удалении услуги произошла ошибка', 'danger')
        print((f"Error : {str(e)}"))
        return redirect(url_for('services.services_page'))
