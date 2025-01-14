from flask import Flask
from routes.auth import auth_bp
from routes.main import main_bp
from routes.admin import admin_bp
from extensions import db, login_manager, mail
from models.user import User
from config.config import Config
import logging

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    with app.app_context():
        db.init_app(app)
        db.create_all()

    login_manager.init_app(app)
    mail.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Flask app created")

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)