from flask import Blueprint, render_template
import os
import logging
from crypt import methods

from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from app.utils.functions import allowed_file
from flask_login import login_required
from ..extensions import db
from ..models.post import PhotoSession


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
