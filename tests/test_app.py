from app.extensions import db
from app.models import User


def register(client):
    return client.post(
        "/auth/register",
        data={"name": "Jitesh", "email": "jitesh@example.com", "password": "Password123", "confirm": "Password123"},
        follow_redirects=True,
    )


def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"CVNova AI" in response.data


def test_user_can_register_and_create_resume(client, app):
    response = register(client)
    assert response.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email="jitesh@example.com").first() is not None
    response = client.post("/resumes/new", data={"title": "Software Resume", "target_role": "Flask Developer", "template": "nova"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Software Resume" in response.data
    response = client.get("/resumes/templates")
    assert response.status_code == 200
    assert b"Choose your resume template" in response.data
    response = client.get("/resumes/1/downloads")
    assert response.status_code == 200
    assert b"Download PDF" in response.data
    response = client.get("/resumes/1/export/docx")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/vnd.openxmlformats")
    response = client.get("/resumes/1/export/pdf")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/pdf")


def test_ai_settings_page_accepts_provider_keys(client):
    register(client)
    response = client.post(
        "/dashboard/settings",
        data={"ai_provider": "openai", "openai_api_key": "sk-test", "gemini_api_key": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"AI settings updated" in response.data


def test_password_hashing(app):
    with app.app_context():
        user = User(name="Secure", email="secure@example.com")
        user.set_password("Password123")
        db.session.add(user)
        db.session.commit()
        assert user.password_hash != "Password123"
        assert user.check_password("Password123")
