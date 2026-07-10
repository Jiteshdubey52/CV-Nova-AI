from app.extensions import db
from app.models import Resume, ResumeVersion


class ResumeRepository:
    def list_for_user(self, user_id: int) -> list[Resume]:
        return Resume.query.filter_by(user_id=user_id).order_by(Resume.updated_at.desc()).all()

    def get_for_user(self, resume_id: int, user_id: int) -> Resume | None:
        return Resume.query.filter_by(id=resume_id, user_id=user_id).first()

    def save(self, resume: Resume) -> Resume:
        db.session.add(resume)
        db.session.commit()
        return resume

    def delete(self, resume: Resume) -> None:
        db.session.delete(resume)
        db.session.commit()

    def snapshot(self, resume: Resume, label: str) -> ResumeVersion:
        version = ResumeVersion(
            resume_id=resume.id,
            label=label,
            content=resume.content,
            ats_score=resume.ats_score,
        )
        db.session.add(version)
        db.session.commit()
        return version
