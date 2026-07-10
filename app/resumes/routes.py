from flask import Blueprint, Response, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import GeneratedDocument, Resume
from app.repositories.resume_repository import ResumeRepository
from app.services.ai_service import AIService
from app.services.export_service import ExportService
from app.services.resume_service import ResumeService
from app.services.upload_service import UploadResumeService

bp = Blueprint("resumes", __name__)

TEMPLATES = [
    {
        "id": "nova",
        "name": "Nova",
        "best_for": "Modern software, AI, data, and product roles",
        "tone": "Clean, keyword-dense, high signal",
    },
    {
        "id": "linear",
        "name": "Linear",
        "best_for": "Operations, analyst, and business roles",
        "tone": "Structured, compact, recruiter friendly",
    },
    {
        "id": "executive",
        "name": "Executive",
        "best_for": "Senior engineering, leadership, and consulting",
        "tone": "Premium, impact-led, strategic",
    },
    {"id": "atlas", "name": "Atlas", "best_for": "Global enterprise and consulting roles", "tone": "Authoritative, polished, balanced"},
    {"id": "signal", "name": "Signal", "best_for": "Startup, product, and growth roles", "tone": "Sharp, lean, outcome-first"},
    {"id": "aura", "name": "Aura", "best_for": "Creative, marketing, and brand roles", "tone": "Elegant, expressive, readable"},
    {"id": "forge", "name": "Forge", "best_for": "Engineering, DevOps, and infrastructure", "tone": "Technical, dense, credibility-led"},
    {"id": "clarity", "name": "Clarity", "best_for": "Freshers, internships, and campus placements", "tone": "Simple, clean, achievement-focused"},
    {"id": "summit", "name": "Summit", "best_for": "Management, program, and operations leaders", "tone": "Executive, strategic, metrics-heavy"},
    {"id": "pulse", "name": "Pulse", "best_for": "Sales, support, and customer success", "tone": "Energetic, measurable, people-centered"},
]


@bp.route("/")
@login_required
def index():
    resumes = ResumeRepository().list_for_user(current_user.id)
    return render_template("resumes/index.html", resumes=resumes)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        resume = ResumeService().create(current_user.id, request.form["title"], request.form.get("target_role", ""), request.form.get("template", "nova"))
        flash("Resume created.", "success")
        return redirect(url_for("resumes.edit", resume_id=resume.id))
    selected_template = request.args.get("template", "nova")
    return render_template("resumes/new.html", templates=TEMPLATES, selected_template=selected_template)


@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        file = request.files.get("resume_file")
        if not file or not file.filename:
            flash("Choose a PDF, DOCX, or TXT resume to upload.", "warning")
            return redirect(url_for("resumes.upload"))
        try:
            text = UploadResumeService().extract_text(file.filename, file.read())
            resume = ResumeService().create_from_upload(
                current_user.id,
                request.form.get("title") or "Imported resume",
                request.form.get("target_role", ""),
                text,
                request.form.get("template", "nova"),
            )
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("resumes.upload"))
        flash("Resume imported and analyzed. Review the extracted details before downloading.", "success")
        return redirect(url_for("resumes.edit", resume_id=resume.id))
    return render_template("resumes/upload.html", templates=TEMPLATES)


@bp.route("/templates")
@login_required
def templates():
    return render_template("resumes/templates.html", templates=TEMPLATES)


@bp.route("/<int:resume_id>")
@login_required
def detail(resume_id: int):
    resume = _resume_or_404(resume_id)
    resume.content = ResumeService().normalized_content(resume.content)
    return render_template("resumes/detail.html", resume=resume, ai_status=AIService().status())


@bp.route("/<int:resume_id>/edit", methods=["GET", "POST"])
@login_required
def edit(resume_id: int):
    resume = _resume_or_404(resume_id)
    if request.method == "POST":
        ResumeService().update_content(resume, request.form)
        flash("Resume updated.", "success")
        return redirect(url_for("resumes.detail", resume_id=resume.id))
    resume.content = ResumeService().normalized_content(resume.content)
    return render_template("resumes/edit.html", resume=resume, templates=TEMPLATES)


@bp.route("/<int:resume_id>/delete", methods=["POST"])
@login_required
def delete(resume_id: int):
    resume = _resume_or_404(resume_id)
    ResumeRepository().delete(resume)
    flash("Resume deleted.", "info")
    return redirect(url_for("resumes.index"))


@bp.route("/<int:resume_id>/versions")
@login_required
def versions(resume_id: int):
    resume = _resume_or_404(resume_id)
    return render_template("resumes/versions.html", resume=resume)


@bp.route("/<int:resume_id>/match", methods=["GET", "POST"])
@login_required
def match(resume_id: int):
    resume = _resume_or_404(resume_id)
    result = None
    if request.method == "POST":
        result = ResumeService().compare_to_job(resume, request.form.get("job_description", ""))
    return render_template("resumes/match.html", resume=resume, result=result)


@bp.route("/<int:resume_id>/downloads")
@login_required
def downloads(resume_id: int):
    resume = _resume_or_404(resume_id)
    resume.content = ResumeService().normalized_content(resume.content)
    return render_template("resumes/downloads.html", resume=resume)


@bp.route("/<int:resume_id>/compare")
@login_required
def compare(resume_id: int):
    resume = _resume_or_404(resume_id)
    latest = resume.versions[-1] if resume.versions else None
    return render_template("resumes/compare.html", resume=resume, latest=latest)


@bp.route("/<int:resume_id>/export/<kind>")
@login_required
def export(resume_id: int, kind: str):
    resume = _resume_or_404(resume_id)
    resume.content = ResumeService().normalized_content(resume.content)
    exporter = ExportService()
    if kind == "pdf":
        return Response(exporter.to_pdf(resume), mimetype="application/pdf", headers={"Content-Disposition": f"attachment; filename={resume.title}.pdf"})
    if kind == "docx":
        from io import BytesIO

        return send_file(BytesIO(exporter.to_docx(resume)), as_attachment=True, download_name=f"{resume.title}.docx")
    abort(404)


@bp.route("/<int:resume_id>/cover-letter", methods=["GET", "POST"])
@login_required
def cover_letter(resume_id: int):
    resume = _resume_or_404(resume_id)
    output = None
    if request.method == "POST":
        output = AIService().cover_letter(resume.content, request.form.get("job_description", ""))
        db.session.add(GeneratedDocument(user_id=current_user.id, resume_id=resume.id, kind="cover_letter", title=f"Cover letter for {resume.title}", body=output))
        db.session.commit()
    return render_template("resumes/cover_letter.html", resume=resume, output=output)


@bp.route("/<int:resume_id>/linkedin", methods=["GET", "POST"])
@login_required
def linkedin(resume_id: int):
    resume = _resume_or_404(resume_id)
    output = None
    if request.method == "POST":
        output = AIService().linkedin(resume.content, resume.target_role)
        db.session.add(GeneratedDocument(user_id=current_user.id, resume_id=resume.id, kind="linkedin", title=f"LinkedIn optimization for {resume.title}", body=output))
        db.session.commit()
    return render_template("resumes/linkedin.html", resume=resume, output=output)


@bp.route("/<int:resume_id>/interview", methods=["GET", "POST"])
@login_required
def interview(resume_id: int):
    resume = _resume_or_404(resume_id)
    output = None
    if request.method == "POST":
        output = AIService().interview(resume.content, request.form.get("job_description", ""))
        db.session.add(GeneratedDocument(user_id=current_user.id, resume_id=resume.id, kind="interview", title=f"Interview prep for {resume.title}", body=output))
        db.session.commit()
    return render_template("resumes/interview.html", resume=resume, output=output)


def _resume_or_404(resume_id: int) -> Resume:
    resume = ResumeRepository().get_for_user(resume_id, current_user.id)
    if not resume:
        abort(404)
    return resume
