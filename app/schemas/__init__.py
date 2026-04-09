from typing import TypeVar, Generic

from pydantic import BaseModel

from app.schemas.cart import AddToCart, CartItemOut, UpdateCartItem
from app.schemas.categories import CreateCategory, ReadCategory, UpdateCategory
from app.schemas.orders import OrderOut
from app.schemas.products import (
    CreateProduct,
    ProductListResponse,
    ReadProduct,
    UpdateProduct,
)

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
    'ProductListResponse',
    'AddToCart',
    'UpdateCartItem',
    'CartItemOut',
    'OrderOut',
]
