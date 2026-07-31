import os
from dataclasses import dataclass

@dataclass
class Config:
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-key-123')
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
