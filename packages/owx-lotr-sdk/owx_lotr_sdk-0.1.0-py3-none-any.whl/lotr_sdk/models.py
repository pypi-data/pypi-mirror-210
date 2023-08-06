"""This module contains the classes for the results of the API calls."""
from lotr_sdk import exceptions


class Movie(dict):

    def __init__(self, movie_dict: dict):
        if not movie_dict or not isinstance(movie_dict, dict):
            raise exceptions.InvalidModelDictionaryError(movie_dict)
        self.id = movie_dict.get("_id")
        self.name = movie_dict.get("name")
        self.runtimeInMinutes = movie_dict.get("runtimeInMinutes")
        self.budgetInMillions = movie_dict.get("budgetInMillions")
        self.boxOfficeRevenueInMillions = movie_dict.get(
            "boxOfficeRevenueInMillions")
        self.academyAwardNominations = movie_dict.get(
            "academyAwardNominations")
        self.academyAwardWins = movie_dict.get("academyAwardWins")
        self.rottenTomatoesScore = movie_dict.get("rottenTomatoesScore")


class Book(dict):

    def __init__(self, book_dict: dict):
        if not book_dict or not isinstance(book_dict, dict):
            raise exceptions.InvalidModelDictionaryError(book_dict)
        self.id = book_dict.get("_id")
        self.name = book_dict.get("name")
        self.numberOfChapters = book_dict.get("numberOfChapters")
        self.releaseDate = book_dict.get("releaseDate")


class Chapter(dict):

    def __init__(self, chapter_dict: dict):
        if not chapter_dict or not isinstance(chapter_dict, dict):
            raise exceptions.InvalidModelDictionaryError(chapter_dict)
        self.id = chapter_dict.get("_id")
        self.name = chapter_dict.get("name")
        self.chapterNumber = chapter_dict.get("chapterNumber")
        self.book = chapter_dict.get("book")


class Character(dict):

    def __init__(self, character_dict: dict):
        if not character_dict or not isinstance(character_dict, dict):
            raise exceptions.InvalidModelDictionaryError(character_dict)
        self.id = character_dict.get("_id")
        self.name = character_dict.get("name")


class Quote(dict):

    def __init__(self, quote_dict: dict):
        if not quote_dict or not isinstance(quote_dict, dict):
            raise exceptions.InvalidModelDictionaryError(quote_dict)
        self.id = quote_dict.get("_id")
        self.dialog = quote_dict.get("dialog")
        self.movie = quote_dict.get("movie")
        self.character = quote_dict.get("character")
