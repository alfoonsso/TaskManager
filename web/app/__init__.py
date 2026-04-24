from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Instancias globales de las extensiones
# Se inicializan aquí pero se 'enlazan' a la app en create_app()
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.main import main
    from app.routes.projects import projects
    from app.routes.tasks import tasks
    from app.routes.auth import auth
    app.register_blueprint(main)
    app.register_blueprint(projects)
    app.register_blueprint(tasks)
    app.register_blueprint(auth)

    # Importar los modelos para que Flask-Migrate los detecte
    from app import models # noqa: F401

    
    @app.errorhandler(404)
    def pagina_no_encontrada(error):
        return render_template('errores/404.html'), 404
    @app.errorhandler(500)
    def error_interno(error):
        return render_template('errores/500.html'), 500
    @app.context_processor
    def inject_globals():
        from flask import session
        return {'current_user': session.get('usuario', None)}
    
    return app