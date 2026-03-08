from typing import TypeVar, Generic

from pydantic import BaseModel

from app.schemas.categories import CreateCategory, ReadCategory, UpdateCategory
from app.schemas.products import CreateProduct, UpdateProduct, ReadProduct

T = TypeVar('T', bound=BaseModel)


class ResponseSchema(BaseModel, Generic[T]):
    message: str
    data: T | None = None


__all__ = [
    'ResponseSchema',
    'CreateCategory',
    'ReadCategory',
    'UpdateCategory',
    # product
    'CreateProduct',
    'ReadProduct',
    'UpdateProduct',
]
