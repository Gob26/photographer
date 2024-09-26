from flask import Blueprint, render_template
import os
import logging
from crypt import methods

from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from app.utils.functions import allowed_file
from flask_login import login_required
from ..extensions import db



photoshoot_bp = Blueprint('photosession', __name__)

@photoshoot_bp.route('/photoshoot/create', methods=['GET', 'POST'])
def create_photoshoot():
    if request.method == 'POST':
        title = request.form.get('title')
        meta_description = request.form.get('meta_description')
        content = request.form.get('content')
    return render_template('create_photoshoot.html')


