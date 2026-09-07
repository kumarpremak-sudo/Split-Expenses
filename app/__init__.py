from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_name='development'):
    app = Flask(__name__)

    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    db.init_app(app)

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    @app.after_request
    def add_no_cache_headers(response):
        """Prevent HTTP caching for dynamic HTML responses so session checks run on Back button."""
        if response.content_type and 'text/html' in response.content_type:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    with app.app_context():
        from app import models
        db.create_all()

    return app
