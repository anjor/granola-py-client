from typing import Callable, Awaitable, TypeVar, AsyncGenerator, Generic, Optional, List
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T", bound=BaseModel)

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    next_cursor: Optional[str] = Field(None, alias="next_cursor")

    model_config = ConfigDict(populate_by_name=True)

# FetchPageFunc is already generic with respect to T due to its definition
FetchPageFunc = Callable[[Optional[str]], Awaitable[PaginatedResponse[T]]]

# When using FetchPageFunc as a type hint for an argument,
# the type variable T is bound by the context of the function 'paginate'.
# The 'paginate' function itself is generic in T.
async def paginate(fetch_page: FetchPageFunc) -> AsyncGenerator[T, None]: # Corrected line
    """
    Async pagination iterator helper.
    :param fetch_page: An async function that takes an optional cursor string
                       and returns a PaginatedResponse object containing items of type T.
    """
    cursor: Optional[str] = None
    while True:
        # The type of 'response' will be PaginatedResponse[T]
        # because 'fetch_page' is expected to return that.
        response = await fetch_page(cursor)
        for item in response.items: # 'item' will be of type T
            yield item

        if response.next_cursor:
            cursor = response.next_cursor
        else:
            break
