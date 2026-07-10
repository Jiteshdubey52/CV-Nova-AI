from io import BytesIO

from docx import Document
from pypdf import PdfReader


class UploadResumeService:
    def extract_text(self, filename: str, data: bytes) -> str:
        lower = filename.lower()
        if lower.endswith(".pdf"):
            reader = PdfReader(BytesIO(data))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if lower.endswith(".docx"):
            document = Document(BytesIO(data))
            return "\n".join(paragraph.text for paragraph in document.paragraphs)
        if lower.endswith(".txt"):
            return data.decode("utf-8", errors="ignore")
        raise ValueError("Upload a PDF, DOCX, or TXT resume.")
