# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

import pytest
from unittest.mock import MagicMock, patch
from models.film import Film

def test_film_init():
    film = Film(
        filmId=1,
        title="Inception",
        description="A thief who steals corporate secrets through the use of dream-sharing technology.",
        genre="Sci-Fi",
        ageRating="PG-13",
        actors="Leonardo DiCaprio, Joseph Gordon-Levitt"
    )
    assert film.filmId == 1
    assert film.title == "Inception"
    assert film.genre == "Sci-Fi"
    assert "Leonardo DiCaprio" in film.actors

def test_film_from_row():
    row = {
        "filmId": 1,
        "title": "Inception",
        "description": "Dream stuff",
        "genre": "Sci-Fi",
        "ageRating": "PG-13",
        "actors": "Leo"
    }
    film = Film.from_row(row)
    assert film.filmId == 1
    assert film.title == "Inception"

@patch("models.film.db")
def test_film_get_all(mock_db):
    mock_db.fetchall.return_value = [
        {"filmId": 1, "title": "A", "description": "", "genre": "", "ageRating": "", "actors": ""},
        {"filmId": 2, "title": "B", "description": "", "genre": "", "ageRating": "", "actors": ""}
    ]
    films = Film.get_all()
    assert len(films) == 2
    assert films[0].title == "A"
    assert films[1].title == "B"
    mock_db.fetchall.assert_called_once()

@patch("models.film.db")
def test_film_get_by_id(mock_db):
    mock_db.fetchone.return_value = {"filmId": 1, "title": "Inception", "description": "", "genre": "", "ageRating": "", "actors": ""}
    film = Film.get_by_id(1)
    assert film is not None
    assert film.title == "Inception"
    mock_db.fetchone.assert_called_once_with("SELECT * FROM films WHERE filmId=?", (1,))

@patch("models.film.db")
def test_film_get_by_id_not_found(mock_db):
    mock_db.fetchone.return_value = None
    film = Film.get_by_id(999)
    assert film is None

def test_film_get_details():
    film = Film(1, "Title", "Desc", "Genre", "Rating", "Actors")
    details = film.getDetails()
    assert details["title"] == "Title"
    assert details["filmId"] == 1

def test_film_repr():
    film = Film(1, "Inception", "", "", "", "")
    assert repr(film) == "<Film id=1 title='Inception'>"

