from pydantic import BaseModel


class CreateCategory(BaseModel):
    name: str


class UpdateCategory(BaseModel):
    name: str | None = None

    class Config:
        from_attributes = True


class ReadCategory(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
