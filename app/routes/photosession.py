import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from werkzeug.utils import secure_filename
from flask_login import login_required
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

        # Создаем новый объект фотосессии
        new_photoshoot = Photosession(
            title=form.title.data,
            meta_description=form.meta_description.data,
            content=form.content.data,
            category=category  # Используем категорию из enum
        )

        # Добавляем фотосессию в базу данных
        db.session.add(new_photoshoot)
        db.session.commit()

        # Получаем путь для загрузки файлов из конфигурации
        upload_folder = current_app.config['SERVER_PATH']

        # Проверяем, существует ли папка для загрузки, если нет — создаем
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Обрабатываем загруженные фотографии
        photos = request.files.getlist('photos')
        for photo in photos:
            if photo and allowed_file(photo.filename):
                # Генерируем безопасное имя файла
                filename = secure_filename(photo.filename)

                # Сохраняем файл в нужную директорию
                photo.save(os.path.join(upload_folder, filename))

                # Создаем объект Photo и связываем его с фотосессией
                new_photo = Photo(filename=filename, photosession_id=new_photoshoot.id)
                db.session.add(new_photo)

        # Сохраняем изменения в базе данных
        db.session.commit()

        # Выводим сообщение об успешном создании фотосессии
        flash('Фотосессия успешно создана!', 'success')

        # Перенаправляем пользователя на страницу созданной фотосессии
        return redirect(url_for('photosession.view_photoshoot', id=new_photoshoot.id))

    # Если метод GET, отображаем форму создания фотосессии
    return render_template('photosession/create_photoshoot.html', form=form)

@photoshoot_bp.route('/photoshoot/<int:id>', methods=['GET'])
def view_photoshoot(id):
    # Отображаем фотосессию по ID
    photoshoot = Photosession.query.get_or_404(id)
    return render_template('photosession/view_photoshoot.html', photoshoot=photoshoot)

@photoshoot_bp.route('/photosessions', methods=['GET'])
def list_photoshoots():
    # Отображение всех фотосессий
    photoshoots = Photosession.query.all()
    return render_template('photosession/list_photoshoots.html', photoshoots=photoshoots)

@photoshoot_bp.route('/photosessions/category/<string:category_name>', methods=['GET'])
def category_photoshoots(category_name):
    # Проверяем, что категория существует в enum
    try:
        category = Category[category_name]
    except KeyError:
        flash('Категория не найдена', 'danger')
        return redirect(url_for('photosession.list_photoshoots'))

    # Отбираем фотосессии по категории
    photoshoots = Photosession.query.filter_by(category=category).all()
    return render_template('photosession/category_photoshoots.html', photoshoots=photoshoots, category=category.value)

@photoshoot_bp.route('/photosessions/categories', methods=['GET'])
def list_categories():
    # Отображение всех категорий
    categories = [category for category in Category]
    return render_template('photosession/categories.html', categories=categories)
