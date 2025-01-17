import os
import sys
from flask import Flask
from extensions import db, login_manager, mail, migrate
from routes.auth import auth_bp
from routes.main import main_bp
from models.user import User
from config import Config

def create_app():
    try:
        app = Flask(__name__)
        
        # Load configuration
        app.config.from_object(Config)
        
        print("Configuration loaded:")
        print(f"DATABASE_URL: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
        print(f"SECRET_KEY set: {'Yes' if app.config.get('SECRET_KEY') else 'No'}")
        print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER', 'Not set')}")
        
        # Initialize extensions
        db.init_app(app)
        login_manager.init_app(app)
        mail.init_app(app)
        migrate.init_app(app, db)
        
        # Register blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        
        # Create tables if they don't exist
        with app.app_context():
            try:
                db.create_all()
                print("Database tables created successfully")
            except Exception as e:
                print(f"Error creating database tables: {str(e)}", file=sys.stderr)
                raise
        
        return app
    except Exception as e:
        print(f"Error creating app: {str(e)}", file=sys.stderr)
        raise

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)