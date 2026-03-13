from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from starlette.responses import JSONResponse

from app.models.user import User
from app.schemas.auth import VerifyCodeForm, RegisterForm, LoginForm
from app.services.otp_services import OtpService
from app.utils.security import get_password_hash, verify_password, create_access_token, get_current_user
from app.utils.utils import generate_code

auth_router = APIRouter(prefix='/auth', tags=['auth'])


# def otp_service():
#     return OtpService()


@auth_router.post('/register')
async def login_view(data: RegisterForm, service: OtpService = Depends(OtpService)):
    user = await User.get_by_phone(data.phone_number)
    if user is not None:
        return ORJSONResponse(
            {'message': 'phone number is already registered'},
            status.HTTP_400_BAD_REQUEST
        )
    user_data = data.model_dump(exclude={"confirm_password"})

    service.save_user_before_registration(data.phone_number, user_data)

    code = generate_code()
    is_sent, _time = service.send_otp_by_phone(data.phone_number, code)
    if not is_sent:
        return ORJSONResponse(
            {'message': f'Smsni {_time} dan keyin yubora olasiz'}
        )
    return ORJSONResponse(
        {'message': 'Sms yuborildi'}
    )


@auth_router.post('/verification-phone')
async def login_phone_view(data: VerifyCodeForm, service: OtpService = Depends(OtpService)):
    # 1. Verify OTP
    is_valid = service.verify_otp_by_phone(data.phone_number, data.code)
    if not is_valid:
        return ORJSONResponse(
            {"success": False, "message": "Invalid or expired OTP"},
            status.HTTP_400_BAD_REQUEST
        )

    # 2. Get user data from Redis
    user_data = service.get_user_before_registration(data.phone_number)
    if not user_data:
        return ORJSONResponse(
            {"success": False, "message": "User data expired. Please register again."},
            status.HTTP_400_BAD_REQUEST
        )

    # 3. Save user in DB
    user = await User.create(**user_data)

    # 4. (Optional) cleanup Redis so the same OTP/user_data can’t be reused
    service.delete_user_before_registration(data.phone_number)

    return ORJSONResponse(
        {"success": True, "message": "User registered successfully"}
    )


@auth_router.post('/login')
async def login_view(data: LoginForm):
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
    token = create_access_token({'sub': str(user.id)})
    return JSONResponse(
        {'access_token': token}
    )
