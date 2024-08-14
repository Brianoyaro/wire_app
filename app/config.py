import os
import uuid


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    '''configuration variables'''
    SECRET_KEY = os.getenv('SECRET_KEY') or str(uuid.uuid4())
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False