from pydantic import BaseModel
from typing import Generic, TypeVar
import math

T = TypeVar('T')

class Pageable(BaseModel, Generic[T]):
    items: list[T]
    total_elements: int
    total_pages: int
    current_page: int
    size: int
    
    @classmethod
    def create(cls, items: list[T], total_elements: int, page: int, size: int) -> "Pageable[T]":
        total_pages = math.ceil(total_elements / size) if size > 0 else 0
        return cls(
            items=items,
            total_elements=total_elements,
            total_pages=total_pages,
            current_page=page,
            size=size
        )