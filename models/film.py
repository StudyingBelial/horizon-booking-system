# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
models/film.py — Film domain model.
"""

from database.db_manager import db


class Film:
    def __init__(self, filmId: int, title: str, description: str,
                 genre: str, ageRating: str, actors: str):
        self.filmId      = filmId
        self.title       = title
        self.description = description or ""
        self.genre       = genre or ""
        self.ageRating   = ageRating or ""
        self.actors      = actors or ""

    @staticmethod
    def from_row(row) -> "Film":
        return Film(**dict(row))

    @staticmethod
    def get_all():
        rows = db.fetchall("SELECT * FROM films ORDER BY title")
        return [Film.from_row(r) for r in rows]

    @staticmethod
    def get_by_id(film_id: int) -> "Film":
        row = db.fetchone("SELECT * FROM films WHERE filmId=?", (film_id,))
        return Film.from_row(row) if row else None

    def getDetails(self) -> dict:
        return {
            "filmId":      self.filmId,
            "title":       self.title,
            "description": self.description,
            "genre":       self.genre,
            "ageRating":   self.ageRating,
            "actors":      self.actors,
        }

    def __repr__(self):
        return f"<Film id={self.filmId} title={self.title!r}>"

