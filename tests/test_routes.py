import pytest

from app import create_app, db
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret"


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as test_client:
        yield test_client
    with app.app_context():
        db.drop_all()


def test_landing_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"SkillRadar" in response.data


def test_registration_login_logout(client):
    response = client.post("/register", data={
        "name": "Test Student",
        "email": "student@example.com",
        "password": "password123",
        "college": "Test College",
        "branch": "CSE",
        "academic_year": "3rd Year",
    })
    assert response.status_code == 302

    client.get("/logout")
    response = client.post("/login", data={
        "email": "student@example.com",
        "password": "password123",
    })
    assert response.status_code == 302

    response = client.get("/dashboard")
    assert response.status_code == 200
