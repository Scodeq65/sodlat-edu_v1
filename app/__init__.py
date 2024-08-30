from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)  # Load configuration from config.py

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    from app.routes import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    return app