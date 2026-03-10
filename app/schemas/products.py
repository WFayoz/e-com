from pydantic import BaseModel


class CreateProduct(BaseModel):
    name: str
    description: str | None = None
    price: float
    discount_percentage: float = 0
    rating: float = 0
    availability: int = 0


class UpdateProduct(BaseModel):
    name: str | None = None

    class Config:
        from_attributes = True


class ReadProduct(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
