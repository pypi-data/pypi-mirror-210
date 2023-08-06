"""This module contains all the query clauses used in the API."""
from collections import defaultdict
import re

from lotr_sdk import exceptions
from lotr_sdk import options
from lotr_sdk import query


class Paginate(int):
    """Base class for pagination clauses in the API.

    This class should not be instantiated directly.

    Raises:
    - TypeError: If instantiated directly.
    """

    def __new__(cls, *args, **kwargs):
        if cls is Paginate:
            raise TypeError("Cannot instantiate Paginate directly")


class Limit(Paginate):
    """Clause to limit the number of paginated results in the API query.

    This clause specifies the maximum number of results to be returned in a
    single page.

    Example:
        clauses.Limit(10)
    """
    def __new__(cls, value: int):
        """Creates a new Limit clause.

        Args:
        - value (int):
            The maximum number of results to be returned in a single page.
        """
        return int.__new__(cls, value)


class Offset(Paginate):
    """Clause to offset the starting point of paginated results in the API
    query.

    This clause specifies the number of results to skip from the beginning
    of the paginated results.

    Example:
        clauses.Offset(10)
    """
    def __new__(cls, value: int):
        """Creates a new Offset clause.

        Args:
        - value (int):
            The number of results to skip from the beginning of the paginated
            results.
        """
        return int.__new__(cls, value)


class Page(Paginate):
    """Clause to set the page number of paginated results in the API query.

    This clause specifies the specific page number of the results to be
    retrieved.

    Example:
        clauses.Page(1)
    """
    def __new__(cls, value: int):
        """Creates a new Page clause.

        Args:
        - value (int):
            The page number of the results to be retrieved.
        """
        return int.__new__(cls, value)


class Sort(str):
    """Clause to sort the results by a given key and order in the API query.

    Args:
    - key (str):
        The key to sort by.
    - order (SortOrder):
        The order to sort in. Defaults to SortOrder.ASCENDING.

    Example:
        clauses.Sort("name")
        query.Sort("title", SortOrder.DESCENDING)
    """

    def __new__(cls, key: str, order: options.SortOrder
                = options.SortOrder.ASCENDING):
        """Creates a new Sort clause.

        Args:
        - key (str):
            The key to sort by.
        - order (SortOrder):
            The order to sort in. Defaults to SortOrder.ASCENDING.
        """
        return str.__new__(cls, f"{key}:{order.value}")

    def __init__(self, key: str, order: options.SortOrder
                 = options.SortOrder.ASCENDING):
        """Initializes the Sort clause.

        Args:
        - key (str):
            The key to sort by.
        - order (SortOrder):
            The order to sort in. Defaults to SortOrder.ASCENDING.
        """
        super().__init__()
        self._key = key
        self._order = order

    @property
    def key(self):
        return self._key


class Filter(str):
    """Base class for filter clauses in the API query.

    Args:
    - key (str): The key to filter by.

    Raises:
    - TypeError: If instantiated directly.
    """

    def __new__(cls, key: str):
        """Raises TypeError if instantiated directly.

        Raises:
        - TypeError: If instantiated directly.
        """
        if cls is Filter:
            raise TypeError("Cannot instantiate Filter directly")

    def __init__(self, key: str):
        """Initializes the Filter clause.

        Args:
        - key (str):
            The key to filter by.
        """
        super().__init__()
        self._key = key

    @property
    def key(self) -> str:
        """The key to filter by.
        """
        return self._key


class Match(Filter):
    """Clause to match a given key with a given value in the API query.

    Args:
    - key (str):
        The key to match.
    - value (str):
        The value to match the key with.
    - negate (bool, optional):
        Whether to negate the match. Defaults to False.

    Example:
        Match("name", "Gandalf")
        Match("name", "Gandalf", negate=True)

    """

    def __new__(cls, key: str, value: str, negate: bool = False):
        """Creates a new Match clause.

        Args:
        - key (str):
            The key to match.
        - value (str):
            The value to match the key with.
        - negate (bool, optional):
            Whether to negate the match. Defaults to False.

        Returns:
            Match: The Match clause.
        """
        return str.__new__(cls, f"{key}{'!=' if negate else '='}{value}")

    def __init__(self, key: str, value: str, negate: bool = False):
        """Initializes the Match clause.

        Args:
        - key (str):
            The key to match.
        - value (str):
            The value to match the key with.
        - negate (bool, optional):
            Whether to negate the match. Defaults to False.
        """
        super().__init__(key)
        self._value = value
        self._operator = "!=" if negate else "="

    @property
    def value(self) -> str:
        """The value used in the Match clause.
        """
        return self._value

    @property
    def operator(self) -> str:
        """The operator used in the Match clause.

        This will be either "=" or "!=".
        """
        return self._operator

    def __str__(self) -> str:
        """Returns the string representation of the Match clause.
        """
        return f"{self.key}{self.operator}{self.value}"


class MatchRegex(Filter):
    """Clause to match a given key with a given regex pattern in the API
    query.

    Args:
    - key (str):
        The key to match.
    - value (str):
        The regex pattern to match the key with.
    - negate (bool, optional):
        Whether to negate the match. Defaults to False.

    Raises:
    - ValueError:
        If the regex pattern is invalid.

    Examples:
        MatchRegex("name", ".*")
        MatchRegex("name", ".*", negate=True)
    """

    def __new__(cls, key: str, value: str, negate: bool = False):
        """Create a new MatchRegex clause.

        Args:
        - key (str):
            The key to match.
        - value (str):
            The regex pattern to match the key with.
        - negate (bool, optional):
            Whether to negate the match. Defaults to False.

        Returns:
            MatchRegex: The newly created MatchRegex clause.
        """
        return str.__new__(cls, f"{key}{'!=' if negate else '='}{value}")

    def __init__(self, key: str, value: str, negate: bool = False):
        """Initialize a new MatchRegex clause.

        Args:
        - key (str):
            The key to match.
        - value (str):
            The regex pattern to match the key with.
        - negate (bool, optional):
            Whether to negate the match. Defaults to False.

        Raises:
        - ValueError:
            If the regex pattern is invalid.
        """
        super().__init__(key)
        self._value = value
        self._operator = "!=" if negate else "="

        # Validate regex
        try:
            re.compile(value)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {value}") from e

    @property
    def value(self) -> str:
        """The regex pattern to match the key with.
        """
        return self._value

    @property
    def operator(self) -> str:
        """The operator to use for the match.

        This will be '=' or '!='.
        """
        return self._operator

    def __str__(self) -> str:
        """The string representation of the MatchRegex clause.
        """
        return f"{self.key}{self.operator}{self.value}"


class Include(Filter):
    """Clause to include a given key with given values in the API query.

    Args:
    - key (str):
        The key to include.
    - values (list[str]):
        The values to include with the key.
    - negate (bool, optional):
        Whether to negate the inclusion. Defaults to False.

    Examples:
        Include("character", ["Gandalf", "Frodo"])
        Include("character", ["Gandalf", "Frodo"], negate=True)
    """

    def __new__(cls, key: str, values: list[str], negate: bool = False):
        """Creates a new Include instance.

        Args:
            key (str): The key to include.
            values (list[str]): The values to include with the key.
            negate (bool, optional): Whether to negate the inclusion.
                Defaults to False.

        Returns:
            Include: The new Include instance.
        """
        operator = '!=' if negate else '='
        return str.__new__(cls, f"{key}{operator}{','.join(values)}")

    def __init__(self, key: str, values: list[str], negate: bool = False):
        """Initializes a new Include instance.

        Args:
            key (str): The key to include.
            values (list[str]): The values to include with the key.
            negate (bool, optional): Whether to negate the inclusion.
                Defaults to False.
        """
        super().__init__(key)
        self._values = values
        self._operator = "!=" if negate else "="

    @property
    def values(self) -> list[str]:
        """The values to Include for the key.
        """
        return self._values

    @property
    def operator(self) -> str:
        """The operator used to include the values with the key.

        This will be either '=' or '!='.
        """
        return self._operator

    def __str__(self) -> str:
        """The string representation of the Include clause.
        """
        return f"{self.key}{self.operator}{','.join(self.values)}"


class Exists(Filter):
    """Clause to check if a given key exists in the API query.

    Args:
    - key (str):
        The key to check.
    - negate (bool, optional):
        Whether to negate the existence check. Defaults to False.

    Examples:
        Exists("name")
        Exists("name", negate=True)
    """

    def __new__(cls, key: str, negate: bool = False):
        """Create a new Exists instance.

        Args:
            key (str): The key to check.
            negate (bool, optional): Whether to negate the existence
                check. Defaults to False.

        Returns:
            Exists: The new Exists instance.
        """
        return str.__new__(cls, f"{'!=' if negate else '='}{key}")

    def __init__(self, key: str, negate: bool = False):
        """Initialize a new Exists instance.

        Args:
            key (str): The key to check.
            negate (bool, optional): Whether to negate the existence
                check. Defaults to False.
        """
        super().__init__(key)
        self._operator = "!" if negate else ""

    @property
    def operator(self):
        """Get the operator for the Exists clause.

        This will be either '!' or ''.
        """
        return self._operator

    def __str__(self) -> str:
        """The string representation of the Exists clause.
        """
        return f"{self.operator}{self.key}"


class Compare(Filter):
    """Clause to compare a given key with a given value in the API
    query.

    Args:
    - key (str):
        The key to compare.
    - comparator (Comparator):
        The comparison operation. Options are enumerated in the
        Comparator class.
    - value (int):
        The value to compare the key to.

    Examples:
        Compare("age", Comparator.GREATER_THAN, 18)
    """

    def __new__(cls, key: str, comparator: options.Comparator, value: int):
        """Create a new Compare instance.

        Args:
            key (str): The key to compare.
            comparator (Comparator): The comparison operation.
            value (int): The value to compare the key to.
        Returns:
            Compare: The new Compare instance.

        """
        return str.__new__(cls, f"{key}{comparator.value}{value}")

    def __init__(self, key: str, comparator: options.Comparator, value: int):
        """Initialize a Compare instance.

        Args:
            key (str): The key to compare.
            comparator (Comparator): The comparison operation.
            value (int): The value to compare the key to.
        """
        super().__init__(key)
        self._comparator = comparator
        self._value = value

    @property
    def comparator(self) -> options.Comparator:
        """Get the comparison operation used in the compare clause.
        """
        return self._comparator

    @property
    def value(self) -> int:
        """Get the value to compare the key against.
        """
        return self._value

    def __str__(self) -> str:
        """The string representation of the Compare clause.
        """
        return f"{self.key}{self.comparator.value}{self.value}"


class LotrQueryBuilder:
    """Helper class to build queries for the LotR API.

    This class provides methods to add various query parameters like page,
    limit, offset, sort, and filter.

    Examples:
    query_builder = LotrQueryBuilder()
    query_builder.paginate(page=1, limit=10)
    query_builder.add_sort(query.Sort("title", SortOrder.DESCENDING))
    query_builder.build()

    query_builder = LotrQueryBuilder() \\
        .paginate(page=1, limit=10) \\
        .add_sort(query.Sort("title", SortOrder.DESCENDING))
    query_builder.build()
    """

    def __init__(self):
        """Initialize the builder with the query parameters.
        """
        self._params = defaultdict(list)

    def paginate(self,
                 page: int = 1,
                 limit: int = 10,
                 offset: int = 0) -> "LotrQueryBuilder":
        """Set the pagination options for the query.

        Args:
        - page (int, optional):
            The page number to fetch. Defaults to 1.
        - limit (int, optional):
            The number of results per page. Defaults to 10.
        - offset (int, optional):
            The number of results to skip before starting to fetch. Defaults to
            0.

        Raises:
        - InvalidClauseError:
            If the page, limit, or offset has already been set.

        Returns:
        - LotrQueryBuilder:
            The builder instance to allow method chaining.
        """

        self.add_page(page)
        self.add_limit(limit)
        self.add_offset(offset)

        return self

    def add_limit(self,
                  limit: query.Limit | int) -> "LotrQueryBuilder":
        """Sets the limit for the query.

        Args:
        - limit (query.Limit | int):
           The limit for the number of items per page. Must be a Limit object
           or an integer.

        Raises:
        - Error:
              If the limit has already been set.
        - InvalidClauseError:
                If the limit is not a Limit object or an integer.

        Returns:
        - LotrQueryBuilder:
           The builder instance to allow method chaining.
        """
        if options.Pagination.LIMIT in self._params:
            raise exceptions.Error("Limit already set")
        if not isinstance(limit, (query.Limit, int)):
            raise exceptions.InvalidClauseError("Limit must be a Limit or an "
                                                "integer")

        self._params[options.Pagination.LIMIT] = limit

        return self

    def add_offset(self, offset: query.Offset | int) -> "LotrQueryBuilder":
        """Sets the offset for the query.

        Args:
        - offset (query.Offset | int):
              The offset for the query. Must be an Offset object or an integer.

        Raises:
        - Error:
              If the offset has already been set.
        - InvalidClauseError:
                If the offset is not an Offset object or an integer.

        Returns:
        - LotrQueryBuilder:
            The builder instance to allow method chaining.
        """
        if options.Pagination.OFFSET in self._params:
            raise exceptions.Error("Offset already set")
        if not isinstance(offset, (query.Offset, int)):
            raise exceptions.InvalidClauseError(
                "Offset must be an Offset or an integer")

        self._params[options.Pagination.OFFSET] = offset

        return self

    def add_page(self, page: query.Page | int) -> "LotrQueryBuilder":
        """Sets the page for the query.

        Args:
        - page (query.Page | int):
            The page number to fetch. Must be a Page object or an integer.

        Raises:
        - Error:
              If the page has already been set.
        - InvalidClauseError:
                If the page is not a Page object or an integer.

        Returns:
        - LotrQueryBuilder:
            The builder instance to allow method chaining.
        """
        if options.Pagination.PAGE in self._params:
            raise exceptions.Error("Page already set")
        if not isinstance(page, (query.Page, int)):
            raise exceptions.InvalidClauseError("Page must be an integer")

        self._params[options.Pagination.PAGE] = page

        return self

    def add_sort(self, sort: query.Sort) -> "LotrQueryBuilder":
        """Set the sorting options for the query.

        Args:
        - field (str):
            The field to sort by.
        - order (SortOrder, optional):
            The order to sort in. Options are enumerated in the SortOrder
            class. Defaults to SortOrder.ASC.

        Returns:
        - LotrQueryBuilder:
            The builder instance to allow method chaining.
        """
        if options.QueryOption.SORT.value in self._params:
            raise exceptions.InvalidClauseError("Sort order already set")

        self._params[options.QueryOption.SORT] = str(sort)

        return self

    def add_filter(
            self, filter: query.Match | query.MatchRegex | query.Include
            | query.Exists | query.Compare) -> "LotrQueryBuilder":
        """Set a filter for the query.

        Args:
        - filter: (query.Match | query.MatchRegex | query.Include
            | query.Exists | query.Compare) :
            The field to filter by.

        Returns:
        - LotrQueryBuilder:
            The builder instance to allow method chaining.
        """
        if any(filter_.key == filter.key for filter_ in
               self._params[options.QueryOption.FILTER]):
            raise exceptions.InvalidClauseError(
                f"Filter for {filter.key} already set")

        self._params[options.QueryOption.FILTER].append(filter)

        return self

    def add(self, *clauses: list[query.Paginate | query.Sort |
                                 query.Filter]) -> "LotrQueryBuilder":
        """Adds clauses to the query.

        Args:
            *clauses (list[query.Paginate | query.Sort | query.Filter]):
                The clauses to be added.

        Returns:
        - LotrQueryBuilder:
            The builder instance to allow method chaining.

        Examples:
            builder = LotrQueryBuilder()
            builder.add(query.Paginate(10, 0))
            builder.add(query.Sort("name", SortOrder.ASCENDING)
            builder.add(query.Filter("age", Compare.GREATER_THAN, 18))
        """
        for clause in clauses:
            match type(clause):
                case query.Limit:
                    self.add_limit(clause)
                case query.Offset:
                    self.add_offset(clause)
                case query.Page:
                    self.add_page(clause)
                case query.Sort:
                    self.add_sort(clause)

                case _:
                    if issubclass(type(clause), query.Filter):
                        self.add_filter(clause)
                        return

                    raise exceptions.InvalidClauseError(
                        f"Invalid clause type {type(clause)}")
        return self

    def build(self) -> dict:
        """Finalizes and returns the query parameters.

        Returns:
        - dict: The query parameters as a dictionary.
        """
        return dict(self._params)
