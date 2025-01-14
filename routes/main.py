from flask import Blueprint, render_template, flash, current_app, request, redirect, url_for
from flask_login import login_required, current_user
from models.time_log import TimeLog
from services.jira_service import JiraService
from config.config import Config
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

main_bp = Blueprint('main', __name__)
db = SQLAlchemy()

@main_bp.route('/')
@login_required
def dashboard():
    print("\n" + "#" * 80)
    print("DASHBOARD ROUTE ACCESSED")
    print("#" * 80)
    print(f"Current User: {current_user.email}")
    print(f"Current Time: {datetime.now()}")

    # Debug print for config
    print("\nJIRA CONFIG:")
    print(f"JIRA_SERVER: {Config.JIRA_SERVER}")
    print(f"JIRA_EMAIL: {Config.JIRA_EMAIL}")
    print(f"JIRA_API_TOKEN exists: {'Yes' if Config.JIRA_API_TOKEN else 'No'}")

    try:
        print("\nINITIALIZING JIRA SERVICE...")
        jira_service = JiraService()

        if not jira_service.jira:
            print("ERROR: Jira client was not initialized!")
            flash("Failed to initialize Jira client.", "error")
            return render_template('dashboard.html',
                                tickets=[],
                                recent_logs=[],
                                Config=Config)

        print("\nTESTING JIRA CONNECTION...")
        if not jira_service.test_connection():
            print("ERROR: Jira connection test failed!")
            flash("Unable to connect to Jira.", "error")
            return render_template('dashboard.html',
                                tickets=[],
                                recent_logs=[],
                                Config=Config)

        print("\nFETCHING TICKETS...")
        current_tickets = jira_service.get_current_sprint_tickets(current_user.email)
        print(f"Retrieved {len(current_tickets) if current_tickets else 0} tickets")

    except Exception as e:
        import traceback
        print("\nERROR IN DASHBOARD ROUTE:")
        print(traceback.format_exc())
        flash("An error occurred while fetching Jira data.", "error")
        return render_template('dashboard.html',
                            tickets=[],
                            recent_logs=[],
                            Config=Config)

    print("\nFETCHING RECENT LOGS...")
    recent_logs = TimeLog.query.filter_by(user_id=current_user.id)\
        .order_by(TimeLog.created_at.desc())\
        .limit(5)

    print("\nRENDERING TEMPLATE...")
    print("#" * 80 + "\n")

    return render_template('dashboard.html',
                         tickets=current_tickets,
                         recent_logs=recent_logs,
                         Config=Config)

@main_bp.route('/log-time', methods=['GET', 'POST'])
@login_required
def log_time():
    if request.method == 'POST':
        time_log = TimeLog(
            user_id=current_user.id,
            jira_ticket=request.form['jira_ticket'],
            work_completed=request.form['work_completed'],
            issues_faced=request.form['issues_faced'],
            next_steps=request.form['next_steps'],
            hours_spent=float(request.form['hours_spent'])
        )

        db.session.add(time_log)

        # Log work in Jira
        jira_service = JiraService()
        comment = f"""Work Completed: {time_log.work_completed}
        Issues Faced: {time_log.issues_faced}
        Next Steps: {time_log.next_steps}"""

        if jira_service.log_work(time_log.jira_ticket, time_log.hours_spent, comment):
            db.session.commit()
            flash('Time logged successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            db.session.rollback()
            flash('Failed to log time in Jira.', 'error')

    return render_template('time_log.html')

@main_bp.route('/debug-config')
@login_required
def debug_config():
    print("\n=== CONFIG DEBUG ===")
    print(f"JIRA_SERVER: {Config.JIRA_SERVER}")
    print(f"JIRA_EMAIL: {Config.JIRA_EMAIL}")
    print(f"JIRA_API_TOKEN: {'Set' if Config.JIRA_API_TOKEN else 'Not Set'}")
    return "Check console for config debug info"