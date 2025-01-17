from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from models.user import User
from extensions import db
import re
from services.email_service import EmailService
from datetime import datetime
from forms import RegistrationForm

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
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Send verification email
        EmailService.send_verification_email(user)

        flash('Registration successful! Please check your email to verify your account.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

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