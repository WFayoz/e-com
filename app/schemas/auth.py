from typing import Self

from pydantic import BaseModel, Field,  model_validator

from app.utils.security import get_password_hash


class RegisterForm(BaseModel):
    firstname: str = Field(..., min_length=1, max_length=255, examples=['name'])
    lastname: str = Field(..., min_length=1, max_length=255, examples=['surname'])
    phone_number: str = Field(..., title='1', min_length=9, examples=['998901112233'])
    password: str = Field(..., min_length=1, examples=['1'])
    confirm_password: str = Field(..., min_length=1, examples=['1'])

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')

        self.password = get_password_hash(self.password)
        return self


class VerifyCodeForm(BaseModel):
    code: int = Field(..., examples=[123456])
    phone_number: str = Field(..., title='1', min_length=9, examples=['998901112233'])


class LoginForm(BaseModel):
    phone_number: str = Field(..., title='1', min_length=9, examples=['998901112233'])
    password: str = Field(..., min_length=1, examples=['1'])
