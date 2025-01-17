import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Required settings with defaults
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail settings with defaults
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # JIRA settings with defaults
    JIRA_SERVER = os.environ.get('JIRA_SERVER', 'https://focus-corporation.atlassian.net')
    JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
    JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')

    # Application settings
    PREFERRED_URL_SCHEME = 'https'  # Changed to https for production
    
    @classmethod
    def init_app(cls, app):
        # Log configuration loading
        print("Loading configuration...")
        for key in dir(cls):
            if not key.startswith('_') and key.isupper():
                value = getattr(cls, key)
                if isinstance(value, str) and 'PASSWORD' not in key and 'KEY' not in key:
                    print(f"{key}: {value}")
                else:
                    print(f"{key}: {'Set' if value else 'Not set'}")