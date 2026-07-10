from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.models import GeneratedDocument, Resume

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.updated_at.desc()).all()
    documents = GeneratedDocument.query.filter_by(user_id=current_user.id).order_by(GeneratedDocument.created_at.desc()).limit(5).all()
    avg_score = round(sum(r.ats_score for r in resumes) / len(resumes)) if resumes else 0
    return render_template("dashboard/index.html", resumes=resumes, documents=documents, avg_score=avg_score)


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    return render_template("dashboard/settings.html")


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("dashboard/profile.html")
