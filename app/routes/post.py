import os
import logging
from crypt import methods

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.utils.functions import allowed_file, generate_unique_slug
from flask_login import login_required
from ..extensions import db
from ..models.post import Post


post = Blueprint('post', __name__)


def save_uploaded_files(files):
    image_paths = []
    # Получаем основную папку для загрузки файлов из конфигурации
    upload_folder = current_app.config['SERVER_PATH']

    # Создаем путь к папке для сохранения фотографий на основе категории
    category_folder = os.path.join(upload_folder, 'blog')

    # Проверяем, существует ли папка для данной категории, если нет — создаем
    if not os.path.exists(category_folder):
        os.makedirs(category_folder)

    for file in files:
        if file and allowed_file(file.filename): # Проверка на допустимый формат
            filename = secure_filename(file.filename)
            file_path = os.path.join(category_folder, filename)
            logging.debug(f"Attempting to save file to: {file_path}")
            try:
                file.save(file_path)
                image_paths.append(filename)
                logging.debug(f"File saved successfully: {file_path}")
            except Exception as e:
                logging.error(f"Error saving file {filename}: {str(e)}")
        else:
            logging.warning(f"Invalid file or format: {file.filename}")
    return image_paths


@post.route('/post', methods=['POST', 'GET'])
def all():
    posts = Post.query.all()
    return render_template('post/all.html', posts=posts)


@post.route('/post/<int:post_id>', methods=['GET'])
def post_detail(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return 'Пост не найден', 404
    return render_template('post/detail.html', post=post)


@post.route('/post/create', methods=['POST', 'GET'])
@login_required
def create():
    if request.method == 'POST':
        title_post = request.form.get('title_post')
        content_post = request.form.get('content_post')
        snippet_post = request.form.get('snippet_post')
        slug = generate_unique_slug(title_post)
        # Обработка новых изображений
        uploaded_files = request.files.getlist('images')
        image_paths = save_uploaded_files(uploaded_files)

        if not image_paths:
            logging.warning("No valid images uploaded.")
            return 'Не загружены допустимые изображения', 400

        post = Post(title=title_post, slug=slug, content=content_post, snippet=snippet_post, images=image_paths)

        try:
            db.session.add(post)
            db.session.commit()
            logging.info(f"Post created successfully: {title_post}")
            return redirect(url_for('post.all'))
        except Exception as e:
            logging.error(f"Error adding post to database: {str(e)}")
            return 'При добавлении поста произошла ошибка', 500
    else:
        return render_template('post/create.html')


@post.route('/post/<int:post_id>/update', methods=['POST', 'GET'])
@login_required
def update(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        post.title = request.form.get('title_post')
        post.content = request.form.get('content_post')
        post.snippet = request.form.get('snippet_post')
        post.slug = generate_unique_slug(Post,post.title)
        # Обработка новых изображений
        uploaded_files = request.files.getlist('images')
        image_paths = save_uploaded_files(uploaded_files)

        if image_paths:
            post.images = image_paths  # Обновляем изображения только если есть новые

        try:
            db.session.commit()
            logging.info(f"Post updated successfully: {post.title}")
            return redirect(url_for('post.all'))#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        except Exception as e:
            logging.error(f"Error updating post: {str(e)}")
            return 'При обновлении поста произошла ошибка', 500

    return render_template('post/update.html', post=post)


@post.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)

    try:
        db.session.delete(post)
        db.session.commit()
        flash('Пост успешно удален', 'success')
        logging.info(f"Post deleted successfully: {post.title}")
        return redirect(url_for('post.all'))
    except Exception as e:
        logging.error(f"Error deleting post: {str(e)}")
        return 'При удалении поста произошла ошибка', 500


