from pydantic import BaseModel, EmailStr
from typing import List, Optional

# ================== АВТОРИЗАЦИЯ ====================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

# ================== ПОЛЬЗОВАТЕЛИ ====================
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# ================== ЖАНР ====================
class GenreBase(BaseModel):
    name: str

class Genre(GenreBase):
    id: int

    class Config:
        orm_mode = True

# ================== ЭПИЗОД ====================
class EpisodeBase(BaseModel):
    title: str
    duration_minutes: int

class Episode(EpisodeBase):
    id: int

    class Config:
        orm_mode = True

# ================== СЕЗОН ====================
class SeasonBase(BaseModel):
    number: int
    release_year: int

class Season(SeasonBase):
    id: int
    episodes: List[Episode] = []

    class Config:
        orm_mode = True

# ================== СЕРИАЛ ====================
class SeriesBase(BaseModel):
    title: str
    description: str
    release_year: int
    rating: Optional[float] = None

class SeriesCreate(SeriesBase):
    genre_ids: List[int] = []

class Series(SeriesBase):
    id: int
    genres: List[Genre] = []
    seasons: List[Season] = []

    class Config:
        orm_mode = True