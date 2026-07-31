import os
import pathlib

base_dir = r"c:/Users/owais/OneDrive/Desktop/study material/learning-material/04_Python_and_Flask/Flask"

def append_to_file(rel_path, content):
    path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n\n" + content + "\n")

# 1. Expand API development notes covering Flask-Smorest, Pydantic integration, OpenAPI 3.0 specs, GraphQL with Ariadne, and WebSockets/SocketIO.

api_expansion = """
## Deep A-Z Content Enhancement: Modern API Development

### 1. Flask-Smorest & OpenAPI 3.0 Specs
Flask-smorest provides a robust framework for building REST APIs using OpenAPI 3.0 standards.
- **Auto-generated Documentation**: Integrates with Swagger UI and ReDoc.
- **Validation**: Uses Marshmallow (or Pydantic through plugins) for request/response validation.
- **Pagination & ETag**: Built-in support for standard REST features.

### 2. Pydantic Integration
While Flask traditionally relies on Marshmallow, Pydantic offers faster, type-hint driven validation.
- **Flask-Pydantic**: Provides `@validate()` decorators to automatically parse JSON bodies and query parameters into Pydantic BaseModel instances.
- **Performance**: Rust-based core (V2) ensures minimal overhead.

### 3. GraphQL with Ariadne
Ariadne is a schema-first GraphQL library for Python.
- **Schema-First**: Define schemas using standard GraphQL syntax (`.graphql` files).
- **Resolvers**: Map Python functions directly to schema queries and mutations.
- **Integration**: Easily mount Ariadne's WSGI/ASGI app inside Flask.

### 4. WebSockets and SocketIO
Flask-SocketIO brings bi-directional real-time communication.
- **Transports**: Falls back to long-polling if WebSockets are unavailable.
- **Namespaces & Rooms**: Multiplexing connections and broadcasting to specific subsets of users.
- **Message Queues**: Integrate with Redis or RabbitMQ for multi-worker scaling.
"""

append_to_file("11-Modern-API/API-Enhancement.md", api_expansion)
append_to_file("07-Async-Realtime/Flask-SocketIO.md", "## Enhanced WebSockets Notes\nFlask-SocketIO allows highly concurrent real-time features. Combine with Eventlet or Gevent for production. When scaling beyond one worker, a message queue (Redis/RabbitMQ) is mandatory.")

# 2. Expand background task queue notes (Celery, RQ, Dramatiq) and deployment guides (Gunicorn, Nginx, Docker, CI/CD).

task_queue_expansion = """
## Deep A-Z Content Enhancement: Background Task Queues

### 1. Celery
- **Broker**: RabbitMQ or Redis.
- **Result Backend**: Redis, SQLAlchemy, Memcached.
- **Features**: Crontab scheduling (Celery Beat), task routing, retries, rate limiting.
- **Best Practice**: Keep tasks small and idempotent. Pass IDs, not full ORM objects.

### 2. RQ (Redis Queue)
- **Simplicity**: Lower barrier to entry than Celery.
- **Requirement**: Redis is mandatory.
- **Use Case**: Simple background jobs, email sending, basic image processing.

### 3. Dramatiq
- **Modern Alternative**: Focuses on reliability and simplicity.
- **Broker**: RabbitMQ or Redis.
- **Features**: Built-in retries, actor model, middleware support.
"""
append_to_file("16-Task-Queues/Task-Queues-Enhancement.md", task_queue_expansion)

deployment_expansion = """
## Deep A-Z Content Enhancement: Deployment & CI/CD

### 1. Gunicorn (WSGI Server)
- **Workers**: `gunicorn -w 4 -b 127.0.0.1:8000 app:app` (Rule of thumb: 2 * cores + 1).
- **Worker Types**: Sync (default), Gevent/Eventlet (for IO-bound), Uvicorn (for ASGI/Flask 2.0+ async).

### 2. Nginx (Reverse Proxy)
- **Role**: SSL termination, serving static files, load balancing.
- **Config**: Proxy pass to Gunicorn, set `X-Forwarded-For` headers.

### 3. Docker & Containerization
- **Dockerfile Best Practices**: Use multi-stage builds, alpine or slim base images, run as non-root user.
- **Docker Compose**: Orchestrate Flask, Postgres, Redis, and Celery together.

### 4. CI/CD Pipelines
- **GitHub Actions / GitLab CI**: Automate `pytest`, `flake8`/`black`/`ruff` checks.
- **Deployment**: Push to AWS ECR, deploy via ECS or render.com/Heroku.
"""
append_to_file("07-Deployment/Deployment-Overview.md", deployment_expansion)

# 3. Build a second complete, runnable sample application
app_dir = os.path.join(base_dir, "11-Sample-Applications", "04-RESTful-Microservice-App")
os.makedirs(app_dir, exist_ok=True)

app_py = '''from flask import Flask
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
'''

config_py = '''import os

class Config:
    API_TITLE = "User Microservice API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
'''

models_py = '''from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class UserModel(db.Model):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
'''

schemas_py = '''from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields
from models import db, UserModel

UserBlueprint = Blueprint("users", "users", url_prefix="/users", description="Operations on users")

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)

@UserBlueprint.route("/")
class UserList(UserBlueprint.MethodView):
    @UserBlueprint.response(200, UserSchema(many=True))
    def get(self):
        """List all users"""
        return UserModel.query.all()

    @UserBlueprint.arguments(UserSchema)
    @UserBlueprint.response(201, UserSchema)
    def post(self, user_data):
        """Create a new user"""
        if UserModel.query.filter_by(username=user_data["username"]).first():
            abort(409, message="Username already exists.")
            
        user = UserModel(**user_data)
        db.session.add(user)
        db.session.commit()
        return user

@UserBlueprint.route("/<int:user_id>")
class UserResource(UserBlueprint.MethodView):
    @UserBlueprint.response(200, UserSchema)
    def get(self, user_id):
        """Get user by ID"""
        user = db.session.get(UserModel, user_id)
        if not user:
            abort(404, message="User not found.")
        return user
'''

reqs_txt = '''Flask==3.0.3
flask-smorest==0.42.3
marshmallow==3.21.1
Flask-SQLAlchemy==3.1.1
pytest==8.2.0
'''

dockerfile = '''FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
'''

test_api_py = '''import pytest
from app import create_app
from models import db

@pytest.fixture
def app():
    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        API_TITLE = "Test API"
        API_VERSION = "v1"
        OPENAPI_VERSION = "3.0.2"
        
    app = create_app(TestConfig)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_user(client):
    response = client.post("/users/", json={"username": "testuser", "email": "test@example.com"})
    assert response.status_code == 201
    assert response.json["username"] == "testuser"

def test_get_users(client):
    client.post("/users/", json={"username": "user1", "email": "1@example.com"})
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json) >= 1
'''

def write_file(filename, content):
    with open(os.path.join(app_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

write_file("app.py", app_py)
write_file("config.py", config_py)
write_file("models.py", models_py)
write_file("schemas.py", schemas_py)
write_file("requirements.txt", reqs_txt)
write_file("Dockerfile", dockerfile)

os.makedirs(os.path.join(app_dir, "tests"), exist_ok=True)
with open(os.path.join(app_dir, "tests", "test_api.py"), "w", encoding="utf-8") as f:
    f.write(test_api_py)

print("SUCCESS")
