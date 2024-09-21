from flask import Blueprint, render_template, request
from werkzeug.utils import redirect

from ..extensions import db
from ..models.post import Post

post = Blueprint('post', __name__)

# Получаем все посты
@post.route('/post', methods=['POST', 'GET'])
def all():
    posts = Post.query.all()   # берем все статьи
    return render_template('post/all.html', posts=posts)  # передаем посты

# Получаем детали поста
@post.route('/post/<int:post_id>', methods=['GET'])
def post_detail(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return 'Пост не найден', 404
    return render_template('post/detail.html', post=post)

# Создание поста
@post.route('/post/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title_post = request.form.get('title_post')
        content_post = request.form.get('content_post')
        snippet_post = request.form.get('snippet_post')


        post = Post(title=title_post, content=content_post, snippet=snippet_post)
        
        try:
            db.session.add(post)
            db.session.commit()
            return redirect('/post')
        except Exception as e:
            print(f'Ошибка при добавлении поста: {str(e)}')
            return 'При добавлении поста произошла ошибка'

    else:
        # Если метод GET, просто отображаем форму
        return render_template('post/create.html')
