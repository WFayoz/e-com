from pydantic import BaseModel


class CreateProduct(BaseModel):
    name: str


class UpdateProduct(BaseModel):
    name: str | None = None

    class Config:
        from_attributes = True


class ReadProduct(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
