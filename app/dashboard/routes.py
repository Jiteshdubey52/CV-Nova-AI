import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import GeneratedDocument, Resume
from app.services.ai_service import AIService

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
    if request.method == "POST":
        provider = request.form.get("ai_provider", "openai")
        openai_key = request.form.get("openai_api_key", "").strip()
        gemini_key = request.form.get("gemini_api_key", "").strip()
        current_app.config["AI_PROVIDER"] = provider
        if openai_key:
            current_app.config["OPENAI_API_KEY"] = openai_key
        if gemini_key:
            current_app.config["GEMINI_API_KEY"] = gemini_key
        if not current_app.config.get("TESTING") and os.getenv("FLASK_ENV") != "production":
            update_local_env(provider, openai_key, gemini_key)
        flash("AI settings updated for this local environment.", "success")
        return redirect(url_for("dashboard.settings"))
    return render_template("dashboard/settings.html", ai_status=AIService().status())


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("dashboard/profile.html")


def update_local_env(provider: str, openai_key: str, gemini_key: str) -> None:
    env_path = os.path.join(current_app.root_path, "..", ".env")
    existing: dict[str, str] = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as file:
            for line in file:
                if "=" in line and not line.lstrip().startswith("#"):
                    key, value = line.rstrip("\n").split("=", 1)
                    existing[key] = value
    existing["AI_PROVIDER"] = provider
    if openai_key:
        existing["OPENAI_API_KEY"] = openai_key
    if gemini_key:
        existing["GEMINI_API_KEY"] = gemini_key
    with open(env_path, "w", encoding="utf-8") as file:
        for key, value in existing.items():
            file.write(f"{key}={value}\n")
