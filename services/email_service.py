from flask_mail import Message
from app import mail
from flask import render_template

class EmailService:
    @staticmethod
    def send_reminder(user_email, pending_tickets):
        msg = Message(
            'Daily Time Log Reminder',
            sender='noreply@focus-corporation.com',
            recipients=[user_email]
        )

        msg.html = render_template(
            'emails/reminder.html',
            pending_tickets=pending_tickets
        )

        mail.send(msg)