from flask import Blueprint, render_template, jsonify, current_app
from app.models.photosession import Photosession

map = Blueprint('map', __name__)

# Маршрут для отображения карты
@map.route('/map')
def map_view():
    return render_template('map/yandex_map.html')

# Маршрут для получения данных фотосессий
@map.route('/map_data')
def map_data():
    # Получаем все фотосессии из базы данных
    photo_sessions = Photosession.query.all()

    # Форматируем базовый путь к фотографиям
    upload_folder = current_app.config['SERVER_PATH']

    # Преобразуем данные в формат JSON
    photo_sessions_data = [
        {
            'coords': [session.latitude, session.longitude],
            'title': session.title,  # Заголовок фотосессии
            'category': session.category.name if session.category else 'Не указана',  # Категория фотосессии
            'description': session.meta_description if session.meta_description else 'Нет описания',
            'session_url': f'http://127.0.0.1:5000/photosessions/{session.category.name}/{session.id}',  # Добавляем ссылку на фотосессию
            'photo_url': f'/static/upload/{session.category.name}/{session.photos[0].filename}' if session.photos else None
        }
        for session in photo_sessions if session.latitude is not None and session.longitude is not None
    ]

    return jsonify({'photo_sessions': photo_sessions_data})
