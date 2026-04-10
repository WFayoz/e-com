from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.products import ReadProduct


class AddToCart(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class UpdateCartItem(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemOut(BaseModel):
    id: UUID
    product_id: int
    quantity: int
    product: ReadProduct

    class Config:
        from_attributes = True
