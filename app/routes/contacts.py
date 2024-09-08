from flask import Blueprint, render_template

contacts = Blueprint('contacts', __name__)

@contacts.route('/contacts')
def contacts_page():
    return render_template('contacts.html')