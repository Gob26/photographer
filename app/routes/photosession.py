import os
from crypt import methods
import logging

from decorator import append
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from sqlalchemy.testing.plugin.plugin_base import logging
from werkzeug.utils import secure_filename
from flask_login import login_required

from app.utils.Vk.vk_posting import post_vk_group
from app.utils.telegram_bot.post_to_socials import send_photosession_to_telegram
from ..forms import CreatePhotosessionForm
from app.utils.functions import allowed_file
from app.models.photosession import Photo, Category, Photosession
from ..extensions import db


photoshoot_bp = Blueprint('photosession', __name__)



@photoshoot_bp.route('/photoshoot/create', methods=['GET', 'POST'])
@login_required
def create_photoshoot():
    form = CreatePhotosessionForm()

    if form.validate_on_submit():
        # Преобразуем строковое значение категории в enum
        category = Category[form.category.data]

        # Обрабатываем координаты
        latitude, longitude = form.process_coordinates()

        # Создаем новый объект фотосессии
        new_photoshoot = Photosession(
            title=form.title.data,
            meta_description=form.meta_description.data,
            content=form.content.data,
            category=category,
            latitude=latitude,  # Координаты могут быть None
            longitude=longitude,  # Координаты могут быть None
        )

        # Добавляем фотосессию в базу данных
        db.session.add(new_photoshoot)
        db.session.commit()

        # Получаем основную папку для загрузки файлов из конфигурации
        upload_folder = current_app.config['SERVER_PATH']

        # Создаем путь к папке для сохранения фотографий на основе категории
        category_folder = os.path.join(upload_folder, category.name)

        # Проверяем, существует ли папка для данной категории, если нет — создаем
        if not os.path.exists(category_folder):
            os.makedirs(category_folder)
        #Сохраняем ссылки на фото для ВК
        photo_links = []
        # Обрабатываем загруженные фотографии
        photos = request.files.getlist('photos')
        for photo in photos:
            if photo and allowed_file(photo.filename):
                # Генерируем безопасное имя файла
                filename = secure_filename(photo.filename)

                # Формируем полный путь для сохранения фотографии
                photo_path = os.path.join(category_folder, filename)

                try:
                    # Сохраняем файл по указанному пути
                    photo.save(photo_path)

                    # Создаем запись фотографии в базе данных
                    new_photo = Photo(filename=filename, photosession_id=new_photoshoot.id)
                    db.session.add(new_photo)
                    # Добавляем ссылки на фото в список для BK
                    photo_links.append(f"{category_folder}/{filename}")  # Пример ссылки, измените по необходимости
                except Exception as e:
                    flash(f'Ошибка при сохранении фотографии: {str(e)}', 'danger')

        # Сохраняем изменения в базе данных
        db.session.commit()
        # Отправляем данные в ВК
        post_vk_group(
            title=new_photoshoot.title,
            description=new_photoshoot.meta_description
        )
        # Отправляем данные о фотосессии в Telegram
        send_photosession_to_telegram(new_photoshoot, photo_links)
        # Выводим сообщение об успешном создании фотосессии
        flash('Фотосессия успешно создана!', 'success')

        # Перенаправляем пользователя на страницу созданной фотосессии
        return redirect(
            url_for('photosession.view_photoshoot', category_name=new_photoshoot.category.name, id=new_photoshoot.id))

    # Если метод GET, отображаем форму создания фотосессии
    return render_template('photosession/create_photoshoot.html', form=form, categories=Category)


@photoshoot_bp.route('/photosessions/<string:category_name>/<int:id>/delete', methods=['POST'])
@login_required
def delete(category_name, id):
    photosession = Photosession.query.get_or_404(id)

    try:
        # Delete associated photos
        for photo in photosession.photos:
            # удаляем фото
            photo_path = os.path.join(current_app.config['SERVER_PATH'], category_name, photo.filename)
            if os.path.exists(photo_path):
                os.remove(photo_path)

            # Delete photo record from database
            db.session.delete(photo)

        # Delete photosession
        db.session.delete(photosession)
        db.session.commit()

        current_app.logger.info(f"Photosession deleted: {photosession}")
        flash('Фотосессия успешно удалена', 'success')
        return redirect(url_for('photosession.list_photoshoots'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting photosession: {str(e)}")
        flash('При удалении фотосессии произошла ошибка', 'danger')
        return redirect(url_for('photosession.view_photoshoot', category_name=category_name, id=id))


@photoshoot_bp.route('/photosessions/<string:category_name>/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(category_name, id):  # Changed function name from update_photoshoot to update
    photosession = Photosession.query.get_or_404(id)
    form = CreatePhotosessionForm(obj=photosession)

    if form.validate_on_submit():
        try:
            # Update photosession details
            photosession.title = form.title.data
            photosession.meta_description = form.meta_description.data
            photosession.content = form.content.data
            photosession.category = Category[form.category.data]

            # Handle photo uploads
            upload_folder = current_app.config['SERVER_PATH']
            new_category_folder = os.path.join(upload_folder, form.category.data)

            if not os.path.exists(new_category_folder):
                os.makedirs(new_category_folder)

            photos = request.files.getlist('photos')
            for photo in photos:
                if photo and allowed_file(photo.filename):
                    filename = secure_filename(photo.filename)
                    photo_path = os.path.join(new_category_folder, filename)
                    photo.save(photo_path)

                    new_photo = Photo(filename=filename, photosession_id=photosession.id)
                    db.session.add(new_photo)

            # Handle photo deletions
            photos_to_delete = request.form.getlist('delete_photos')
            for photo_id in photos_to_delete:
                photo = Photo.query.get(photo_id)
                if photo:
                    os.remove(os.path.join(upload_folder, category_name, photo.filename))
                    db.session.delete(photo)

            db.session.commit()
            current_app.logger.info(f"Photosession updated: {photosession}")
            flash('Фотосессия успешно обновлена', 'success')
            return redirect(url_for('photosession.view_photoshoot', category_name=photosession.category.name, id=photosession.id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating photosession: {str(e)}")
            flash('При обновлении фотосессии произошла ошибка', 'danger')

    # If GET request or form validation fails, render the update form
    return render_template('photosession/update_photoshoot.html', form=form, photosession=photosession)

#показ конкретной фотосессии
@photoshoot_bp.route('/photosessions/<string:category_name>/<int:id>', methods=['GET'])
def view_photoshoot(category_name, id):
    # Проверяем, что категория существует в enum
    try:
        category = Category[category_name]
    except KeyError:
        flash('Категория не найдена', 'danger')
        return redirect(url_for('photosession.list_photoshoots'))

    # Отображаем фотосессию по ID
    photoshoot = Photosession.query.get_or_404(id)

    return render_template('photosession/view_photoshoot.html', photoshoot=photoshoot)


@photoshoot_bp.route('/photosessions', methods=['GET'])
def list_photoshoots():
    page = request.args.get('page', 1, type=int)
    photoshoots = Photosession.query.order_by(Photosession.created_at.desc()).paginate(page=page, per_page=10)
    categories = Category.__members__
    return render_template('photosession/list_photoshoots.html', photoshoots=photoshoots, categories=categories)

#отображение фотосессий  ГОТОВО ОТОБРАЖАЕТ
@photoshoot_bp.route('/photosessions/<string:category_name>', methods=['GET'])
def category_photoshoots(category_name):
    try:
        category = Category[category_name]
    except KeyError:
        flash('Категория не найдена', 'danger')
        return redirect(url_for('photosession.list_photoshoots'))
    # отображение все фотосессии в категории
    page = request.args.get('page', 1, type=int)
    photoshoots = Photosession.query.filter_by(category=category).order_by(Photosession.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('photosession/category_photoshoots.html', photoshoots=photoshoots, category=category.value, category_name=category_name)



