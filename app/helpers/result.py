from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar('T')

class Result(BaseModel, Generic[T]):
    is_success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    status_code: int
    errors: Optional[List[str]] = None
    
    @classmethod
    def success(cls, message: str, status_code: int, data: Optional[T] = None):
        return cls(
            is_success=True,
            data=data,
            message=message,
            status_code=status_code,    
            errors=None
        )
        
    @classmethod
    def failure(cls, message: str, status_code: int, errors: Optional[List[str]] = None):
        return cls(
            is_success=False,
            data=None,
            message=message,
            status_code=status_code,
            errors=errors
        )