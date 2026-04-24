import os

basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-taskmanager-inseguracambiar'
    
    # Ruta del archivo SQLite — se crea automáticamente si no existe
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'taskmanager.db')
    # Desactivar el seguimiento de modificaciones (ahorra memoria)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
