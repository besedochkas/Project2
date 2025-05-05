from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine
from app import models

client = TestClient(app)


def setup_module():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Проверка: если жанр уже есть — используем его, иначе создаём
    genre = db.query(models.Genre).filter_by(name="Drama").first()
    if not genre:
        genre = models.Genre(name="Drama")
        db.add(genre)
        db.commit()
        db.refresh(genre)

    # Создаём сериал и связываем с жанром
    series = models.Series(
        title="Test Series",
        description="Test Description",
        release_year=2020,
        rating=8.5
    )
    db.add(series)
    db.commit()
    db.refresh(series)

    series.genres.append(genre)
    db.commit()
    db.close()


def test_create_user():
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpass"}
    )
    print("CREATE USER RESPONSE:", response.json())
    assert response.status_code == 200
    assert "id" in response.json()


def test_login():
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_read_series():
    response = client.get("/series/")
    print("READ SERIES RESPONSE:", response.json())
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_genre_average_rating():
    # Сначала логинимся, чтобы получить токен
    login_response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Получаем список жанров
    response = client.get("/genres/", headers=headers)
    genre_id = response.json()[0]["id"]

    # Запрашиваем средний рейтинг по жанру
    response = client.get(f"/genres/{genre_id}/average-rating", headers=headers)
    print("GENRE AVERAGE RESPONSE:", response.json())
    assert response.status_code == 200
    assert "average_rating" in response.json()