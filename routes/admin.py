from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.time_log import TimeLog
from models.user import User
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return "Unauthorized", 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/panel')
@login_required
@admin_required
def panel():
    users = User.query.all()
    logs = TimeLog.query.order_by(TimeLog.created_at.desc()).limit(20)
    return render_template('admin/panel.html', users=users, logs=logs)

@admin_bp.route('/stats')
@login_required
@admin_required
def stats():
    return render_template('admin/stats.html')