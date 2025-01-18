from sqlmodel import Field, SQLModel
from datetime import date

class Premier(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key = True)
    firstAired: date | None = None
    premierDate: date | None = None
    season: str | None = None
    premierType: str | None = None
    title: str | None = None
    year: int | None = None
    traktId: str | None = None
    imdbId: str | None = None
    overview: str | None = None
    country: str | None = None
    trailer: str | None = None
    language: str | None = None

class Genre(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key = True)
    genre: str | None = None
    premier: str | None = Field(default = None, foreign_key = "premier.id")

class Rating(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key = True)
    rating: int | None = None
    premier: str | None = Field(default = None, foreign_key = "premier.id")

class Search(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key = True)
    start: date
    end: date