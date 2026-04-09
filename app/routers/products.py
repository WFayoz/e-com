from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from starlette import status
from starlette.responses import JSONResponse

from app.models.base_model import db
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.schemas import (
    CreateProduct,
    ProductListResponse,
    ReadProduct,
    ResponseSchema,
    UpdateProduct,
)
from app.schemas.products import ProductPagination
from app.utils.security import get_current_admin

product_router = APIRouter(prefix='/product', tags=['product'])


@product_router.get('')
async def get_products(
    search: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
):
    query = select(Product)
    count_query = select(func.count()).select_from(Product)

    if search:
        search_term = f"%{search.strip()}%"
        condition = or_(
            Product.name.ilike(search_term),
            Product.description.ilike(search_term),
        )
        query = query.where(condition)
        count_query = count_query.where(condition)

    if category_id is not None:
        query = query.where(Product.category_id == category_id)
        count_query = count_query.where(Product.category_id == category_id)

    if min_price is not None:
        query = query.where(Product.price >= min_price)
        count_query = count_query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)
        count_query = count_query.where(Product.price <= max_price)

    total = (await db.execute(count_query)).scalar() or 0
    products = (
        await db.execute(
            query.order_by(Product.id.desc()).offset((page - 1) * size).limit(size)
        )
    ).scalars().all()

    return ResponseSchema[ProductListResponse](
        message='Products fetched',
        data=ProductListResponse(
            items=[ReadProduct.model_validate(product) for product in products],
            pagination=ProductPagination(page=page, size=size, total=total),
        ),
    )


@product_router.get('/{id}')
async def get_product(id: int):
    product = await Product.get(id)
    if product is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'product not found', 'data': None}
        )
    return ResponseSchema[ReadProduct](
        message='Product detail',
        data=product
    )


@product_router.patch('/{id}')
async def up_product(id: int, data: UpdateProduct, current_user: User = Depends(get_current_admin)):
    if data.category_id is not None:
        category = await Category.get(data.category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

    update_product = await Product.update(id, **data.model_dump(exclude_unset=True))
    if update_product is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'product not found', 'data': None}
        )
    return ResponseSchema[UpdateProduct](
        message='Product updated',
        data=update_product
    )


@product_router.delete('/{id}')
async def del_product(id: int, current_user: User = Depends(get_current_admin)):
    await Product.delete(id)
    return ResponseSchema(
        message=f"Product {id} deleted"
    )


@product_router.post('')
async def cr_product(data: CreateProduct, current_user: User = Depends(get_current_admin)):
    category = await Category.get(data.category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    product = await Product.create(**data.model_dump())
    return ResponseSchema[ReadProduct](
        message=f'Product {product.id} created',
        data=product
    )
