import os
from dotenv import load_dotenv

load_dotenv()  # Reload environment variables

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Jira settings
    JIRA_SERVER = os.environ.get('JIRA_SERVER')
    JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
    JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')

    @classmethod
    def reload(cls):
        """Reload configuration from environment variables"""
        load_dotenv()
        print("\nLoading configuration:")
        print(f"JIRA_EMAIL: {os.environ.get('JIRA_EMAIL')}")
        print(f"JIRA_SERVER: {os.environ.get('JIRA_SERVER')}")
        print(f"Token exists: {'Yes' if os.environ.get('JIRA_API_TOKEN') else 'No'}")
        cls.SECRET_KEY = os.environ.get('SECRET_KEY')
        cls.SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        cls.MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
        cls.MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
        cls.JIRA_SERVER = os.environ.get('JIRA_SERVER')
        cls.JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
        cls.JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')