from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app.models.categories import Category
from app.schemas import CreateCategory, ReadCategory, UpdateCategory, ResponseSchema

category_router = APIRouter()


@category_router.get('/category')
async def get_categories():
    categories = await Category.get_all()
    return ResponseSchema[list[ReadCategory]](
        message='all categories',
        data=categories
    )


@category_router.get('/category/{id}')
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


@category_router.patch('/category/{id}')
async def up_category(id: int, data: UpdateCategory):
    update_category = await Category.update(id, **data.model_dump(exclude_unset=True))
    return ResponseSchema[UpdateCategory](
        message='Category updated',
        data=update_category
    )


@category_router.delete('/category/{id}')
async def del_category(id: int):
    await Category.delete(id)
    return ResponseSchema(
        message=f"Category {id} deleted"
    )


@category_router.post('/category')
async def cr_category(data: CreateCategory):
    category = await Category.create(**data.model_dump())
    return ResponseSchema[ReadCategory](
        message=f'Category {category.id} created',
        data=category
    )
