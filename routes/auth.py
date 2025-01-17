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
            # First save the user
            db.session.add(user)
            db.session.commit()

            # Generate and send verification email in a separate transaction
            try:
                # Create a new session to ensure token is stored
                db.session.begin_nested()
                
                if not EmailService.send_verification_email(user):
                    db.session.rollback()
                    flash('Account created but verification email could not be sent. Please use the resend verification option.')
                else:
                    db.session.commit()
                    flash('Registration successful! Please check your email to verify your account.')
                
                return redirect(url_for('auth.login'))
                
            except Exception as mail_error:
                db.session.rollback()
                print(f"Email error: {str(mail_error)}")
                flash('Account created but verification email could not be sent. Please use the resend verification option.')
                return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.')
            return render_template('auth/register.html')

    return render_template('auth/register.html')

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    print(f"\n=== VERIFYING EMAIL ===")
    print(f"Token received: {token}")
    
    if not token:
        print("No token provided")
        flash('Invalid verification link.', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(verification_token=token).first()
    print(f"User found: {user is not None}")
    
    if not user:
        print("No user found with this token")
        flash('Invalid verification link or account already verified.', 'error')
        return redirect(url_for('auth.login'))

    try:
        if user.verify_email():
            db.session.commit()
            print("Email verified successfully")
            login_user(user)  # Automatically log in the user
            return render_template('auth/verification_success.html', user=user)
        else:
            print("Verification failed - token expired or invalid")
            flash('Verification link has expired. Please request a new one.', 'error')
            return redirect(url_for('auth.login'))
    except Exception as e:
        db.session.rollback()
        print(f"Error during verification: {e}")
        flash('An error occurred during verification. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/resend-verification')
def resend_verification():
    """Add this new route to handle resending verification emails"""
    email = request.args.get('email')
    if not email:
        flash('Email address is required.', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email, is_verified=False).first()
    if not user:
        flash('Invalid email or account already verified.', 'error')
        return redirect(url_for('auth.login'))

    try:
        if EmailService.send_verification_email(user):
            flash('Verification email has been resent. Please check your inbox.', 'success')
        else:
            flash('Failed to send verification email. Please try again.', 'error')
    except Exception as e:
        print(f"Error resending verification: {e}")
        flash('An error occurred. Please try again later.', 'error')

    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))