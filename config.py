import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # For demo purposes, SQLite is used here
    SQLALCHEMY_TRACK_MODIFICATIONS = False
