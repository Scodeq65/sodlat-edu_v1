from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from app.db import db  # Import db from the new module

migrate = Migrate()
login = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'auth.login'

    from app.routes import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    from app.models import User  # Import after db initialization


