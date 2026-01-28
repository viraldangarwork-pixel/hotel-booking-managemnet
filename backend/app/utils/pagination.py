"""Pagination utilities."""

from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Query


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

    class Config:
        arbitrary_types_allowed = True


class Paginator:
    """Paginator for SQLAlchemy queries."""

    def __init__(
        self,
        query: Query,
        page: int = 1,
        size: int = 20,
        max_size: int = 100,
    ):
        """
        Initialize paginator.

        Args:
            query: SQLAlchemy query object
            page: Current page number (1-indexed)
            size: Number of items per page
            max_size: Maximum allowed items per page
        """
        self.query = query
        self.page = max(1, page)
        self.size = min(max(1, size), max_size)

        # Get total count
        self._total = None
        self._items = None

    @property
    def total(self) -> int:
        """Get total number of items."""
        if self._total is None:
            self._total = self.query.count()
        return self._total

    @property
    def pages(self) -> int:
        """Get total number of pages."""
        if self.total == 0:
            return 1
        return (self.total + self.size - 1) // self.size

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1

    @property
    def offset(self) -> int:
        """Calculate offset for query."""
        return (self.page - 1) * self.size

    @property
    def items(self) -> List:
        """Get items for current page."""
        if self._items is None:
            self._items = self.query.offset(self.offset).limit(self.size).all()
        return self._items

    def get_response(self) -> dict:
        """Get paginated response as dictionary."""
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "size": self.size,
            "pages": self.pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }


def paginate(
    query: Query,
    page: int = 1,
    size: int = 20,
    max_size: int = 100,
) -> dict:
    """
    Paginate a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object
        page: Current page number (1-indexed)
        size: Number of items per page
        max_size: Maximum allowed items per page

    Returns:
        Dictionary with paginated results
    """
    paginator = Paginator(query, page, size, max_size)
    return paginator.get_response()


class CursorPaginator:
    """Cursor-based pagination for large datasets."""

    def __init__(
        self,
        query: Query,
        cursor_field: str = "id",
        cursor: Optional[int] = None,
        size: int = 20,
        max_size: int = 100,
    ):
        """
        Initialize cursor paginator.

        Args:
            query: SQLAlchemy query object
            cursor_field: Field to use for cursor (default: id)
            cursor: Current cursor value (last seen item's cursor field)
            size: Number of items per page
            max_size: Maximum allowed items per page
        """
        self.query = query
        self.cursor_field = cursor_field
        self.cursor = cursor
        self.size = min(max(1, size), max_size)

    def get_items(self) -> List:
        """Get items after cursor."""
        query = self.query

        if self.cursor is not None:
            # Filter items after cursor
            query = query.filter(
                getattr(query.column_descriptions[0]["entity"], self.cursor_field) > self.cursor
            )

        return query.order_by(self.cursor_field).limit(self.size + 1).all()

    def get_response(self) -> dict:
        """Get cursor-paginated response."""
        items = self.get_items()

        has_next = len(items) > self.size
        if has_next:
            items = items[:-1]

        next_cursor = None
        if items and has_next:
            next_cursor = getattr(items[-1], self.cursor_field)

        return {
            "items": items,
            "next_cursor": next_cursor,
            "has_next": has_next,
            "size": len(items),
        }
