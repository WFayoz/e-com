from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class OrderItemOut(BaseModel):
    id: UUID
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: UUID
    status: str
    total_amount: Decimal
    items: list[OrderItemOut]

    class Config:
        from_attributes = True
