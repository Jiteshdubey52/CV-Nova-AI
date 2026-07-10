from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.models import GeneratedDocument
from app.repositories.resume_repository import ResumeRepository
from app.services.ai_service import AIService

bp = Blueprint("ai", __name__)


@bp.post("/resume/<int:resume_id>/<action>")
@login_required
def resume_action(resume_id: int, action: str):
    resume = ResumeRepository().get_for_user(resume_id, current_user.id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    service = AIService()
    text = request.form.get("text", "")
    actions = {
        "summary": lambda: service.summary(resume.content, resume.target_role),
        "experience": lambda: service.rewrite_experience(text, resume.target_role),
        "skills": lambda: service.skill_suggestions(resume.content, resume.target_role),
        "linkedin": lambda: service.linkedin(resume.content, resume.target_role),
        "interview": lambda: service.interview(resume.content, text),
    }
    if action not in actions:
        return jsonify({"error": "Unsupported action"}), 400
    output = actions[action]()
    db.session.add(GeneratedDocument(user_id=current_user.id, resume_id=resume.id, kind=action, title=f"{action.title()} for {resume.title}", body=output))
    db.session.commit()
    return jsonify({"output": output})
