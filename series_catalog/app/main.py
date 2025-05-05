from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, crud, auth
from .database import SessionLocal, engine
from .auth import get_current_user
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Series Catalog API",
        version="1.0.0",
        description="API для сериалов с JWT авторизацией",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema
app.openapi = custom_openapi
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = crud.create_user(db, user)
    return schemas.User.from_orm(created_user)


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return schemas.User.from_orm(current_user)


@app.post("/series/", response_model=schemas.Series)
def create_series(
    series: schemas.SeriesCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    created = crud.create_series(db=db, series=series)
    return schemas.Series.from_orm(created)


@app.get("/series/", response_model=List[schemas.Series])
def read_series(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    series = crud.get_series_list(db, skip=skip, limit=limit)
    return [schemas.Series.from_orm(s) for s in series]


@app.get("/series/{series_id}", response_model=schemas.Series)
def read_series(series_id: int, db: Session = Depends(get_db)):
    db_series = crud.get_series(db, series_id=series_id)
    if db_series is None:
        raise HTTPException(status_code=404, detail="Series not found")
    return schemas.Series.from_orm(db_series)


@app.post("/series/{series_id}/seasons/", response_model=schemas.Season)
def create_season_for_series(
    series_id: int,
    season: schemas.SeasonBase,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    created = crud.create_season(db=db, season=season, series_id=series_id)
    return schemas.Season.from_orm(created)


@app.post("/seasons/{season_id}/episodes/", response_model=schemas.Episode)
def create_episode_for_season(
    season_id: int,
    episode: schemas.EpisodeBase,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    created = crud.create_episode(db=db, episode=episode, season_id=season_id)
    return schemas.Episode.from_orm(created)


@app.post("/genres/", response_model=schemas.Genre)
def create_genre(
    genre: schemas.GenreBase,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    created = crud.create_genre(db=db, genre=genre)
    return schemas.Genre.from_orm(created)


@app.get("/genres/", response_model=List[schemas.Genre])
def read_genres(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    genres = crud.get_genre_list(db, skip=skip, limit=limit)
    return [schemas.Genre.from_orm(g) for g in genres]


@app.get("/genres/{genre_id}/average-rating")
def get_genre_average_rating(
    genre_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    genre = crud.get_genre(db, genre_id=genre_id)
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    series_in_genre = db.query(models.Series).join(models.SeriesGenre).filter(
        models.SeriesGenre.genre_id == genre_id
    ).all()

    if not series_in_genre:
        return {"genre_id": genre_id, "average_rating": None, "message": "No series in this genre"}

    ratings = [s.rating for s in series_in_genre if s.rating is not None]
    if not ratings:
        return {"genre_id": genre_id, "average_rating": None, "message": "No ratings available"}

    average = sum(ratings) / len(ratings)
    return {"genre_id": genre_id, "average_rating": round(average, 2)}