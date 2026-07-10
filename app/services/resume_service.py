from __future__ import annotations

from copy import deepcopy

from app.models import Resume
from app.repositories.resume_repository import ResumeRepository
from app.services.security import clean_text


DEFAULT_CONTENT = {
    "name": "",
    "email": "",
    "phone": "",
    "location": "",
    "summary": "",
    "skills": [],
    "experience": [],
    "education": [],
    "links": [],
}


class ResumeService:
    def __init__(self, repository: ResumeRepository | None = None) -> None:
        self.repository = repository or ResumeRepository()

    def create(self, user_id: int, title: str, target_role: str, template: str = "nova") -> Resume:
        resume = Resume(
            user_id=user_id,
            title=clean_text(title),
            target_role=clean_text(target_role),
            template=template,
            content=deepcopy(DEFAULT_CONTENT),
        )
        resume.ats_score = self.score_resume(resume.content, target_role)
        return self.repository.save(resume)

    def update_content(self, resume: Resume, form: dict[str, str]) -> Resume:
        self.repository.snapshot(resume, "Before update")
        content = deepcopy(resume.content or DEFAULT_CONTENT)
        for field in ["name", "email", "phone", "location", "summary"]:
            content[field] = clean_text(form.get(field, ""))
        content["skills"] = [clean_text(s.strip()) for s in form.get("skills", "").split(",") if s.strip()]
        content["experience"] = self._lines_to_items(form.get("experience", ""))
        content["education"] = self._lines_to_items(form.get("education", ""))
        content["links"] = self._lines_to_items(form.get("links", ""))
        resume.title = clean_text(form.get("title", resume.title))
        resume.target_role = clean_text(form.get("target_role", resume.target_role))
        resume.template = clean_text(form.get("template", resume.template))
        resume.content = content
        resume.ats_score = self.score_resume(content, resume.target_role)
        return self.repository.save(resume)

    def score_resume(self, content: dict, target_role: str = "") -> int:
        score = 30
        if content.get("summary"):
            score += 12
        if len(content.get("skills", [])) >= 6:
            score += 18
        if len(content.get("experience", [])) >= 2:
            score += 18
        if content.get("education"):
            score += 10
        if target_role and target_role.lower() in " ".join(content.get("skills", []) + [content.get("summary", "")]).lower():
            score += 12
        return min(score, 100)

    def compare_to_job(self, resume: Resume, job_description: str) -> dict:
        resume_text = " ".join([resume.content.get("summary", ""), *resume.content.get("skills", [])]).lower()
        jd_words = {word.strip(".,:;()[]").lower() for word in job_description.split() if len(word) > 3}
        matched = sorted([word for word in jd_words if word in resume_text])
        missing = sorted(list(jd_words - set(matched)))[:20]
        score = int((len(matched) / max(len(jd_words), 1)) * 100)
        return {"score": min(score, 100), "matched": matched[:20], "missing": missing}

    def _lines_to_items(self, value: str) -> list[str]:
        return [clean_text(line.strip()) for line in value.splitlines() if line.strip()]
