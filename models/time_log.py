from datetime import datetime
from extensions import db

class TimeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    jira_ticket = db.Column(db.String(20), nullable=False)
    work_completed = db.Column(db.Text, nullable=False)
    issues_faced = db.Column(db.Text)
    next_steps = db.Column(db.Text)
    hours_spent = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)