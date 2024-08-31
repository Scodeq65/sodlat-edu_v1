from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from app.db import db

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
    app.register_blueprint(main.bp, url_prefix='/main')
    app.register_blueprint(auth.bp, url_prefix='/auth')

    from app.models import User

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    return app
