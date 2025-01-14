from flask_mail import Message
from extensions import mail
from flask import render_template, current_app, url_for, request

class EmailService:
    @staticmethod
    def send_verification_email(user):
        token = user.generate_verification_token()

        # Get the current host
        host = request.host_url.rstrip('/')
        verification_url = f"{host}{url_for('auth.verify_email', token=token)}"

        msg = Message('Verify your TimeLogger account',
                     recipients=[user.email])

        msg.html = render_template('emails/verify_email.html',
                                 user=user,
                                 verification_url=verification_url)

        mail.send(msg)

    @staticmethod
    def send_reminder(user_email, pending_tickets):
        msg = Message(
            'Daily Time Log Reminder',
            recipients=[user_email]
        )
        msg.html = render_template(
            'emails/reminder.html',
            pending_tickets=pending_tickets
        )
        mail.send(msg)