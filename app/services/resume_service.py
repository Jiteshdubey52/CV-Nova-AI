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
    "hidden_sections": [],
    "custom_sections": [],
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
        content = self.normalized_content(resume.content)
        for field in ["name", "email", "phone", "location", "summary"]:
            content[field] = clean_text(form.get(field, ""))
        content["skills"] = [clean_text(s.strip()) for s in form.get("skills", "").split(",") if s.strip()]
        content["experience"] = self._lines_to_items(form.get("experience", ""))
        content["education"] = self._lines_to_items(form.get("education", ""))
        content["links"] = self._lines_to_items(form.get("links", ""))
        content["hidden_sections"] = [section for section in ["summary", "skills", "experience", "education", "links"] if form.get(f"show_{section}") != "on"]
        custom_sections: list[dict[str, str | list[str]]] = []
        for index in range(1, 4):
            title = clean_text(form.get(f"custom_title_{index}", ""))
            body = self._lines_to_items(form.get(f"custom_body_{index}", ""))
            if title and body:
                custom_sections.append({"title": title, "items": body})
        content["custom_sections"] = custom_sections
        resume.title = clean_text(form.get("title", resume.title))
        resume.target_role = clean_text(form.get("target_role", resume.target_role))
        resume.template = clean_text(form.get("template", resume.template))
        resume.content = content
        resume.ats_score = self.score_resume(content, resume.target_role)
        return self.repository.save(resume)

    def normalized_content(self, content: dict | None) -> dict:
        merged = deepcopy(DEFAULT_CONTENT)
        if content:
            merged.update(content)
        merged.setdefault("hidden_sections", [])
        merged.setdefault("custom_sections", [])
        return merged

    def create_from_upload(self, user_id: int, title: str, target_role: str, uploaded_text: str, template: str = "nova") -> Resume:
        parsed = self.parse_uploaded_resume(uploaded_text)
        resume = Resume(
            user_id=user_id,
            title=clean_text(title),
            target_role=clean_text(target_role),
            template=template,
            content=parsed,
        )
        resume.ats_score = self.score_resume(parsed, target_role)
        return self.repository.save(resume)

    def parse_uploaded_resume(self, text: str) -> dict:
        content = deepcopy(DEFAULT_CONTENT)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if lines:
            content["name"] = clean_text(lines[0][:120])
        for line in lines:
            if "@" in line and not content["email"]:
                content["email"] = clean_text(line[:120])
            if any(char.isdigit() for char in line) and len(line) <= 40 and not content["phone"]:
                content["phone"] = clean_text(line)
        joined = " ".join(lines)
        content["summary"] = clean_text(joined[:700])
        likely_skills = [
            "Python", "Flask", "Django", "SQL", "MySQL", "PostgreSQL", "JavaScript", "React", "AI",
            "Machine Learning", "APIs", "Git", "Docker", "AWS", "Communication", "Leadership",
        ]
        content["skills"] = [skill for skill in likely_skills if skill.lower() in joined.lower()][:12]
        content["experience"] = [clean_text(line) for line in lines[1:8]]
        return content

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
