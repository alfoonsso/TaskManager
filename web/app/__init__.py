from flask import Flask, render_template
from config import Config
def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)
    from app.routes.main import main
    from app.routes.projects import projects
    from app.routes.tasks import tasks
    from app.routes.auth import auth
    app.register_blueprint(main)
    app.register_blueprint(projects)
    app.register_blueprint(tasks)
    app.register_blueprint(auth)
    
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