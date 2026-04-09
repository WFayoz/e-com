from pydantic import BaseModel


class CreateProduct(BaseModel):
    name: str
    description: str | None = None
    price: float
    discount_percentage: float = 0
    rating: float = 0
    availability: int = 0
    category_id: int


class UpdateProduct(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    discount_percentage: float | None = None
    rating: float | None = None
    availability: int | None = None
    category_id: int | None = None

    class Config:
        from_attributes = True


class ReadProduct(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    discount_percentage: float
    rating: float
    availability: int
    category_id: int

    class Config:
        from_attributes = True


class ProductPagination(BaseModel):
    page: int
    size: int
    total: int


class ProductListResponse(BaseModel):
    items: list[ReadProduct]
    pagination: ProductPagination
