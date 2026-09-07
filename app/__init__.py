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

    with app.app_context():
        from app import models
        db.create_all()

    return app
