from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from starlette import status
from starlette.responses import JSONResponse

from app.config.config import settings
from app.models.user import User
from app.schemas.auth import (
    LoginForm,
    PasswordResetConfirmForm,
    PasswordResetRequestForm,
    RefreshTokenForm,
    RegisterForm,
    TokenPair,
    VerifyCodeForm,
)
from app.services.otp_services import OtpService
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.utils.utils import generate_code

auth_router = APIRouter(prefix='/auth', tags=['auth'])


# def otp_service():
#     return OtpService()


@auth_router.post('/register')
async def login_view(data: RegisterForm, service: OtpService = Depends(OtpService)):
    user = await User.get_by_phone(data.phone_number)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='phone number is already registered',
        )
    user_data = data.model_dump(exclude={"confirm_password"})
    service.save_user_before_registration(data.phone_number, user_data)

    code = generate_code()
    is_sent, _time = service.send_otp_by_phone(data.phone_number, code, "registration")
    if not is_sent:
        return {'message': f'Smsni {_time} dan keyin yubora olasiz'}
    return {'message': 'Sms yuborildi'}


@auth_router.post('/verification-phone')
async def login_phone_view(data: VerifyCodeForm, service: OtpService = Depends(OtpService)):
    is_valid, message = service.verify_otp_by_phone(data.phone_number, data.code, "registration")
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    user_data = service.get_user_before_registration(data.phone_number)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User data expired. Please register again.",
        )

    await User.create(**user_data)
    service.delete_user_before_registration(data.phone_number)

    return {"success": True, "message": "User registered successfully"}


def build_token_pair(user: User, service: OtpService) -> TokenPair:
    access_token = create_access_token({'sub': str(user.id)})
    refresh_token = create_refresh_token({'sub': str(user.id)})
    payload = decode_token(refresh_token)
    service.store_refresh_token(
        str(user.id),
        payload["jti"],
        settings.JWT_REFRESH_TOKEN_EXPIRE_TIME * 60,
    )
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@auth_router.post('/login')
async def login_view(data: LoginForm, service: OtpService = Depends(OtpService)):
    user = await User.get_by_phone(data.phone_number)
    if user is None:
        return JSONResponse(
            {'message': 'invalid phone or password'},
            status.HTTP_404_NOT_FOUND
        )

    is_valid_password = verify_password(data.password, user.password)
    if not is_valid_password:
        return JSONResponse(
            {'message': '2 invalid phone or password'},
            status.HTTP_400_BAD_REQUEST
        )
    tokens = build_token_pair(user, service)
    return tokens.model_dump()


@auth_router.post('/refresh')
async def refresh_tokens(data: RefreshTokenForm, service: OtpService = Depends(OtpService)):
    try:
        payload = decode_token(data.refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = payload.get("sub")
    jti = payload.get("jti")
    if not user_id or not jti or not service.is_refresh_token_active(user_id, jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid")

    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    service.revoke_refresh_token(user_id, jti)
    tokens = build_token_pair(user, service)
    return tokens.model_dump()


@auth_router.post('/logout')
async def logout_view(data: RefreshTokenForm, service: OtpService = Depends(OtpService)):
    try:
        payload = decode_token(data.refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = payload.get("sub")
    jti = payload.get("jti")
    if user_id and jti:
        service.revoke_refresh_token(user_id, jti)
    return {"message": "Logged out successfully"}


@auth_router.post('/password-reset/request')
async def password_reset_request(
        data: PasswordResetRequestForm,
        service: OtpService = Depends(OtpService),
):
    user = await User.get_by_phone(data.phone_number)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    service.save_password_reset_request(data.phone_number, {"user_id": str(user.id)})
    code = generate_code()
    is_sent, ttl = service.send_otp_by_phone(data.phone_number, code, "password-reset")
    if not is_sent:
        return {"message": f'Smsni {ttl} dan keyin yubora olasiz'}
    return {"message": "Password reset OTP sent"}


@auth_router.post('/password-reset/confirm')
async def password_reset_confirm(
        data: PasswordResetConfirmForm,
        service: OtpService = Depends(OtpService),
):
    is_valid, message = service.verify_otp_by_phone(data.phone_number, data.code, "password-reset")
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    reset_data = service.get_password_reset_request(data.phone_number)
    if not reset_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset request expired")

    user = await User.get(reset_data["user_id"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await User.update(user.id, password=get_password_hash(data.password))
    service.delete_password_reset_request(data.phone_number)
    return {"message": "Password reset successfully"}

