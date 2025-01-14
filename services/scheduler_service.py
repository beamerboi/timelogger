from datetime import datetime
from app import scheduler
from services.email_service import EmailService
from services.jira_service import JiraService
from models.user import User

def send_daily_reminders():
    jira_service = JiraService()
    email_service = EmailService()

    users = User.query.filter(
        User.email.endswith('@focus-corporation.com')
    ).all()

    for user in users:
        pending_tickets = jira_service.get_current_sprint_tickets(user.email)
        if pending_tickets:
            email_service.send_reminder(user.email, pending_tickets)

def init_scheduler():
    scheduler.add_job(
        send_daily_reminders,
        'cron',
        hour=16,
        minute=30,
        id='daily_reminder'
    )