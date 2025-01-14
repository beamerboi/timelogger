from flask import Flask, request
from config.config import Config
from extensions import db, login_manager, mail
from models.user import User
import sys
import logging

def create_app():
    app = Flask(__name__)

    # Reload config from environment
    Config.reload()
    app.config.from_object(Config)

    with app.app_context():
        # Set up logging to stdout
        app.logger.addHandler(logging.StreamHandler(sys.stdout))
        app.logger.setLevel(logging.INFO)

        print("\nApplication starting...")
        app.logger.info("Flask app created")

        # Initialize extensions
        db.init_app(app)
        login_manager.init_app(app)
        mail.init_app(app)

        # Set up Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            try:
                return User.query.get(int(user_id))
            except Exception as e:
                print(f"Error loading user: {e}")
                return None

        # Register blueprints
        print("\nRegistering blueprints...")
        from routes.auth import auth_bp
        from routes.main import main_bp
        from routes.admin import admin_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(admin_bp)

        # Now we can print routes after registration
        print("\nRegistered routes:")
        for rule in app.url_map.iter_rules():
            print(f"- {rule.endpoint}: {rule.rule}")

        @app.before_request
        def before_request():
            print(f"\nIncoming request: {request.method} {request.path}")

        @app.after_request
        def after_request(response):
            print(f"Response status: {response.status_code}")
            return response

        @app.errorhandler(Exception)
        def handle_exception(e):
            print(f"Unhandled exception: {str(e)}")
            return "An error occurred", 500

        print("\nApplication initialization complete!")

        # Create tables
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)