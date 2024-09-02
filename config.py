import os

class Config:
    """Configuration settings for the application."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///sodlat_edu.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
