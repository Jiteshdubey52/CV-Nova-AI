# CVNova AI

CVNova AI is a production-minded Flask SaaS for AI-assisted resumes, cover letters, ATS scoring, LinkedIn optimization, interview preparation, exports, and resume version management.

## Tech

- Flask, SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF
- Tailwind CSS, Jinja2, Alpine.js, Chart.js, Lucide
- OpenAI or Gemini through a provider abstraction
- MySQL locally, PostgreSQL on Railway
- PDF and DOCX downloads
- Upload and analyze old PDF, DOCX, or TXT resumes
- Ten modern resume templates with optional and custom sections

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

For local development, paste your key in the app at:

```text
http://127.0.0.1:5000/dashboard/settings
```

Or place it in `.env`:

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
GEMINI_API_KEY=
```

## Railway

Set `SECRET_KEY`, `DATABASE_URL`, `FLASK_ENV=production`, and optional AI/OAuth/mail variables. Railway runs the `Procfile` with Gunicorn.

## Render

Render deployment is configured with `render.yaml`.

1. Push this repository to GitHub.
2. In Render, choose **New > Blueprint**.
3. Connect `Jiteshdubey52/CV-Nova-AI`.
4. Render will create:
   - `cvnova-ai` web service
   - `cvnova-ai-db` Postgres database
5. Add optional secrets in the Render dashboard:
   - `OPENAI_API_KEY`
   - `GEMINI_API_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`

The Render start command runs migrations before starting Gunicorn:

```bash
flask --app app:create_app db upgrade && gunicorn "app:create_app()" --bind 0.0.0.0:$PORT
```
