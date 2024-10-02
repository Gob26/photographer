import os
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
            category=category
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
                except Exception as e:
                    flash(f'Ошибка при сохранении фотографии: {str(e)}', 'danger')

        # Сохраняем изменения в базе данных
        db.session.commit()

        # Выводим сообщение об успешном создании фотосессии
        flash('Фотосессия успешно создана!', 'success')

        # Перенаправляем пользователя на страницу созданной фотосессии
        return redirect(
            url_for('photosession.view_photoshoot', category_name=new_photoshoot.category.name, id=new_photoshoot.id))

    # Если метод GET, отображаем форму создания фотосессии
    return render_template('photosession/create_photoshoot.html', form=form, categories=Category)


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

    page = request.args.get('page', 1, type=int)
    photoshoots = Photosession.query.filter_by(category=category).order_by(Photosession.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('photosession/category_photoshoots.html', photoshoots=photoshoots, category=category.value, category_name=category_name)



