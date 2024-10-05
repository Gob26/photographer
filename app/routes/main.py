from flask import Blueprint, render_template
from app.extensions import cache
from app.utils.functions import get_random_photosessions  # Рандомные фотосессии

main = Blueprint('main', __name__)

@main.route('/index')
@main.route('/')
@cache.cached(timeout=60 * 60 * 24)  # Кэшируем результат на 24 часа
def index():
    random_photosessions = get_random_photosessions()  # Получаем случайные фотосессии
    return render_template('main/index.html', random_photosessions=random_photosessions, )
