from flask import Flask
from flask_smorest import Api
from config import Config
from models import db
from schemas import UserBlueprint

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    api = Api(app)
    
    api.register_blueprint(UserBlueprint)
    
    with app.app_context():
        db.create_all()
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0")
