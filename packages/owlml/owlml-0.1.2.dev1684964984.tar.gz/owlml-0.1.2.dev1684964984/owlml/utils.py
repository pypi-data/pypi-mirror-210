"""Utility functions for owlml."""
from typing import Any, Callable, Iterator


def pagination_iterator(
    api_function: Callable[[int], dict[str, Any]]
) -> Iterator[dict[str, Any]]:
    """Return an iterator over all pages of an API function."""
    page = 1
    response = api_function(page)
    yield from response["results"]
    while response["has_next"]:
        page += 1
        response = api_function(page)
        yield from response["results"]
