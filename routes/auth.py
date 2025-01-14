from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from models.user import User
from extensions import db
import re
from services.email_service import EmailService
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    # First check basic email format
    basic_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(basic_pattern, email):
        return False, "Invalid email format"

    # Then check domain
    domain = email.split('@')[1]
    if domain.lower() != 'focus-corporation.com':
        return False, "Only focus-corporation.com email addresses are allowed"

    return True, ""

def validate_password(password):
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, ""

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Update email validation check
        is_valid_email, email_error = validate_email(email)
        if not is_valid_email:
            flash(email_error)
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_verified:
                flash('Please verify your email address before logging in.')
                return render_template('auth/login.html')

            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')

        # Update email validation check
        is_valid_email, email_error = validate_email(email)
        if not is_valid_email:
            flash(email_error)
            return render_template('auth/register.html')

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('auth/register.html')

        # Validate name
        if not name or len(name) < 2 or not re.match(r'^[A-Za-z\s]+$', name):
            flash('Invalid name format (use only letters and spaces)')
            return render_template('auth/register.html')

        # Validate password
        is_valid_password, password_error = validate_password(password)
        if not is_valid_password:
            flash(password_error)
            return render_template('auth/register.html')

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('auth/register.html')

        # Create new user
        user = User(email=email, name=name)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()

            # Send verification email
            try:
                EmailService.send_verification_email(user)
            except Exception as mail_error:
                print(f"Email error: {str(mail_error)}")  # Log email error
                # Even if email fails, we want to keep the user registered
                flash('Account created but verification email could not be sent. Please contact support.')
                return redirect(url_for('auth.login'))

            flash('Registration successful! Please check your email to verify your account.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")  # Log the actual error
            flash('An error occurred during registration. Please try again.')
            return render_template('auth/register.html')

    return render_template('auth/register.html')

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        flash('Invalid verification link.')
        return redirect(url_for('auth.login'))

    if user.verification_token_expires < datetime.utcnow():
        flash('The verification link has expired. Please request a new one.')
        return redirect(url_for('auth.login'))

    try:
        user.verify_email()
        db.session.commit()
        flash('Your email has been verified! You can now log in.')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during verification. Please try again.')

    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))