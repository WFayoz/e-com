from typing import Optional

from pydantic import BaseModel


class UpdateProfile(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None


class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str
