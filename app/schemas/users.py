from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UpdateProfile(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone_number: Optional[str] = None


class UserOut(BaseModel):
    id: UUID
    firstname: str
    lastname: str
    phone_number: str
    role: str

    class Config:
        from_attributes = True


class ChangePassword(BaseModel):
    old_password: str
    new_password: str

    class Config:
        from_attributes = True
