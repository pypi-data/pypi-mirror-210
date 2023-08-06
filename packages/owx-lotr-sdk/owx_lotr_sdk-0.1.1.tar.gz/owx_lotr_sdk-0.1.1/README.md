# LOTR SDK

A Python SDK for https://the-one-api.dev.

This library provides a client for interacting with The One API, as well as
helper classes for building queries and handling errors. The main classes
are `LotrClient`, which sends requests to the API, and `LotrQueryBuilder`, which
helps construct query parameters for those requests.

Example usage:

```
    from lotr_sdk import client
    from lotr_sdk import query
    from lotr_sdk import options

    # Use query builder to construct parameters for client fetch requests.
    query_builder = query.LotrQueryBuilder(models.BOOK)
    query_builder \
        .paginate(page=1, limit=10) \
        .add(query.Sort("title", SortOrder.DESCENDING))
    query = query_builder.build()

    # Create a LotrClient using your API key from https://the-one-api.dev.
    lotr_client = client.LotrClient(api_key="your_api_key")
    books = lotr_client.get_books(query)
```

This module depends on the requests library for sending HTTP requests, and
the backoff and ratelimit libraries for handling rate limits and retries.

## Project Configuration

This project uses [poetry](https://python-poetry.org/docs/). From the `poetry` site:

> Poetry is a tool for dependency management and packaging in Python. It allows you to declare the
> libraries your project depends on and it will manage (install/update) them for you. Poetry offers
> a lockfile to ensure repeatable installs, and can build your project for distribution.

## LotrQueryBuilder

The `lotr_sdk.query` module contains a query parameter builder and supporting classes. Specifically,
it contains the `LotrQueryBuilder` class with the following primary methods:

- `add()` takes instances of `Paginate`, `Sort`, or `Filter` classes for defining clauses in the
  query. These classes can also be found in the `lotr_sdk.client` module.
- `build()` returns the query parameters as a dictionary, ready to be used with the `LotrClient`
  interface.

## LotrClient

The `LotrClient` class provides methods for fetching information from [The One API](https:
//the-one-api.dev). Fetch results use types defined in the `lotr_sdk.models` module. The client
methods return either a single object, or a homogeneous list of objects. The following types are
supported:

- Book
- Chapter
- Movie
- Quote
- Character

## Tests

Tests use the `pytest` library, and can be found in the `tests` module. Assuming that you have
[poetry](https://python-poetry.org/docs/) installed and set up, tests can be run using:
`poetry run pytest tests/test_lotr_sdk.py`

The One API key is read from `THE_ONE_API_KEY` environment variable. It can be specified in most
shells using the following syntax:
`THE_ONE_API_KEY="your-api-key" poetry run pytest tests/test_lotr_sdk.py`

Tests are divided between the following classes:

- `TestLotrClientUnit` runs through the client methods with mocked network requests.
- `TestLotrClientIntegration` runs through the client methods making network requests. Beware of API
  rate limitations.
- `TestLotrQueryBuilder` runs through the query builder methods to create query parameter
  dictionaries for all clauses.

To install dependencies, run `poetry install`.

To run a subset of tests, use the following syntax:
`poetry run pytest tests/test_lotr_sdk.py::TestLotrClientUnit` to run only tests in that test class.

`poetry run pytest tests/test_lotr_sdk.py::TestLotrClientUnit::test_get_books` to run only the
`get_books` test in that test class.

## Publish
To install dependencies, run:
`poetry install`

To set your PyPI token:
`poetry config pypi-token.pypi your-api-token`

To build the project, run:
`poetry build`

To publish:
`poetry publish`

Alternatively:
`poetry publish --build`
