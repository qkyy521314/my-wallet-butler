from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional
from typing_extensions import Literal


T = TypeVar('T')


class SuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None


class SuccessResponseWithData(SuccessResponse):
    data: Optional[T] = None

    class Config:
        arbitrary_types_allowed = True


class PaginatedResponse(BaseModel):
    items: List[T]
    total: int
    page: int
    size: int
    total_pages: int

    class Config:
        arbitrary_types_allowed = True


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None