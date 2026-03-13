from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.models.user import User
from app.schemas import ResponseSchema
from app.schemas.users import UpdateProfile
from app.utils.security import get_current_user

user_router = APIRouter(prefix='/user', tags=['Users'])


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
        data=updated_user
    )
