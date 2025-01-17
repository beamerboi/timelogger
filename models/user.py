from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from datetime import datetime, timedelta
import secrets

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    name = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    verification_token_expires = db.Column(db.DateTime)
    time_logs = db.relationship('TimeLog', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_verification_token(self):
        """Generate and store verification token"""
        print(f"\n=== GENERATING VERIFICATION TOKEN ===")
        print(f"User: {self.email}")

        self.verification_token = secrets.token_urlsafe(32)
        self.verification_token_expires = datetime.utcnow() + timedelta(hours=24)

        print(f"Generated token: {self.verification_token}")
        print(f"Expires at: {self.verification_token_expires}")

        try:
            db.session.add(self)  # Ensure the user is in the session
            db.session.commit()
            print("Token stored successfully")
            return self.verification_token
        except Exception as e:
            db.session.rollback()
            print(f"Error storing verification token: {e}")
            return None

    def verify_email(self):
        """Verify email and clean up token"""
        print(f"\n=== VERIFYING EMAIL FOR USER ===")
        print(f"User: {self.email}")
        print(f"Current token: {self.verification_token}")
        print(f"Token expires: {self.verification_token_expires}")

        if not self.verification_token or not self.verification_token_expires:
            print("No token or expiration date found")
            return False

        if self.verification_token_expires < datetime.utcnow():
            print("Token has expired")
            return False

        self.is_verified = True
        self.verification_token = None
        self.verification_token_expires = None
        print("Email verified successfully")
        return True