"""This module contains the enumerations for the options of the API."""

from enum import StrEnum


class QueryOption(StrEnum):
    """Enumeration representing the options for the query API.

    Options include:
    - PAGE: To set the page number of paginated results.
    - LIMIT: To limit the number of results.
    - OFFSET: To offset the starting point of paginated results.
    - SORT: To sort the results.
    - FILTER: To filter the results.
    """
    PAGE = "page"
    LIMIT = "limit"
    OFFSET = "offset"
    SORT = "sort"
    FILTER = ""  # Empty string key in `request` params dict turned into list.


class Pagination(StrEnum):
    """Enumeration representing the pagination options for the query API.

    Options include:
    - PAGE: To set the page number of paginated results.
    - LIMIT: To limit the number of results.
    - OFFSET: To offset the starting point of paginated results.
    """
    PAGE = "page"
    LIMIT = "limit"
    OFFSET = "offset"


class SortOrder(StrEnum):
    """Enumeration representing the sort order options for the API.

    Options include:
    - ASCENDING: To sort the results in ascending order.
    - DESCENDING: To sort the results in descending order.
    """
    ASCENDING = "asc"
    DESCENDING = "desc"


class Comparator(StrEnum):
    """Enumeration representing the comparator options for the API.

    Options include:
    - EQUALS: Represents the equality comparator.
    - GREATER_THAN: Represents the greater than comparator.
    - GREATER_THAN_EQUALS: Represents the greater than or equals comparator.
    - LESS_THAN: Represents the less than comparator.
    - LESS_THAN_EQUALS: Represents the less than or equals comparator.
    """
    EQUALS = "="
    GREATER_THAN = ">"
    GREATER_THAN_EQUALS = ">="
    LESS_THAN = "<"
    LESS_THAN_EQUALS = "<="


class Resource(StrEnum):
    """Enumeration representing the resource options for the API.

    Options include:
    - BOOK: Represents the book resource.
    - CHAPTER: Represents the chapter resource.
    - MOVIE: Represents the movie resource.
    - QUOTE: Represents the quote resource.
    - CHARACTER: Represents the character resource.
    """
    BOOK = "book"
    CHAPTER = "chapter"
    MOVIE = "movie"
    QUOTE = "quote"
    CHARACTER = "character"
