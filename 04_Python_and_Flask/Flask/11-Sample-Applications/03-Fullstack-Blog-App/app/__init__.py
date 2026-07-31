from flask import Flask
from .config import Config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from app.blue_auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.blue_blog.routes import bp as blog_bp
    app.register_blueprint(blog_bp)

    with app.app_context():
        db.create_all()

    return app
