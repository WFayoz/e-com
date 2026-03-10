from fastapi import APIRouter
from starlette import status
from starlette.responses import JSONResponse

from app.models.category import Category
from app.models.product import Product
from app.schemas import ResponseSchema, ReadProduct, UpdateProduct, CreateProduct

product_router = APIRouter(prefix='/product', tags=['product'])


@product_router.get('')
async def get_products():
    products = await Product.get_all()
    return ResponseSchema[list[ReadProduct]](
        message='all categories',
        data=products
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
        message='Category detail',
        data=product
    )


@product_router.patch('/{id}')
async def up_product(id: int, data: UpdateProduct):
    update_product = await Product.update(id, **data.model_dump(exclude_unset=True))
    return ResponseSchema[UpdateProduct](
        message='Product updated',
        data=update_product
    )


@product_router.delete('/{id}')
async def del_product(id: int):
    await Product.delete(id)
    return ResponseSchema(
        message=f"Product {id} deleted"
    )


@product_router.post('')
async def cr_product(data: CreateProduct):
    product = await Product.create(**data.model_dump())
    return ResponseSchema[ReadProduct](
        message=f'Product {product.id} created',
        data=product
    )


@product_router.post('/search')
async def get_products(search_query: str = None):
    products = await Product.get_all()
    # Filter products based on search_query if provided
    if search_query:
        products = [product for product in products if search_query.lower() in product.lower()]
        return {"products": products}

    return {"no products found"}
