from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from app.models.category import Category
from app.models.user import User
from app.schemas import CreateCategory, ReadCategory, UpdateCategory, ResponseSchema
from app.utils.security import get_current_user, get_current_admin

category_router = APIRouter(prefix='/category', tags=['category'])


@category_router.get('')
async def get_categories():
    categories = await Category.get_all()
    return ResponseSchema[list[ReadCategory]](
        message='all categories',
        data=categories
    )


@category_router.get('/{id}')
async def get_category(id: int):
    category = await Category.get(id)
    if category is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'category not found', 'data': None}
        )
    return ResponseSchema[ReadCategory](
        message='Category detail',
        data=category
    )


@category_router.patch('/{id}')
async def up_category(id: int, data: UpdateCategory, current_user: User = Depends(get_current_admin)):
    update_category = await Category.update(id, **data.model_dump(exclude_unset=True))
    return ResponseSchema[UpdateCategory](
        message='Category updated',
        data=update_category
    )


@category_router.delete('/{id}')
async def del_category(id: int, current_user: User = Depends(get_current_admin)):
    await Category.delete(id)
    return ResponseSchema(
        message=f"Category {id} deleted"
    )


@category_router.post('')
async def cr_category(data: CreateCategory, current_user: User = Depends(get_current_admin)):
    category = await Category.create(**data.model_dump())
    return ResponseSchema[ReadCategory](
        message=f'Category {category.id} created',
        data=category
    )
