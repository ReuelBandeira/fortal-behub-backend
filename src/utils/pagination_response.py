from typing import Generic, TypeVar, List
from pydantic import BaseModel
from math import ceil

T = TypeVar("T")

class PaginationResponse(BaseModel, Generic[T]):
    page: int
    limit: int
    items_in_page: int
    total_items: int
    total_pages: int
    items: List[T]

    @classmethod
    def create(
        cls,
        page: int,
        limit: int,
        total: int,
        items: List[T]
    ):
        total_pages = ceil(total / limit) if limit else 1
        return cls.model_validate({
            "page": page,
            "limit": limit,
            "items_in_page": len(items),
            "total_items": total,
            "total_pages": total_pages,
            "items": items
        })
