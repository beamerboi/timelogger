from flask import Flask
from config.config import Config
from extensions import db, login_manager, mail
from routes.auth import auth_bp
from routes.main import main_bp
from flask_migrate import Migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Initialize Flask-Migrate
    Migrate(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)