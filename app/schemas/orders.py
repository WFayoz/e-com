from decimal import Decimal

from pydantic import BaseModel


class OrderItemOut(BaseModel):
    id: str
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: str
    status: str
    total_amount: Decimal
    items: list[OrderItemOut]

    class Config:
        from_attributes = True
