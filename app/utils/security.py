from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPBearer
from jose import exceptions, jwt
from passlib.context import CryptContext
from starlette import status

from app.config.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

http_bearer = HTTPBearer()


def _create_token(data: dict, token_type: str, expires_delta: timedelta):
    to_encode = data.copy()
    now = datetime.now(UTC)
    expire = now + expires_delta
    to_encode.update({"exp": expire, "iat": now, "type": token_type, "jti": str(uuid4())})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    return _create_token(
        data,
        "access",
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_TIME),
    )


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    return _create_token(
        data,
        "refresh",
        expires_delta or timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_TIME),
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_current_user(token: Annotated[str, Depends(http_bearer)]):
    from app.models.user import User

    token = token.credentials
    try:
        encoded_jwt = decode_token(token)
    except exceptions.JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if encoded_jwt.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = encoded_jwt.get('sub')

    if user_id and (user := await User.get(user_id)):
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


async def get_current_admin(user=Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
