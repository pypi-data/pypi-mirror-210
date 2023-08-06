"""
A Python SDK for https://the-one-api.dev.

This module provides a client for interacting with the One API, as well as
helper classes for building queries and handling errors. The main classes
are LotrClient, which sends requests to the API, and LotrQueryBuilder, which
helps construct query parameters for those requests.

Example usage:

    client = LotrClient(api_key="your_api_key")
    query_builder = LotrQueryBuilder(models.BOOK)
    query_builder \\
        .paginate(page=1, limit=10) \\
        .add_sort(query.Sort("title", SortOrder.DESCENDING))
    query = query_builder.build()
    books = client.get_books(query)

This module depends on the requests library for sending HTTP requests, and
the backoff and ratelimit libraries for handling rate limits and retries.
"""

import logging

import backoff
import ratelimit
import requests

from lotr_sdk import exceptions
from lotr_sdk import models


class LotrClient:
    """Client for interacting with the One API.

    This class provides methods to send requests to the API and handle the
    responses. It manages the rate limit and request timeout, and it can be
    configured with a specific API key and log level.

    Attributes:
    - RATE_LIMIT (int):
        The maximum number of requests that can be made within a specific time
        period.
    - TIME_PERIOD (int):
        The time period (in seconds) for the rate limit.

    Examples:
    client = LotrClient(api_key="your-api-key")
    client.get_books()

    client.get_quote("5cd99d4bde30eff6ebccfea0")

    client.get_quotes(LotrQueryBuild()
                         .add(Include("movie", ["The Fellowship of the Ring"]))
                         .build())
    """

    _RATE_LIMIT = 100
    _TIME_PERIOD = 600

    def __init__(self,
                 api_key: str,
                 timeout: int = 60,
                 log_level: str = "INFO"):
        """Initialize the client with API key, timeout, and log level.

        Args:
        - api_key (str):
            The API key obtained from https://the-one-api.dev/.
        - timeout (int, optional):
            The request timeout in seconds. Defaults to 60.
        - log_level (str, optional):
            The log level for the logger. Defaults to "INFO".

        Raises:
        - exceptions.InvalidAPIKeyError:
            If the API key is invalid or not set.
        """

        if not api_key:
            raise exceptions.InvalidAPIKeyError("API key must be set")

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level.upper())

        self.api_key = api_key
        self._base_url = "https://the-one-api.dev/v2"
        self._headers = {"Authorization": f"Bearer {self.api_key}"}

        self._session = requests.Session()
        self._session.headers.update(self._headers)
        self._session.timeout = timeout

    @backoff.on_exception(
        backoff.expo,
        (ratelimit.RateLimitException, requests.RequestException),
        jitter=backoff.full_jitter,
        max_tries=1)
    @ratelimit.limits(calls=_RATE_LIMIT, period=_TIME_PERIOD)
    def _get(self, endpoint: str, params: dict = None) -> dict:
        """Makes a GET request to the API and returns the response as a JSON
        object.

        Args:
            endpoint (str):
                The endpoint to query in the API.
            params (dict, optional):
                The parameters to include in the request URL (default: None).

        Returns:
            dict: The JSON response from the API.

        Raises:
            requests.exceptions.HTTPError:
                If the GET request returns a non-successful status code.
            ratelimit.RateLimitException:
                If the request exceeds the rate limit.
        """

        url = f"{self._base_url}/{endpoint}"
        self.logger.info(f"GET {url} with params {params}")
        response = self._session.get(url, params=params)
        response.raise_for_status()

        return response.json()["docs"]

    def get_books(self, query: dict = None) -> dict:
        """Fetches a list of books from the API.

        Args:
        - query (dict, optional):
            Query parameters for the request.

        Returns:
        - dict:
            The JSON response from the API as a dictionary.
        """
        return [models.Book(m) for m in self._get("book", query)]

    def get_book(self, book_id: str, query: dict = None) -> dict:
        """Fetches a single book from the API.

        Returns:
        - models.Book:
            The book resource.
        """
        return models.Book(self._get(f"book/{book_id}", query)[0])

    def get_chapters(self, book_id: str, query: dict = None) -> dict:
        """Fetches a list of chapters from the API.

        Args:
        - book_id (str):
            The ID of the book to fetch chapters from.
        - query (dict, optional):
            Query parameters for the request.

        Returns:
        - list[models.Chapter]:
            A list of chapter resources.
        """
        return [
            models.Chapter(m)
            for m in self._get(f"book/{book_id}/chapter", query)
        ]

    def get_chapter(self, chapter_id: str, query: dict = None) -> dict:
        """Fetches a single chapter from the API.

        Args:
        - chapter_id (str):
            The ID of the chapter to fetch.
        - query (dict, optional):
            Query parameters for the request.

        Returns:
        - models.Chapter:
            The chapter resource.
        """
        return models.Chapter(self._get(f"chapter/{chapter_id}", query)[0])

    def get_movies(self, query: dict = None) -> dict:
        """Fetches a list of movies from the API.

        Args:
        - query (dict, optional):
            Query parameters for the request.

        Returns:
        - list[models.Movie]:
            A list of movie resources.
        """
        return [models.Movie(m) for m in self._get("movie", query)]

    def get_movie(self, movie_id: str, query: dict = None) -> dict:
        """Fetches a single movie from the API.

        Args:
        - movie_id (str):
            The ID of the movie to fetch.
        - query (dict, optional):
            Query parameters for the request.

        Returns:
        - models.Movie:
            The movie resource.
        """
        return models.Movie(self._get(f"movie/{movie_id}", query)[0])

    def get_quotes(self, movie_id: str, query: dict = None) -> dict:
        """Fetches a list of quotes from the API.

        Args:
        - movie_id (str):
            The ID of the movie to fetch quotes from.
        - query (dict, optional):
            Query parameters for the request.

        Returns:
        - list[models.Quote]:
            A list of quote resources.
        """
        return [
            models.Quote(m)
            for m in self._get(f"movie/{movie_id}/quote", query)
        ]

    def get_quote(self,
                  quote_id: str,
                  query: dict = None) -> dict:
        """Fetches a single quote from the API.

        Args:
        - quote_id (str):
            The ID of the quote to fetch.
        - query (dict, optional):
            Query parameters for the request.

        Returns:
        - models.Quote:
            The quote resource.
        """
        return models.Quote(
            self._get(f"quote/{quote_id}", query)[0])

    def get_characters(self, query: dict = None) -> dict:
        """Fetches a list of characters from the API.

        Args:
        - query (dict, optional):
            Query parameters for the request.

        Returns:
        - list[models.Character]:
            A list of character resources.
        """
        return [models.Character(m) for m in self._get("character", query)]

    def get_character(self, character_id: str, query: dict = None) -> dict:
        """Fetches a single character from the API.

        Args:
        - character_id (str):
            The ID of the character to fetch.
        - query (dict, optional):
            Query parameters for the request.

        Returns:
        - models.Character:
            The character resource.
        """
        return models.Character(self._get(f"character/{character_id}",
                                          query)[0])

    def get_character_quotes(self,
                             character_id: str,
                             query: dict = None) -> dict:
        """Fetches a list of quotes for a character from the API.

        Args:
        - character_id (str):
            The ID of the character to fetch quotes for.
        - query (dict, optional):
            Query parameters for the request.

        Returns:
        - list[models.Quote]:
            A list of quote resources.
        """
        return [
            models.Quote(m)
            for m in self._get(f"character/{character_id}/quote", query)
        ]
