from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class SeriesGenre(Base):
    __tablename__ = "series_genres"
    series_id = Column(Integer, ForeignKey("series.id"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genres.id"), primary_key=True)

class Series(Base):
    __tablename__ = "series"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    release_year = Column(Integer)
    rating = Column(Float)
    genres = relationship("Genre", secondary="series_genres")
    seasons = relationship("Season", back_populates="series")

class Season(Base):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer)
    release_year = Column(Integer)
    series_id = Column(Integer, ForeignKey("series.id"))
    series = relationship("Series", back_populates="seasons")
    episodes = relationship("Episode", back_populates="season")

class Episode(Base):
    __tablename__ = "episodes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    duration_minutes = Column(Integer)
    season_id = Column(Integer, ForeignKey("seasons.id"))
    season = relationship("Season", back_populates="episodes")