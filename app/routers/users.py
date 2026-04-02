from argon2 import hash_password
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse

from app.models.user import User
from app.schemas import ResponseSchema
from app.schemas.users import UpdateProfile, ChangePassword, UserOut
from app.utils.security import get_current_user, verify_password

user_router = APIRouter(prefix='/users', tags=['Users'])


@user_router.get('/profile')
async def get_me_view(current_user: User = Depends(get_current_user)):
    return current_user


@user_router.patch('/profile')
async def update_profile(data: UpdateProfile, current_user: User = Depends(get_current_user)):
    updated_user = await User.update(
        current_user.id,
        **data.model_dump(exclude_unset=True)
    )
    return ResponseSchema(
        message="Profile updated",
        data=UserOut.model_validate(updated_user)
    )


@user_router.put('/password')
async def change_password(
        data: ChangePassword,
        current_user: User = Depends(get_current_user)
):
    if not current_user.check_password(data.old_password):
        raise HTTPException(status_code=400, detail='Old password is incorrect')

    await User.update(
        current_user.id,
        password=User.get_password_hash(data.new_password)
    )

    return ResponseSchema(
        message='Password updated'
    )
