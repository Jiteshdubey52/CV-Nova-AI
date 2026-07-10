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
        if "cover letter" in lower:
            return (
                "Dear Hiring Team,\n\n"
                "I am excited to apply for this opportunity. My experience, practical delivery mindset, "
                "and ability to communicate technical impact make me a strong fit for the role. "
                "I would welcome the chance to bring measurable value to your team.\n\n"
                "Sincerely,\nCVNova AI"
            )
        if "interview" in lower:
            return "Prepare these: 1. Tell me about your strongest project. 2. How do you prioritize under pressure? 3. Explain a technical tradeoff you made. 4. What impact did your work create?"
        return "Results-driven professional with a record of building reliable solutions, collaborating across teams, and turning complex requirements into measurable business outcomes."


class AIService:
    def provider(self) -> AIProvider:
        selected = current_app.config.get("AI_PROVIDER", "openai")
        if selected == "gemini" and current_app.config.get("GEMINI_API_KEY"):
            return GeminiProvider()
        if selected == "openai" and current_app.config.get("OPENAI_API_KEY"):
            return OpenAIProvider()
        return LocalProvider()

    def summary(self, resume_content: dict, target_role: str) -> str:
        return self.provider().generate(f"Write a concise ATS-friendly resume summary for {target_role}. Resume: {resume_content}")

    def rewrite_experience(self, text: str, target_role: str) -> str:
        return self.provider().generate(f"Rewrite this resume experience for {target_role} with metrics and action verbs: {text}")

    def skill_suggestions(self, resume_content: dict, target_role: str) -> str:
        return self.provider().generate(f"Suggest 12 ATS skills for {target_role}. Resume: {resume_content}")

    def cover_letter(self, resume_content: dict, job_description: str) -> str:
        return self.provider().generate(f"Generate a professional cover letter. Resume: {resume_content}. Job: {job_description}")

    def linkedin(self, resume_content: dict, target_role: str) -> str:
        return self.provider().generate(f"Improve LinkedIn headline, about section, and featured content for {target_role}: {resume_content}")

    def interview(self, resume_content: dict, job_description: str) -> str:
        return self.provider().generate(f"Create interview prep questions and model talking points. Resume: {resume_content}. Job: {job_description}")
