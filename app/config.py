import os

class Config(object):
    #APPNAME = 'app'
    #ROOT = os.path.abspath(APPNAME)
    #UPLOAD_PATH = '/static/upload/'
    #SERVER_PATH = ROOT + UPLOAD_PATH

    USER = os.environ.get('POSTGRES_USER', 'anna')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'annaanna')
    HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
    PORT = os.environ.get('POSTGRES_PORT', 5432)
    DB = os.environ.get('POSTGRES_DB', 'mydb')

    SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    SECRET_KEY = 'ferf5453rfrgwrs34t46245rf2454tfwrge'
    SQLALCHEMY_TRACK_MODIFICATIONS = True