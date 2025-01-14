from flask import Blueprint, render_template, flash, current_app, request, redirect, url_for
from flask_login import login_required, current_user
from models.time_log import TimeLog
from services.jira_service import JiraService
from config.config import Config
from extensions import db
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    jira_service = JiraService()
    tickets = jira_service.get_current_sprint_tickets(current_user.email)

    # Get today's date
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())

    # Calculate stats
    today_logs = TimeLog.query.filter(
        TimeLog.user_id == current_user.id,
        TimeLog.date == today
    ).all()

    weekly_logs = TimeLog.query.filter(
        TimeLog.user_id == current_user.id,
        TimeLog.date >= week_start,
        TimeLog.date <= today
    ).all()

    completed_tasks = len(set(log.jira_ticket for log in weekly_logs))
    today_hours = sum(log.hours_spent for log in today_logs)
    weekly_hours = sum(log.hours_spent for log in weekly_logs)

    recent_logs = TimeLog.query.filter_by(user_id=current_user.id)\
        .order_by(TimeLog.date.desc())\
        .limit(10)\
        .all()

    return render_template('dashboard.html',
                         tickets=tickets,
                         recent_logs=recent_logs,
                         today_hours=today_hours,
                         weekly_hours=weekly_hours,
                         completed_tasks=completed_tasks,
                         jira_server=Config.JIRA_SERVER)

@main_bp.route('/log-time', methods=['GET', 'POST'])
@login_required
def log_time():
    # Get current tickets for dropdown
    jira_service = JiraService()
    current_tickets = jira_service.get_current_sprint_tickets(current_user.email)

    if request.method == 'POST':
        # Create the time log instance
        time_log = TimeLog(
            user_id=current_user.id,
            jira_ticket=request.form['jira_ticket'],
            work_completed=request.form['work_completed'],
            issues_faced=request.form['issues_faced'],
            next_steps=request.form['next_steps'],
            hours_spent=float(request.form['hours_spent'])
        )

        try:
            # Log work in Jira first
            comment = f"""Work Completed: {time_log.work_completed}
            Issues Faced: {time_log.issues_faced}
            Next Steps: {time_log.next_steps}"""

            if jira_service.log_work(time_log.jira_ticket, time_log.hours_spent, comment):
                # If Jira logging succeeds, save to database
                with current_app.app_context():
                    db.session.add(time_log)
                    db.session.commit()
                flash('Time logged successfully!', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Failed to log time in Jira.', 'error')
        except Exception as e:
            print(f"Error logging time: {str(e)}")
            flash('An error occurred while logging time.', 'error')

    return render_template('time_log.html', tickets=current_tickets)

@main_bp.route('/debug-config')
@login_required
def debug_config():
    print("\n=== CONFIG DEBUG ===")
    print(f"JIRA_SERVER: {Config.JIRA_SERVER}")
    print(f"JIRA_EMAIL: {Config.JIRA_EMAIL}")
    print(f"JIRA_API_TOKEN: {'Set' if Config.JIRA_API_TOKEN else 'Not Set'}")
    return "Check console for config debug info"