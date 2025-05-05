from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user  # ← важно!

def get_series(db: Session, series_id: int):
    return db.query(models.Series).filter(models.Series.id == series_id).first()


def get_series_by_title(db: Session, title: str):
    return db.query(models.Series).filter(models.Series.title == title).first()


def get_series_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Series).offset(skip).limit(limit).all()


def create_series(db: Session, series: schemas.SeriesCreate):
    db_series = models.Series(
        title=series.title,
        description=series.description,
        release_year=series.release_year,
        rating=series.rating
    )
    db.add(db_series)
    db.commit()
    db.refresh(db_series)

    # Добавляем жанры
    for genre_id in series.genre_ids:
        db_genre = db.query(models.Genre).filter(models.Genre.id == genre_id).first()
        if db_genre:
            db_series.genres.append(db_genre)

    db.commit()
    db.refresh(db_series)
    return db_series


def create_season(db: Session, season: schemas.SeasonBase, series_id: int):
    db_season = models.Season(**season.dict(), series_id=series_id)
    db.add(db_season)
    db.commit()
    db.refresh(db_season)
    return db_season


def create_episode(db: Session, episode: schemas.EpisodeBase, season_id: int):
    db_episode = models.Episode(**episode.dict(), season_id=season_id)
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    return db_episode


def get_genre(db: Session, genre_id: int):
    return db.query(models.Genre).filter(models.Genre.id == genre_id).first()


def get_genre_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Genre).offset(skip).limit(limit).all()


def create_genre(db: Session, genre: schemas.GenreBase):
    db_genre = models.Genre(name=genre.name)
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre