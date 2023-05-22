from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = f"sqlite:///./database.db"

    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    # JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)
