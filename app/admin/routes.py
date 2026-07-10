from functools import wraps

from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required

from app.models import GeneratedDocument, Resume, User

bp = Blueprint("admin", __name__)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@bp.route("/")
@login_required
@admin_required
def index():
    stats = {
        "users": User.query.count(),
        "resumes": Resume.query.count(),
        "documents": GeneratedDocument.query.count(),
        "verified": User.query.filter_by(is_email_verified=True).count(),
    }
    users = User.query.order_by(User.created_at.desc()).limit(20).all()
    return render_template("admin/index.html", stats=stats, users=users)
