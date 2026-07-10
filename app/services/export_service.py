from io import BytesIO

from docx import Document
from flask import render_template

from app.models import Resume


class ExportService:
    def to_pdf(self, resume: Resume) -> bytes:
        from weasyprint import HTML

        html = render_template("resumes/export.html", resume=resume)
        return HTML(string=html).write_pdf()

    def to_docx(self, resume: Resume) -> bytes:
        document = Document()
        content = resume.content
        document.add_heading(content.get("name") or resume.title, 0)
        document.add_paragraph(content.get("summary", ""))
        document.add_heading("Skills", level=1)
        document.add_paragraph(", ".join(content.get("skills", [])))
        for section in ["experience", "education", "links"]:
            document.add_heading(section.title(), level=1)
            for item in content.get(section, []):
                document.add_paragraph(item, style="List Bullet")
        stream = BytesIO()
        document.save(stream)
        return stream.getvalue()
