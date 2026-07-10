from __future__ import annotations

from flask import current_app


class AIProvider:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=current_app.config["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return response.choices[0].message.content or ""


class GeminiProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        import google.generativeai as genai

        genai.configure(api_key=current_app.config["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text or ""


class LocalProvider(AIProvider):
    def generate(self, prompt: str) -> str:
        lower = prompt.lower()
        if "suggest 12 ats skills" in lower:
            return "Python, Flask, SQLAlchemy, REST APIs, MySQL, PostgreSQL, AI Integration, Prompt Engineering, Resume Optimization, Data Analysis, GitHub, Deployment"
        if "linkedin" in lower:
            return (
                "Headline: Software Developer | AI Enthusiast | Flask, Python, SQL and Career-Tech Builder\n\n"
                "About: I build practical software products that combine clean engineering with useful AI workflows. "
                "My focus is shipping reliable web apps, improving user experience, and turning ideas into production-ready tools.\n\n"
                "Featured ideas: CVNova AI demo, resume optimization case study, GitHub project walkthrough, and a post about building AI career tools."
            )
        if "cover letter" in lower:
            return (
                "Dear Hiring Team,\n\n"
                "I am excited to apply for this opportunity. My experience, practical delivery mindset, "
                "and ability to communicate technical impact make me a strong fit for the role. "
                "I would welcome the chance to bring measurable value to your team.\n\n"
                "Sincerely,\nCVNova AI"
            )
        if "interview" in lower:
            return (
                "1. Walk me through the most relevant project on your resume.\n"
                "Talk track: Explain the problem, your ownership, technical choices, measurable result, and what you improved after feedback.\n\n"
                "2. How do you handle unclear requirements?\n"
                "Talk track: Mention clarifying goals, proposing a small prototype, validating with users, and documenting decisions.\n\n"
                "3. Describe a technical tradeoff.\n"
                "Talk track: Compare speed, maintainability, cost, and risk, then explain why your decision fit the product stage."
            )
        return (
            "Results-driven professional with experience building reliable software products, translating requirements into usable features, "
            "and applying AI thoughtfully to improve productivity, quality, and business outcomes."
        )


class AIService:
    def provider(self) -> AIProvider:
        selected = current_app.config.get("AI_PROVIDER", "openai")
        if selected == "gemini" and current_app.config.get("GEMINI_API_KEY"):
            return GeminiProvider()
        if selected == "openai" and current_app.config.get("OPENAI_API_KEY"):
            return OpenAIProvider()
        return LocalProvider()

    def status(self) -> dict[str, str | bool]:
        selected = current_app.config.get("AI_PROVIDER", "openai")
        has_openai = bool(current_app.config.get("OPENAI_API_KEY"))
        has_gemini = bool(current_app.config.get("GEMINI_API_KEY"))
        configured = (selected == "openai" and has_openai) or (selected == "gemini" and has_gemini)
        return {
            "provider": selected,
            "configured": configured,
            "openai_ready": has_openai,
            "gemini_ready": has_gemini,
            "message": "Live AI is connected." if configured else "Add an OpenAI or Gemini API key to enable live AI generation.",
        }

    def summary(self, resume_content: dict, target_role: str) -> str:
        return self.provider().generate(f"Write a concise ATS-friendly resume summary for {target_role}. Resume: {resume_content}. Return only the final summary.")

    def rewrite_experience(self, text: str, target_role: str) -> str:
        return self.provider().generate(f"Rewrite this resume experience for {target_role} with metrics and action verbs: {text}")

    def skill_suggestions(self, resume_content: dict, target_role: str) -> str:
        return self.provider().generate(f"Suggest 12 ATS skills for {target_role}. Resume: {resume_content}. Return a comma-separated list.")

    def cover_letter(self, resume_content: dict, job_description: str) -> str:
        return self.provider().generate(f"Generate a professional cover letter. Resume: {resume_content}. Job: {job_description}")

    def linkedin(self, resume_content: dict, target_role: str) -> str:
        return self.provider().generate(f"Improve LinkedIn headline, about section, and featured content for {target_role}: {resume_content}")

    def interview(self, resume_content: dict, job_description: str) -> str:
        return self.provider().generate(f"Create interview prep questions and model talking points. Resume: {resume_content}. Job: {job_description}")
