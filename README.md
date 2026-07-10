# CVNova AI

CVNova AI is a production-minded Flask SaaS for AI-assisted resumes, cover letters, ATS scoring, LinkedIn optimization, interview preparation, exports, and resume version management.

## Tech

- Flask, SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF
- Tailwind CSS, Jinja2, Alpine.js, Chart.js, Lucide
- OpenAI or Gemini through a provider abstraction
- MySQL locally, PostgreSQL on Railway

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
flask --app app:create_app db init
flask --app app:create_app db migrate -m "initial schema"
flask --app app:create_app db upgrade
flask --app app:create_app run
```

## Railway

Set `SECRET_KEY`, `DATABASE_URL`, `FLASK_ENV=production`, and optional AI/OAuth/mail variables. Railway runs the `Procfile` with Gunicorn.
