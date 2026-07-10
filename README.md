# CVNova AI

CVNova AI is a production-minded Flask SaaS for AI-assisted resumes, cover letters, ATS scoring, LinkedIn optimization, interview preparation, exports, and resume version management.

## Tech

- Flask, SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF
- Tailwind CSS, Jinja2, Alpine.js, Chart.js, Lucide
- OpenAI or Gemini through a provider abstraction
- MySQL locally, PostgreSQL on Railway
- PDF and DOCX downloads

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

For XAMPP, create `cvnova_ai` in phpMyAdmin or run:

```bash
C:\xampp\mysql\bin\mysql.exe -u root -e "CREATE DATABASE IF NOT EXISTS cvnova_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

Use this local connection in `.env`:

```bash
DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/cvnova_ai
```

You can also start the app with:

```bash
run_local.bat
```

## AI providers

Open `/dashboard/settings` after signing in to choose OpenAI or Gemini and save a local API key. In production, configure `AI_PROVIDER`, `OPENAI_API_KEY`, and/or `GEMINI_API_KEY` as environment variables.

## Railway

Set `SECRET_KEY`, `DATABASE_URL`, `FLASK_ENV=production`, and optional AI/OAuth/mail variables. Railway runs the `Procfile` with Gunicorn.
