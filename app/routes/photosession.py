from flask import Blueprint, render_template

photosession_all = Blueprint('photosession', __name__)

@photosession_all.route('/photosession_all')
def photosession_page_all():
    return render_template('photosession/photosession_all.html')


@photosession_all.route('/photosession/<int:id>')
def photosession_page(id):
    # Здесь вы можете загружать информацию о конкретной фотосессии из базы данных
    # Например, используя SQLAlchemy или другой ORM
    # photo_session = PhotoSession.query.get(id)
    # Передайте информацию в шаблон
    return render_template('photosession/photosession_detail.html', id=id)
